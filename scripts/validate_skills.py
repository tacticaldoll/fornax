#!/usr/bin/env python3
"""Validate portable skill folders.

Run from the repository root. `--skills-path` defaults to `skills` relative to
the working directory, and the distribution and host-manifest checks read the
working directory as the repository root — unlike skill_graph.py, which
anchors itself to its own location.

Usage:
    python3 scripts/validate_skills.py
    python3 scripts/validate_skills.py --skills-path templates --allow-template-placeholders
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from skill_interface import INTERFACE_FILE, InterfaceError, load as load_interface
from skill_model import FAMILIES, HANDOFF, STATUSES, listed


NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
FRONTMATTER_PATTERN = re.compile(r"^---\s*\r?\n(.*?)\r?\n---", re.DOTALL)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REQUIRED_MANIFEST_FIELDS = ("name", "family", "description", "triggers", "entrypoint")
HOST_VERSION_MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
)


@dataclass(frozen=True)
class DistributionValidation:
    passed: bool
    publisher_id: str | None


HOST_DESCRIPTION_MANIFESTS = HOST_VERSION_MANIFESTS + (".claude-plugin/marketplace.json",)


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
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue  # the version pass already reports an unreadable manifest

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
    try:
        distribution = json.loads(distribution_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"FAIL distribution.json - {error}")
        return DistributionValidation(False, None)

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
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"FAIL {relative_path} - {error}")
            failed = True
            continue
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


def is_external_link(target: str) -> bool:
    return bool(re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE))


def normalize_markdown_link_target(target: str) -> str:
    target = target.strip()

    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]

    return target.split("#", 1)[0]


def validate_markdown_links(skill_dir: Path, name: str) -> bool:
    failed = False

    for markdown_file in sorted(skill_dir.rglob("*.md")):
        content = markdown_file.read_text(encoding="utf-8")

        for target in MARKDOWN_LINK_PATTERN.findall(content):
            link_target = normalize_markdown_link_target(target)

            if not link_target or is_external_link(link_target):
                continue

            if Path(link_target).is_absolute():
                fail(name, f"{markdown_file.relative_to(skill_dir)} has absolute link: {target}")
                failed = True
                continue

            if not (markdown_file.parent / link_target).exists():
                fail(name, f"{markdown_file.relative_to(skill_dir)} link not found: {target}")
                failed = True

    return failed


def validate_handoffs(skill_dir: Path, name: str, known_skills: set[str]) -> bool:
    failed = False

    for markdown_file in sorted(skill_dir.rglob("*.md")):
        content = markdown_file.read_text(encoding="utf-8")

        for target_skill in HANDOFF.findall(content):
            if target_skill not in known_skills:
                fail(
                    name,
                    f"{markdown_file.relative_to(skill_dir)} handoff target not found: "
                    f"{target_skill}",
                )
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

    manifest = manifest_file.read_text(encoding="utf-8")

    for field in REQUIRED_MANIFEST_FIELDS:
        if not re.search(rf"^{re.escape(field)}\s*:", manifest, re.MULTILINE):
            fail(name, f"skill.yaml missing {field}")
            skill_failed = True

    if re.search(r"^version\s*:", manifest, re.MULTILINE):
        fail(
            name,
            "skill.yaml must not set version; release versioning is the collection's "
            "(distribution.json)",
        )
        skill_failed = True

    manifest_name = get_top_level_yaml_value(manifest, "name")
    manifest_status = get_top_level_yaml_value(manifest, "status")
    entrypoint = get_top_level_yaml_value(manifest, "entrypoint")

    if manifest_name and manifest_name != name and not allow_template_placeholders:
        fail(name, f"skill.yaml name '{manifest_name}' must match folder name")
        skill_failed = True

    if manifest_status and manifest_status not in STATUSES:
        fail(name, f"skill.yaml status must be {listed(STATUSES)}")
        skill_failed = True

    manifest_family = get_top_level_yaml_value(manifest, "family")

    if manifest_family and manifest_family not in FAMILIES:
        fail(name, f"skill.yaml family must be {listed(FAMILIES)}")
        skill_failed = True

    if entrypoint and not (skill_dir / entrypoint).exists():
        fail(name, f"skill.yaml entrypoint not found: {entrypoint}")
        skill_failed = True

    for resource_key in ("scripts", "references", "assets"):
        resource_path = get_yaml_mapping_value(manifest, "resources", resource_key)

        if not resource_path:
            continue

        if Path(resource_path).is_absolute():
            fail(name, f"resources.{resource_key} must use a relative path")
            skill_failed = True
            continue

        if not (skill_dir / resource_path).exists():
            fail(name, f"resources.{resource_key} path not found: {resource_path}")
            skill_failed = True

    content = skill_file.read_text(encoding="utf-8")
    frontmatter_match = FRONTMATTER_PATTERN.search(content)

    if not frontmatter_match:
        fail(name, "SKILL.md must start with YAML frontmatter")
        return False

    frontmatter = frontmatter_match.group(1)
    frontmatter_name = get_top_level_yaml_value(frontmatter, "name")

    if not re.search(r"^name\s*:\s*\S+", frontmatter, re.MULTILINE):
        fail(name, "frontmatter missing name")
        skill_failed = True

    if frontmatter_name and frontmatter_name != name and not allow_template_placeholders:
        fail(name, f"SKILL.md frontmatter name '{frontmatter_name}' must match folder name")
        skill_failed = True

    if manifest_name and frontmatter_name and manifest_name != frontmatter_name:
        fail(name, "skill.yaml name and SKILL.md frontmatter name must match")
        skill_failed = True

    if not re.search(r"^description\s*:\s*\S+", frontmatter, re.MULTILINE):
        fail(name, "frontmatter missing description")
        skill_failed = True

    manifest_description = get_top_level_yaml_value(manifest, "description")
    frontmatter_description = get_top_level_yaml_value(frontmatter, "description")

    if (
        manifest_description
        and frontmatter_description
        and manifest_description != frontmatter_description
    ):
        fail(name, "skill.yaml and SKILL.md frontmatter description must match")
        skill_failed = True

    if manifest_description and not manifest_description.startswith("Use when "):
        fail(name, "skill.yaml description must start with 'Use when '")
        skill_failed = True

    if not re.search(r"^\*\*Input\*\*\s*:", content, re.MULTILINE):
        fail(name, "SKILL.md must state an **Input**: contract line")
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

        if validate_markdown_links(skill_dir, name):
            skill_failed = True

        if validate_handoffs(skill_dir, name, known_skills):
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
