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


VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

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

    if validate_projected_descriptions(root, distribution.get("description")):
        failed = True

    if not failed:
        print(printable(f"OK   distribution {name} {version}"))
    return DistributionValidation(not failed, canonical_publisher)
