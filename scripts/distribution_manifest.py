#!/usr/bin/env python3
"""Validate the collection's own metadata and the host manifests that project it.

distribution.json carries the canonical name, publisher UUID and release version; the
per-host manifests are projections of it, so what this checks is agreement rather than
each file on its own. That is a different subject from whether a skill folder is
well formed, and it shares no helper with it — notably it reports through print
directly and never through the skill validator's fail(), which is what let it move out
whole.

Standard library only.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from diagnostic_text import printable
from skill_model import NAME_PATTERN
from workspace_files import workspace_files


VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

HOST_VERSION_MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
)


HOST_DESCRIPTION_MANIFESTS = HOST_VERSION_MANIFESTS + (".claude-plugin/marketplace.json",)


# Presence only. Which files must carry a pin cannot be derived — an unpinned ref is
# a documented form — so this list answers the one direction the scan cannot.
PINNED_INSTALL_DOCS = (
    ".opencode/INSTALL.md",
    "README.md",
    "tools/fornax-cli/README.md",
)


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


def validate_projected_descriptions(root: Path, canonical: str) -> bool:
    """Require each host description to open with the canonical one.

    A prefix rather than an equality: a host may append to the canonical sentence
    — host-packaging.md calls these projections, and per-surface additions are
    legitimate — but may not replace it with a rewrite of its own.

    The canonical value arrives already validated. Judging it here made the one
    function scoped to projections the only place a distribution.json field defect
    was reported, so a caller reading `FAIL distribution.json` was looking at the
    projection loop for a rule that belongs beside name, version and publisher_id.
    """
    failed = False

    for relative_path in HOST_DESCRIPTION_MANIFESTS:
        path = root / relative_path
        manifest, error = read_json_object(path)
        if error is not None:
            if relative_path not in HOST_VERSION_MANIFESTS:
                print(printable(f"FAIL {relative_path} - {error}"))
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


def install_pin_pattern(repository: str) -> re.Pattern[str]:
    """Match a documented install ref that already names a release tag."""
    return re.compile(re.escape(repository) + r"\.git[@#]v(\d+\.\d+\.\d+)")


def validate_install_pins(root: Path, repository: str, version: str) -> bool:
    """Require every documented install pin to name the release being shipped.

    The host manifests are checked above, but the commands a reader copies live
    in Markdown, and nothing compared those to distribution.json: a release that
    bumped every manifest and missed one pin shipped an install command that
    resolves to the previous tag, with every workspace check still green.

    The docs to read are derived from the workspace rather than listed here, so
    a pin added to a file nobody thought to register is judged like the rest. An
    unpinned ref is left alone: tracking the default branch is a documented form,
    not a stale pin, and only a ref already carrying a version is a claim about
    which release to install.

    Derivation and a declared set guard opposite directions, so both are here. The
    scan catches a stale pin in a file nobody registered, which a list cannot see.
    PINNED_INSTALL_DOCS catches a registered file that stops carrying a pin, which
    the scan cannot see: an unpinned ref is a documented form, so no rule over the
    text alone separates "deliberately unpinned" from "lost its pin".

    Replacing the list with the scan traded the second guarantee for the first and
    was described as only a gain. It was not.
    """
    failed = False
    pattern = install_pin_pattern(repository)
    carrying: set[str] = set()

    for path in sorted(workspace_files(root)):
        if path.suffix != ".md" or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue  # text hygiene owns unreadable files and reports them there
        pinned = pattern.findall(text)
        if not pinned:
            continue
        relative_path = path.relative_to(root).as_posix()
        carrying.add(relative_path)
        for stale in sorted(set(pinned) - {version}):
            print(f"FAIL {relative_path} - install pin v{stale} must match distribution.json")
            failed = True

    for relative_path in PINNED_INSTALL_DOCS:
        if relative_path not in carrying:
            print(f"FAIL {relative_path} - a registered install doc carrying no pin")
            failed = True

    # Only when nothing is registered: with a non-empty list the rows above say it
    # better, one per document. This fires when the list itself was emptied, so
    # deleting the registry cannot buy a clean answer.
    if not PINNED_INSTALL_DOCS and not carrying:
        print("FAIL distribution.json - no documented install pin names the release tag")
        failed = True

    return failed


def validate_distribution(root: Path) -> DistributionValidation:
    """Validate canonical distribution metadata and host projections."""
    distribution_file = root / "distribution.json"
    distribution, error = read_json_object(distribution_file)
    if error is not None:
        print(printable(f"FAIL distribution.json - {error}"))
        return DistributionValidation(False, None)
    assert distribution is not None

    failed = False
    name = distribution.get("name")
    version = distribution.get("version")
    publisher_id = distribution.get("publisher_id")
    description = distribution.get("description")
    skills_directory = distribution.get("skills_directory")
    repository = distribution.get("repository")
    if distribution.get("schema") != 1:
        print("FAIL distribution.json - schema must be 1")
        failed = True
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        print("FAIL distribution.json - name must use lowercase hyphen-case")
        failed = True
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        print("FAIL distribution.json - version must use semantic version format x.y.z")
        failed = True
    if not isinstance(description, str) or not description:
        print("FAIL distribution.json - description must be a non-empty string")
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
            print(printable(f"FAIL {relative_path} - {error}"))
            failed = True
            continue
        assert manifest is not None
        if manifest.get("name") != name:
            print(f"FAIL {relative_path} - name must match distribution.json")
            failed = True
        if manifest.get("version") != version:
            print(f"FAIL {relative_path} - version must match distribution.json")
            failed = True

    # Only when there is a release to compare pins against. An unusable version is
    # already reported above, and every pinned doc would repeat it once more.
    if isinstance(version, str) and VERSION_PATTERN.fullmatch(version):
        if not isinstance(repository, str) or not repository:
            print("FAIL distribution.json - repository must be a non-empty string to check pins")
            failed = True
        elif validate_install_pins(root, repository, version):
            failed = True

    # Only when there is a canonical sentence to project. Without one the failure is
    # already reported above, and every host would repeat it once more.
    if isinstance(description, str) and description:
        if validate_projected_descriptions(root, description):
            failed = True

    if not failed:
        print(printable(f"OK   distribution {name} {version}"))
    return DistributionValidation(not failed, canonical_publisher)
