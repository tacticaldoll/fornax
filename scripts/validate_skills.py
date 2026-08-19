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
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from markdown_links import iter_markdown_links, local_target
from path_boundary import Boundary, Verdict, resolve_within
from skill_interface import INTERFACE_FILE, InterfaceError, load as load_interface
from skill_model import FAMILIES, HANDOFF, STATUSES, listed


NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
FRONTMATTER_PATTERN = re.compile(r"^---\s*\r?\n(.*?)\r?\n---", re.DOTALL)
INPUT_LINE_PATTERN = re.compile(r"^\*\*Input\*\*\s*:\s*(.+)$", re.MULTILINE)
RECORD_INPUT_PATTERN = re.compile(
    r"`(?P<producer>[a-z0-9]+(?:-[a-z0-9]+)*)`\s+"
    r"(?P<label>[A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*)*\s+Record)\b"
)
REQUIRED_MANIFEST_FIELDS = ("name", "family", "description", "triggers", "entrypoint")
HOST_VERSION_MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
)


HOST_DESCRIPTION_MANIFESTS = HOST_VERSION_MANIFESTS + (".claude-plugin/marketplace.json",)


@dataclass(frozen=True)
class DistributionValidation:
    passed: bool
    publisher_id: str | None


def read_json_object(path: Path) -> tuple[dict | None, str | None]:
    """Read one UTF-8 JSON object and return a diagnostic instead of raising."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeError:
        return None, "must use UTF-8"
    except (OSError, json.JSONDecodeError) as error:
        return None, str(error)
    if not isinstance(value, dict):
        return None, "must contain a JSON object"
    return value, None


def described_paths(manifest: dict) -> list[tuple[str, str]]:
    """Every description a host manifest carries, labelled by where it sits."""
    found = []

    if isinstance(manifest.get("description"), str):
        found.append(("description", manifest["description"]))

    for index, plugin in enumerate(manifest.get("plugins", [])):
        if isinstance(plugin, dict) and isinstance(plugin.get("description"), str):
            found.append((f"plugins[{index}].description", plugin["description"]))

    return found


def validate_projected_descriptions(root: Path, canonical: object) -> bool:
    """Require each host description to open with the canonical one.

    A prefix rather than an equality: a host may append to the canonical sentence
    — host-packaging.md calls these projections, and per-surface additions are
    legitimate — but may not replace it with a rewrite of its own.
    """
    if not isinstance(canonical, str) or not canonical:
        print("FAIL distribution.json - description must be a non-empty string")
        return True

    failed = False

    for relative_path in HOST_DESCRIPTION_MANIFESTS:
        path = root / relative_path
        manifest, error = read_json_object(path)
        if error is not None:
            if relative_path not in HOST_VERSION_MANIFESTS:
                print(f"FAIL {relative_path} - {error}")
                failed = True
            continue
        assert manifest is not None
        if not isinstance(manifest.get("plugins", []), list):
            print(f"FAIL {relative_path} - plugins must be a list")
            failed = True
            continue

        for label, description in described_paths(manifest):
            if not description.startswith(canonical):
                print(
                    f"FAIL {relative_path} - {label} must open with the description in "
                    "distribution.json"
                )
                failed = True

    return failed


def validate_distribution(root: Path) -> DistributionValidation:
    """Validate canonical distribution metadata and host projections."""
    distribution_file = root / "distribution.json"
    distribution, error = read_json_object(distribution_file)
    if error is not None:
        print(f"FAIL distribution.json - {error}")
        return DistributionValidation(False, None)
    assert distribution is not None

    failed = False
    name = distribution.get("name")
    version = distribution.get("version")
    publisher_id = distribution.get("publisher_id")
    skills_directory = distribution.get("skills_directory")
    if distribution.get("schema") != 1:
        print("FAIL distribution.json - schema must be 1")
        failed = True
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        print("FAIL distribution.json - name must use lowercase hyphen-case")
        failed = True
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        print("FAIL distribution.json - version must use semantic version format x.y.z")
        failed = True
    canonical_publisher: str | None = None
    if not isinstance(publisher_id, str):
        print("FAIL distribution.json - publisher_id must be a UUID")
        failed = True
    else:
        try:
            parsed_publisher = str(UUID(publisher_id))
        except ValueError:
            print("FAIL distribution.json - publisher_id must be a UUID")
            failed = True
        else:
            if publisher_id != parsed_publisher:
                print(
                    "FAIL distribution.json - publisher_id must use canonical lowercase UUID form"
                )
                failed = True
            else:
                canonical_publisher = parsed_publisher
    if skills_directory != "skills":
        print("FAIL distribution.json - skills_directory must be skills")
        failed = True

    for relative_path in HOST_VERSION_MANIFESTS:
        path = root / relative_path
        manifest, error = read_json_object(path)
        if error is not None:
            print(f"FAIL {relative_path} - {error}")
            failed = True
            continue
        assert manifest is not None
        if manifest.get("name") != name:
            print(f"FAIL {relative_path} - name must match distribution.json")
            failed = True
        if manifest.get("version") != version:
            print(f"FAIL {relative_path} - version must match distribution.json")
            failed = True

    if validate_projected_descriptions(root, distribution.get("description")):
        failed = True

    if not failed:
        print(f"OK   distribution {name} {version}")
    return DistributionValidation(not failed, canonical_publisher)


def get_top_level_yaml_value(content: str, key: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(key)}\s*:\s*(.+?)\s*$", re.MULTILINE)
    match = pattern.search(content)

    if not match:
        return None

    return clean_yaml_scalar(match.group(1))


def get_yaml_mapping_value(content: str, parent_key: str, child_key: str) -> str | None:
    lines = content.splitlines()
    in_parent = False

    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if not line.startswith((" ", "\t")):
            in_parent = line.split(":", 1)[0].strip() == parent_key
            continue

        if in_parent:
            stripped = line.strip()

            if ":" not in stripped:
                continue

            key, value = stripped.split(":", 1)

            if key.strip() == child_key:
                return clean_yaml_scalar(value)

    return None


def get_yaml_list(content: str, key: str) -> list[str]:
    lines = content.splitlines()
    in_key = False
    items: list[str] = []

    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if not line.startswith((" ", "\t")):
            in_key = line.split(":", 1)[0].strip() == key
            continue

        if in_key and line.lstrip().startswith("- "):
            items.append(clean_yaml_scalar(line.lstrip()[2:]))

    return items


def clean_yaml_scalar(value: str) -> str:
    return value.strip().strip("'").strip('"')


def fail(skill_name: str, message: str) -> None:
    print(f"FAIL {skill_name} - {message}")


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

            if Path(link_target).is_absolute():
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
    if Path(value).is_absolute():
        return "must use a relative path"
    if ".." in Path(value).parts:
        return 'must not use ".." segments'
    return None


def validate_manifest_path(label: str, value: str, name: str, boundary: Boundary) -> bool:
    """Hold one declared manifest path to the portability rule and the package boundary.

    The entrypoint and the three resource keys differ only in what they are called,
    so they share the sequence rather than restating it. The syntactic rule runs
    first: it needs no filesystem, and an absolute path that happens to resolve
    inside the folder would otherwise pass containment and still break on copy.
    """
    portability = portable_path_error(value)
    if portability:
        fail(name, f"{label} {portability}: {value}")
        return True

    found = resolve_within(boundary.declared / value, boundary)
    if found.verdict is Verdict.UNRESOLVABLE:
        fail(name, f"{label} could not be resolved: {value} ({found.error})")
        return True
    if found.verdict is Verdict.OUTSIDE:
        fail(name, f"{label} leaves the skill folder: {value}")
        return True
    if found.verdict is Verdict.ABSENT:
        fail(name, f"{label} not found: {value}")
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
        if not re.search(rf"^{re.escape(field)}\s*:", manifest, re.MULTILINE):
            fail(name, f"skill.yaml missing {field}")
            failed = True

    if re.search(r"^version\s*:", manifest, re.MULTILINE):
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

    if entrypoint and validate_manifest_path("skill.yaml entrypoint", entrypoint, name, boundary):
        failed = True

    for resource_key in ("scripts", "references", "assets"):
        resource_path = get_yaml_mapping_value(manifest, "resources", resource_key)

        if resource_path and validate_manifest_path(
            f"resources.{resource_key}", resource_path, name, boundary
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

    if not re.search(r"^name\s*:\s*\S+", frontmatter, re.MULTILINE):
        fail(name, "frontmatter missing name")
        failed = True

    if frontmatter_name and frontmatter_name != name and not allow_template_placeholders:
        fail(name, f"SKILL.md frontmatter name '{frontmatter_name}' must match folder name")
        failed = True

    if manifest_name and frontmatter_name and manifest_name != frontmatter_name:
        fail(name, "skill.yaml name and SKILL.md frontmatter name must match")
        failed = True

    if not re.search(r"^description\s*:\s*\S+", frontmatter, re.MULTILINE):
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

    if not re.search(r"^\*\*Input\*\*\s*:", content, re.MULTILINE):
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
        print(f"OK   {name}")

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
        print(f"Skills directory not found: {skills_path}", file=sys.stderr)
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
