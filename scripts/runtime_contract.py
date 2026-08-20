#!/usr/bin/env python3
"""Keep the declared maintenance runtime consistent with everything that reads it.

.python-version is the single source for the floor, so two things must agree with
it: Ruff's syntax target, and the interpreter actually running. The second matters
because the pre-commit hook only checks that .venv/bin/python is executable — a
virtualenv built before the floor moved satisfies that and then fails later with an
ImportError rather than saying what is wrong.

requirements-maintenance.txt is the same kind of declaration and was not checked at
all. An environment holding a different version of a pinned library satisfies the
floor and then validates the workspace with a parser the pins do not name — the gate
passes while checking something else. So the installed version of every pin is
compared too.
"""

from __future__ import annotations

import re
import sys
from importlib.metadata import PackageNotFoundError, version as installed_version
from pathlib import Path
from typing import Callable

from diagnostic_text import printable


ROOT = Path(__file__).resolve().parent.parent
PYTHON_VERSION = re.compile(r"^(\d+)\.(\d+)$")
RUFF_TARGET = re.compile(r'^target-version\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
REQUIREMENTS = Path("requirements-maintenance.txt")
PIN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s;#]+)")
SETUP = "run the maintenance environment setup from README.md"


def pins(text: str) -> dict[str, str]:
    """Every ``name==version`` a declaration states, comments and markers dropped.

    A requirements line may carry a trailing comment or an environment marker, and a
    pyproject dependency arrives wrapped in quotes and a comma. All three are legal
    and all three otherwise end up inside the version string.
    """
    found: dict[str, str] = {}
    for line in text.splitlines():
        match = PIN.match(line.strip().strip('",'))
        if match:
            found[match.group(1)] = match.group(2)
    return found


def _default_installed(name: str) -> str | None:
    try:
        return installed_version(name)
    except PackageNotFoundError:
        return None


def _read(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeError:
        errors.append(f"{path.name} must use UTF-8")
    except OSError as error:
        errors.append(f"{path.name} could not be read: {error}")
    return None


def check(
    root: Path,
    running: tuple[int, int] = sys.version_info[:2],
    installed: Callable[[str], str | None] = _default_installed,
) -> list[str]:
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
            floor = (int(version[0]), int(version[1]))
            if running < floor:
                errors.append(
                    f".python-version requires Python {floor[0]}.{floor[1]} or newer, but "
                    f"this interpreter is {running[0]}.{running[1]}; run the maintenance "
                    "environment setup from README.md"
                )

    target = None
    if ruff_text is not None:
        targets = RUFF_TARGET.findall(ruff_text)
        if len(targets) != 1:
            errors.append("ruff.toml must declare one target-version")
        else:
            target = targets[0]

    requirements_text = _read(root / REQUIREMENTS, errors)
    if requirements_text is not None:
        declared = pins(requirements_text)
        if not declared:
            errors.append(f"{REQUIREMENTS.name} must pin at least one name==version")
        for name, pinned in sorted(declared.items()):
            found = installed(name)
            if found is None:
                errors.append(f"{name} is pinned at {pinned} but is not installed; {SETUP}")
            elif found != pinned:
                errors.append(f"{name} is pinned at {pinned} but {found} is installed; {SETUP}")

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
        print(printable(f"FAIL runtime contract - {error}"))
    if errors:
        return 1
    print("OK   maintenance runtime contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
