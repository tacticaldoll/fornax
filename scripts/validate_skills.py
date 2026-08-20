#!/usr/bin/env python3
"""Validate portable skill folders.

Run from the repository root. `--skills-path` defaults to `skills` relative to
the working directory, and the distribution and host-manifest checks read the
working directory as the repository root — unlike skill_graph.py, which
anchors itself to its own location.

Usage:
    .venv/bin/python scripts/validate_skills.py
    .venv/bin/python scripts/validate_skills.py --skills-path templates \
        --allow-template-placeholders
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from diagnostic_text import printable
from distribution_manifest import validate_distribution

# Re-exported so scripts/tests/fixtures.py keeps reaching it here while code moves.
from distribution_manifest import HOST_VERSION_MANIFESTS  # noqa: F401
from host_paths import has_parent_segment_anywhere, is_absolute_anywhere
from markdown_links import iter_markdown_links, local_target
from path_boundary import Boundary, Verdict, resolve_within
from skill_interface import INTERFACE_FILE, InterfaceError, load as load_interface
from skill_model import FAMILIES, HANDOFF, NAME_PATTERN, STATUSES, listed
from skill_yaml import (
    Shape,
    declares_key,
    declares_value,
    get_top_level_yaml_value,
    get_yaml_list,
    get_yaml_mapping_value,
)


FRONTMATTER_PATTERN = re.compile(r"^---\s*\r?\n(.*?)\r?\n---", re.DOTALL)
INPUT_LINE_PATTERN = re.compile(r"^\*\*Input\*\*[^\S\n]*:[^\S\n]*([^\n]+)$", re.MULTILINE)
RECORD_INPUT_PATTERN = re.compile(
    r"`(?P<producer>[a-z0-9]+(?:-[a-z0-9]+)*)`\s+"
    r"(?P<label>[A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*)*\s+Record)\b"
)
REQUIRED_MANIFEST_FIELDS = ("name", "family", "description", "triggers", "entrypoint")
# Required fields whose value is the block beneath them rather than same-line text.
BLOCK_MANIFEST_FIELDS = ("triggers",)


def fail(skill_name: str, message: str) -> None:
    print(printable(f"FAIL {skill_name} - {message}"))


def read_skill_text(path: Path, name: str, boundary: Boundary) -> str | None:
    """Read one skill-owned text file or emit the validator's normal diagnostic.

    An absent path falls through to the read, which reports it as unreadable. The
    boundary owner states absence as a fact; whether it is an error is this
    caller's decision, and here every path came from a directory listing.
    """
    relative_path = boundary.relative(path)
    found = resolve_within(path, boundary)
    if found.verdict is Verdict.UNRESOLVABLE:
        fail(name, f"{relative_path} could not be resolved: {found.error}")
        return None
    if found.verdict is Verdict.OUTSIDE:
        fail(name, f"{relative_path} leaves skill directory")
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeError:
        fail(name, f"{relative_path} must use UTF-8")
    except OSError as error:
        fail(name, f"{relative_path} could not be read: {error}")
    return None


def read_markdown_files(name: str, boundary: Boundary) -> tuple[dict[Path, str], bool]:
    """Read every Markdown file once so sibling checks share the same failure boundary."""
    contents = {}
    failed = False
    for markdown_file in sorted(boundary.declared.rglob("*.md")):
        content = read_skill_text(markdown_file, name, boundary)
        if content is None:
            failed = True
        else:
            contents[markdown_file] = content
    return contents, failed


def validate_markdown_links(
    name: str, markdown_files: dict[Path, str], boundary: Boundary
) -> bool:
    failed = False

    for markdown_file, content in markdown_files.items():
        relative_path = boundary.relative(markdown_file)

        for link in iter_markdown_links(content):
            link_target = local_target(link.destination)

            if link_target is None:
                continue

            if is_absolute_anywhere(link_target):
                fail(name, f"{relative_path} has absolute link: {link.shown_target}")
                failed = True
                continue

            found = resolve_within(markdown_file.parent / link_target, boundary)
            if found.verdict is Verdict.UNRESOLVABLE:
                fail(
                    name,
                    f"{relative_path} link could not be resolved: "
                    f"{link.shown_target} ({found.error})",
                )
                failed = True
            elif found.verdict is Verdict.OUTSIDE:
                fail(
                    name,
                    f"{relative_path} link leaves skill directory: {link.shown_target}",
                )
                failed = True
            elif found.verdict is Verdict.ABSENT:
                fail(name, f"{relative_path} link not found: {link.shown_target}")
                failed = True

    return failed


def validate_handoffs(
    skill_dir: Path,
    name: str,
    known_skills: set[str],
    markdown_files: dict[Path, str],
) -> bool:
    failed = False

    for markdown_file, content in markdown_files.items():
        for target_skill in HANDOFF.findall(content):
            if target_skill not in known_skills:
                fail(
                    name,
                    f"{markdown_file.relative_to(skill_dir)} handoff target not found: "
                    f"{target_skill}",
                )
                failed = True

    return failed


def record_type(label: str) -> str:
    """Turn a standardized title-cased Input label into its sidecar record type."""
    return "-".join(part.lower() for part in label.split())


def validate_record_inputs(skill_dir: Path, name: str, content: str) -> bool:
    """Require explicit producer-record Input claims to have matching sidecars.

    This is deliberately a narrow consistency check, not seam discovery. Only a
    standardized ``a `producer` Record Name``-style claim on the Input line opts in;
    matching sidecars remain the authoritative seam inventory.
    """
    input_match = INPUT_LINE_PATTERN.search(content)
    if not input_match:
        return False
    claims = list(RECORD_INPUT_PATTERN.finditer(input_match.group(1)))
    if not claims:
        return False

    consumer_path = skill_dir / INTERFACE_FILE
    if not consumer_path.exists():
        fail(name, f"Input names a produced record but the consumer has no {INTERFACE_FILE}")
        return True
    try:
        consumer = load_interface(consumer_path, name)
    except InterfaceError:
        return False  # ordinary sidecar validation reports the malformed file

    failed = False
    for match in claims:
        producer_name = match.group("producer")
        expected_type = record_type(match.group("label"))
        producer_dir = skill_dir.parent / producer_name
        producer_path = producer_dir / INTERFACE_FILE
        if not producer_path.exists():
            if producer_dir.is_dir():
                fail(
                    name,
                    f"Input names local producer `{producer_name}` {match.group('label')} but it "
                    f"has no {INTERFACE_FILE}",
                )
                failed = True
                continue
            foreign = [
                record
                for record in consumer.consumes
                if record.record_type == expected_type
                and record.publisher != consumer.publisher
            ]
            if not foreign:
                fail(
                    name,
                    f"Input names `{producer_name}` {match.group('label')} but no local skill "
                    f"named `{producer_name}` exists and the consumer declares no matching "
                    "foreign identity; correct the producer name or declare the external record "
                    "identity",
                )
                failed = True
            continue
        try:
            producer = load_interface(producer_path, producer_name)
        except InterfaceError:
            continue  # the producer's ordinary sidecar validation reports the malformed file

        records = [record for record in producer.produces if record.record_type == expected_type]
        if not records:
            fail(
                name,
                f"Input names `{producer_name}` {match.group('label')} but its {INTERFACE_FILE} "
                f"produces no {expected_type} record",
            )
            failed = True
            continue
        if not set(records) & set(consumer.consumes):
            fail(
                name,
                f"Input names `{producer_name}` {match.group('label')} but {INTERFACE_FILE} "
                "does not consume any exact identity produced for that record type",
            )
            failed = True

    return failed


def portable_path_error(value: str) -> str | None:
    """Why a manifest path is not portable, judged without touching the filesystem.

    Containment cannot cover this. An absolute path that happens to resolve inside
    the skill folder passes containment and still breaks the moment the folder is
    copied to a host, and a manifest can be judged by an installer before the
    target it names exists. docs/skill-yaml-schema.md states the rule; this
    enforces it.
    """
    if is_absolute_anywhere(value):
        return "must use a relative path"
    if has_parent_segment_anywhere(value):
        return 'must not use ".." segments'
    return None


def validate_manifest_path(
    label: str, value: str, name: str, boundary: Boundary, *, expect_directory: bool
) -> bool:
    """Hold one declared manifest path to portability, containment, and its kind.

    The entrypoint and the three resource keys differ in what they are called and in
    what they must name, so they share the sequence rather than restating it. The
    syntactic rule runs first: it needs no filesystem, and an absolute path that
    happens to resolve inside the folder would otherwise pass containment and still
    break on copy.

    The kind check is here rather than in path_boundary because the owner states no
    file-type policy — what counts as the right kind is exactly what differs between
    callers. docs/skill-yaml-schema.md says the entrypoint names the primary
    instruction file and the resource keys name bundled directories, and existence
    alone let a directory pass as an entrypoint and a file pass as a resource root.
    """
    portability = portable_path_error(value)
    if portability:
        fail(name, f"{label} {portability}: {value}")
        return True

    target = boundary.declared / value
    found = resolve_within(target, boundary)
    if found.verdict is Verdict.UNRESOLVABLE:
        fail(name, f"{label} could not be resolved: {value} ({found.error})")
        return True
    if found.verdict is Verdict.OUTSIDE:
        fail(name, f"{label} leaves the skill folder: {value}")
        return True
    if found.verdict is Verdict.ABSENT:
        fail(name, f"{label} not found: {value}")
        return True

    if expect_directory and not target.is_dir():
        fail(name, f"{label} must name a directory: {value}")
        return True
    if not expect_directory and not target.is_file():
        fail(name, f"{label} must name a file: {value}")
        return True

    return False


def validate_skill_manifest(
    name: str,
    manifest: str,
    allow_template_placeholders: bool,
    boundary: Boundary,
) -> tuple[bool, str | None, str | None]:
    """Validate one skill manifest and return values shared with SKILL.md checks."""
    failed = False

    for field in REQUIRED_MANIFEST_FIELDS:
        if field in BLOCK_MANIFEST_FIELDS:
            if not declares_key(manifest, field):
                fail(name, f"skill.yaml missing {field}")
                failed = True
            else:
                # Present is not enough: a scalar, an empty block, a flow list, a
                # nested mapping and a list of empty items all declare the key. The
                # read must be a block list, and one item must carry text.
                read = get_yaml_list(manifest, field)
                if read.shape is not Shape.READ or not any(read.items):
                    fail(name, f"skill.yaml {field} must be a non-empty list of strings")
                    failed = True
        elif not declares_value(manifest, field):
            fail(name, f"skill.yaml missing {field}")
            failed = True

    if declares_key(manifest, "version"):
        fail(
            name,
            "skill.yaml must not set version; release versioning is the collection's "
            "(distribution.json)",
        )
        failed = True

    manifest_name = get_top_level_yaml_value(manifest, "name")
    manifest_status = get_top_level_yaml_value(manifest, "status")
    entrypoint = get_top_level_yaml_value(manifest, "entrypoint")

    if manifest_name and manifest_name != name and not allow_template_placeholders:
        fail(name, f"skill.yaml name '{manifest_name}' must match folder name")
        failed = True

    if manifest_status and manifest_status not in STATUSES:
        fail(name, f"skill.yaml status must be {listed(STATUSES)}")
        failed = True

    manifest_family = get_top_level_yaml_value(manifest, "family")

    if manifest_family and manifest_family not in FAMILIES:
        fail(name, f"skill.yaml family must be {listed(FAMILIES)}")
        failed = True

    if entrypoint and validate_manifest_path(
        "skill.yaml entrypoint", entrypoint, name, boundary, expect_directory=False
    ):
        failed = True

    for resource_key in ("scripts", "references", "assets"):
        resource_path = get_yaml_mapping_value(manifest, "resources", resource_key)

        if resource_path and validate_manifest_path(
            f"resources.{resource_key}", resource_path, name, boundary, expect_directory=True
        ):
            failed = True

    return failed, manifest_name, get_top_level_yaml_value(manifest, "description")


def validate_skill_document(
    name: str,
    content: str,
    frontmatter: str,
    manifest_name: str | None,
    manifest_description: str | None,
    allow_template_placeholders: bool,
) -> bool:
    """Validate SKILL.md metadata and its required Input contract."""
    failed = False
    frontmatter_name = get_top_level_yaml_value(frontmatter, "name")

    if not declares_value(frontmatter, "name"):
        fail(name, "frontmatter missing name")
        failed = True

    if frontmatter_name and frontmatter_name != name and not allow_template_placeholders:
        fail(name, f"SKILL.md frontmatter name '{frontmatter_name}' must match folder name")
        failed = True

    if manifest_name and frontmatter_name and manifest_name != frontmatter_name:
        fail(name, "skill.yaml name and SKILL.md frontmatter name must match")
        failed = True

    if not declares_value(frontmatter, "description"):
        fail(name, "frontmatter missing description")
        failed = True

    frontmatter_description = get_top_level_yaml_value(frontmatter, "description")

    if (
        manifest_description
        and frontmatter_description
        and manifest_description != frontmatter_description
    ):
        fail(name, "skill.yaml and SKILL.md frontmatter description must match")
        failed = True

    if manifest_description and not manifest_description.startswith("Use when "):
        fail(name, "skill.yaml description must start with 'Use when '")
        failed = True

    if not declares_key(content, "**Input**"):
        fail(name, "SKILL.md must state an **Input**: contract line")
        failed = True

    return failed


def validate_skill(skill_dir: Path, allow_template_placeholders: bool) -> bool:
    name = skill_dir.name
    manifest_file = skill_dir / "skill.yaml"
    skill_file = skill_dir / "SKILL.md"
    skill_failed = False

    if not NAME_PATTERN.fullmatch(name):
        fail(name, "folder name must use lowercase letters, digits, and hyphens")
        return False

    if not skill_file.exists():
        fail(name, "missing SKILL.md")
        return False

    if not manifest_file.exists():
        fail(name, "missing skill.yaml")
        return False

    boundary = Boundary.at(skill_dir)

    manifest = read_skill_text(manifest_file, name, boundary)
    if manifest is None:
        return False

    manifest_failed, manifest_name, manifest_description = validate_skill_manifest(
        name, manifest, allow_template_placeholders, boundary
    )
    if manifest_failed:
        skill_failed = True

    content = read_skill_text(skill_file, name, boundary)
    if content is None:
        return False
    frontmatter_match = FRONTMATTER_PATTERN.search(content)

    if not frontmatter_match:
        fail(name, "SKILL.md must start with YAML frontmatter")
        return False

    frontmatter = frontmatter_match.group(1)
    if validate_skill_document(
        name,
        content,
        frontmatter,
        manifest_name,
        manifest_description,
        allow_template_placeholders,
    ):
        skill_failed = True

    if validate_record_inputs(skill_dir, name, content):
        skill_failed = True

    interface_file = skill_dir / INTERFACE_FILE
    if interface_file.exists():
        try:
            load_interface(interface_file, name)
        except InterfaceError as error:
            fail(name, f"{INTERFACE_FILE} - {error}")
            skill_failed = True

    if not allow_template_placeholders:
        known_skills = {path.name for path in skill_dir.parent.iterdir() if path.is_dir()}
        markdown_files, markdown_failed = read_markdown_files(name, boundary)
        if markdown_failed:
            skill_failed = True

        if validate_markdown_links(name, markdown_files, boundary):
            skill_failed = True

        if validate_handoffs(skill_dir, name, known_skills, markdown_files):
            skill_failed = True

    if not skill_failed:
        print(printable(f"OK   {name}"))

    return not skill_failed


def validate_interface_publishers(skills_path: Path, publisher_id: str) -> bool:
    """Require this collection's sidecars to share its canonical publisher identity."""
    failed = False
    for sidecar in sorted(skills_path.glob(f"*/{INTERFACE_FILE}")):
        try:
            interface = load_interface(sidecar)
        except InterfaceError:
            continue  # validate_skill reports invalid declarations with the skill context
        if interface.publisher != publisher_id:
            fail(sidecar.parent.name, f"{INTERFACE_FILE} publisher must match distribution.json")
            failed = True
    return not failed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate portable skill folders.")
    parser.add_argument(
        "--skills-path", default="skills", help="Directory containing skill folders."
    )
    parser.add_argument(
        "--allow-template-placeholders",
        action="store_true",
        help="Allow template placeholder names that do not match the folder name.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skills_path = Path(args.skills_path)

    if not skills_path.exists():
        print(printable(f"Skills directory not found: {skills_path}"), file=sys.stderr)
        return 1

    distribution = validate_distribution(Path.cwd())
    failed = not distribution.passed

    for skill_dir in sorted(path for path in skills_path.iterdir() if path.is_dir()):
        if not validate_skill(skill_dir, args.allow_template_placeholders):
            failed = True

    if distribution.publisher_id is not None and not validate_interface_publishers(
        skills_path, distribution.publisher_id
    ):
        failed = True

    if failed:
        return 1

    print("Skill validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
