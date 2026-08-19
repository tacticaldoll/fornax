#!/usr/bin/env python3
"""Keep the maintenance Python floor aligned with Ruff's syntax target."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PYTHON_VERSION = re.compile(r"^(\d+)\.(\d+)$")
RUFF_TARGET = re.compile(r'^target-version\s*=\s*"([^"]+)"\s*$', re.MULTILINE)


def _read(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeError:
        errors.append(f"{path.name} must use UTF-8")
    except OSError as error:
        errors.append(f"{path.name} could not be read: {error}")
    return None


def check(root: Path) -> list[str]:
    """Return runtime-contract diagnostics for one repository root."""
    errors: list[str] = []
    version_text = _read(root / ".python-version", errors)
    ruff_text = _read(root / "ruff.toml", errors)

    version = None
    if version_text is not None:
        match = PYTHON_VERSION.fullmatch(version_text.strip())
        if match is None:
            errors.append(".python-version must contain major.minor")
        else:
            version = match.groups()

    target = None
    if ruff_text is not None:
        targets = RUFF_TARGET.findall(ruff_text)
        if len(targets) != 1:
            errors.append("ruff.toml must declare one target-version")
        else:
            target = targets[0]

    if version is not None and target is not None:
        expected = f"py{version[0]}{version[1]}"
        if target != expected:
            errors.append(
                f"ruff.toml target-version must be {expected} to match .python-version"
            )
    return errors


def main() -> int:
    errors = check(ROOT)
    for error in errors:
        print(f"FAIL runtime contract - {error}")
    if errors:
        return 1
    print("OK   maintenance runtime contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
