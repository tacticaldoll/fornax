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

The workflow used to install its own style pin rather than reading the requirements file, so the two
could name different releases while both looked deliberate. That duplicate is gone: the gate the
workflow runs installs from the requirements file and checks style inside itself. Every
`name==version` token the workflow carries inline is compared against the requirements file anyway —
derived from the token rather than from one command spelling, because anchoring on `pip install `
missed `--upgrade`, a quoted spec, and every package after the first on one line. Zero of them is
the intended state and a clean answer, and the comparison is what keeps a reintroduced one from
passing quietly. A VCS ref is out of scope: the workflow installs the deployment engine as
`agent-skill-deployer @ git+…@v0.1.2`, which the requirements file does not declare and this does
not read, so that pin is guarded by nothing here.
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
WORKFLOW = Path(".github/workflows/validate.yml")
WORKFLOW_PIN = re.compile(r"(?<![\w.-])([A-Za-z0-9][A-Za-z0-9._-]*)==([A-Za-z0-9][^\s\"',;]*)")
INSTALL_LINE = re.compile(r"(?<![\w-])pip(?:3)?\s+install(?![\w-])")
DECLARATION = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==(.+)$")
VERSION = re.compile(r"[0-9][0-9A-Za-z.!+*_-]*")
SETUP = "run the maintenance environment setup from README.md"


def pins(text: str) -> tuple[dict[str, str], list[str]]:
    """Every ``name==version`` a declaration states, and every one that does not parse.

    A requirements line may carry a trailing comment or an environment marker, and a
    pyproject dependency arrives wrapped in quotes and a comma. All three are legal and
    all three otherwise end up inside the version, so each is removed before it is read.

    What is left must then be a version *entirely* — `fullmatch`, not a prefix. Matching
    a prefix of the version's own alphabet was the previous form, and it was worse than
    the terminator list it replaced: `ruff==0.16.1|x` had produced `0.16.1|x`, which
    failed its comparison loudly, and became `0.16.1`, which passes. An alphabet is a
    guess about which characters a version may hold — it omitted the `_` that PEP 440
    admits in a local version — and consuming the whole declaration is what checks the
    guess held. A line that declares an exact pin and does not parse as one is returned
    as malformed, because the alternative is to compare the part that happened to match.

    A line that declares no exact pin is not malformed. `-r base.txt`, a range, a bare
    name and a comment are all legal in a requirements file and none of them is a claim
    this function failed to read.
    """
    found: dict[str, str] = {}
    malformed: list[str] = []
    for line in text.splitlines():
        stated = line.split("#", 1)[0].split(";", 1)[0].strip().strip('",').strip()
        declaration = DECLARATION.match(stated)
        if not declaration:
            continue
        name, version = declaration.groups()
        if VERSION.fullmatch(version):
            found[name] = version
        else:
            malformed.append(stated)
    return found, malformed


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


def workflow_pins(text: str) -> list[tuple[str, str]]:
    """Every exact pin the workflow actually installs, wherever on its line it sits.

    Two failures bound this. Anchoring the whole match on `pip install ` read only the
    first package and only one spelling, so `--upgrade`, a quoted spec, and a second
    package all passed unread. Dropping the anchor entirely read raw YAML, so a comment
    or an `echo` became an install.

    So the logical command decides whether it installs and the token decides what: a
    command carrying a pip install invocation contributes every `name==version` in it,
    and one that does not contributes none. A comment is not an install command — the
    `#` ends it before the invocation, and a commented-out install is not one either.

    Logical, not physical. A trailing backslash continues the command onto the next
    line, which the ordinary way of writing a long pip invocation uses, and reading
    physical lines missed the requirement entirely — the invocation on one line and the
    pin on the next.
    """
    found: list[tuple[str, str]] = []
    for command in logical_commands(text):
        executable = command.split("#", 1)[0]
        if not INSTALL_LINE.search(executable):
            continue
        found.extend(WORKFLOW_PIN.findall(executable))
    return found


def logical_commands(text: str) -> list[str]:
    """Return one string per command the workflow runs, however it is written.

    Two joins, because two layers wrap the command. YAML folds a `>` scalar's lines
    into one before the shell ever sees them, so `pip install` and its requirement can
    sit on separate physical lines with no backslash at all — which a backslash joiner
    read as two commands and matched in neither. The shell then continues a line with a
    trailing backslash.

    A folded block is joined by indentation: the lines more indented than the key
    introducing it belong to it. A literal `|` block keeps its newlines, so its lines
    stay separate commands and only the backslash join applies to them.
    """
    commands: list[str] = []
    pending = ""
    folding: int | None = None
    for line in text.splitlines():
        indent = len(line) - len(line.lstrip())
        if folding is not None:
            if line.strip() and indent > folding:
                pending += line.strip() + " "
                continue
            commands.append(pending.rstrip())
            pending, folding = "", None
        if re.search(r":\s*>[-+]?\s*$", line):
            folding = indent
            pending = ""
            continue
        stripped = line.rstrip()
        if stripped.endswith("\\"):
            pending += stripped[:-1] + " "
            continue
        commands.append(pending + line)
        pending = ""
    if pending:
        commands.append(pending.rstrip())
    return commands


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
        declared, malformed = pins(requirements_text)
        for line in malformed:
            errors.append(f"{REQUIREMENTS.name} states {printable(line)}, which is not a pin")
        if not declared:
            errors.append(f"{REQUIREMENTS.name} must pin at least one name==version")
        for name, pinned in sorted(declared.items()):
            found = installed(name)
            if found is None:
                errors.append(f"{name} is pinned at {pinned} but is not installed; {SETUP}")
            elif found != pinned:
                errors.append(f"{name} is pinned at {pinned} but {found} is installed; {SETUP}")

    # Absence is a failure, not a clean answer. Zero seams is legitimate — a repository
    # may genuinely have none — but PROJECT.md calls this repo "enforced by CI", so a
    # missing workflow contradicts a standing decision rather than describing a state.
    workflow_text = _read(root / WORKFLOW, errors)
    if workflow_text is not None and requirements_text is not None:
        declared, _ = pins(requirements_text)
        for name, pinned in sorted(set(workflow_pins(workflow_text))):
            if name not in declared:
                errors.append(
                    f"{WORKFLOW.name} installs {name}=={pinned}, which "
                    f"{REQUIREMENTS.name} does not declare"
                )
            elif declared[name] != pinned:
                errors.append(
                    f"{WORKFLOW.name} installs {name}=={pinned} but "
                    f"{REQUIREMENTS.name} pins {declared[name]}"
                )

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
