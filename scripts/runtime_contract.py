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
from read_whole import COMMENT, Read, Unread, shell_words, whole


ROOT = Path(__file__).resolve().parent.parent
PYTHON_VERSION = re.compile(r"^(\d+)\.(\d+)$")
RUFF_TARGET = re.compile(r'^target-version\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
REQUIREMENTS = Path("requirements-maintenance.txt")
WORKFLOW = Path(".github/workflows/validate.yml")
INSTALL_LINE = re.compile(r"(?<![\w-])pip(?:3)?\s+install(?![\w-])")
RUN_KEY = re.compile(r"^(\s*(?:-\s+)?)run\s*:[ \t]*(.*?)\s*$")
# A block scalar header carries an indentation indicator and a chomping indicator
# in either order, so `>2-` and `>-2` are both valid and mean the same thing.
BLOCK_HEADER = re.compile(r"[|>](?:[1-9][-+]?|[-+][1-9]?)?")
UNRESOLVED = re.compile(r"[|>*&]")
REQUIREMENT = re.compile(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([0-9][0-9A-Za-z.!+*_-]*)")
SETUP = "run the maintenance environment setup from README.md"


def requirement(token: str) -> Read | None:
    """The exact pin a token states — unread if it states one this cannot read whole,
    and None if it states none at all.

    The two callers used to answer this question with two different matchers. The
    workflow's version ended at a list of characters that may follow it and the
    requirements file's at the version's own alphabet, and each was wrong in its own
    way about the same grammar. One reader, and it truncates neither: `whole()` is the
    only way to a value here, and `whole()` only calls `fullmatch`.

    A token carrying no `==` states no exact pin. A range, an `-r`, a bare name and a
    plain word are all legal where these are read, and none of them is a failed read.
    """
    if "==" not in token:
        return None
    return whole(token, REQUIREMENT, "an exact pin")


def pins(text: str) -> tuple[dict[str, str], list[str]]:
    """Every exact pin a declaration states, and every one it states unreadably.

    A requirements line may carry a trailing comment or an environment marker, and a
    pyproject dependency arrives wrapped in quotes and a comma. All three are legal and
    all three otherwise end up inside the version, so each is removed before it is read.

    The comment cut follows the shell's rule, which is pip's: `#` starts one at the
    beginning of a word, not wherever it appears. Cutting at the first `#` read
    `tool==1.0#x` as `1.0`. The marker cut needs no such care — `;` cannot occur inside
    a version, so ending there cannot end early.

    Neither PEP 440 nor TOML has a parser available on this floor, so the grammar here
    is hand-written, and `development-knowns.yaml` records that with the owner it does
    not use. What the hand-written part cannot do is truncate.
    """
    found: dict[str, str] = {}
    unreadable: list[str] = []
    for line in text.splitlines():
        stated = COMMENT.split(line, maxsplit=1)[0].split(";", 1)[0].strip().strip('",').strip()
        read = requirement(stated)
        if read is None:
            continue
        if isinstance(read, Unread):
            unreadable.append(read.text)
            continue
        found[read.group(1)] = read.group(2)
    return found, unreadable


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


def workflow_pins(text: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Every exact pin the workflow installs, and everything it states unreadably.

    Three failures bound this. Anchoring the whole match on `pip install ` read only the
    first package and only one spelling. Dropping the anchor read raw YAML, so a comment
    and an `echo` became installs. Reading every scalar made any key executable, so
    installation text under `env:` was reported as a pin.

    So a run command decides whether it installs and its words decide what. The words
    come from `shlex`, which owns the shell's quoting: an operator ends a word, a quote
    holds one together, and nothing here has to guess which characters may follow a
    version. A command the lexer cannot finish is reported rather than half-read.
    """
    found: list[tuple[str, str]] = []
    commands, unreadable = run_commands(text)
    for command in commands:
        words = shell_words(command)
        if isinstance(words, Unread):
            unreadable.append(words.text)
            continue
        if not INSTALL_LINE.search(" ".join(words)):
            continue
        for word in words:
            read = requirement(word)
            if read is None:
                continue
            if isinstance(read, Unread):
                unreadable.append(read.text)
            else:
                found.append((read.group(1), read.group(2)))
    return found, unreadable


def run_commands(text: str) -> tuple[list[str], list[str]]:
    """Every command the workflow runs, and every `run:` value this cannot resolve.

    Only a `run:` value is a command. Every other scalar — a `name:`, an `env:` entry,
    a `with:` input — is data the step is handed, and reading those as commands made a
    documented pip invocation inside a help string count as an install.

    Then two joins, because two layers wrap the command. YAML folds a `>` scalar's
    lines into one before the shell ever sees them, so `pip install` and its requirement
    can sit on separate physical lines with no backslash at all. A literal `|` scalar
    keeps its newlines, so its lines stay separate commands. A plain scalar folds onto
    its more-indented lines the same way `>` does. The shell then continues any of them
    onto the next line with a trailing backslash. A block's body is the lines indented
    past the `run` key, which is also what ends it.

    What this cannot resolve, it says so about. `>2-` is a valid block header — the
    indentation and chomping indicators come in either order — and matching only one
    order sent it down the plain-scalar path, where the invocation and its pin became
    two commands and the pin vanished with no error. That is the same hole the token
    readers had, one layer up: a misreading that produces a smaller correct-looking
    answer instead of a complaint. An alias or anchor is unresolvable here for the same
    reason and is reported rather than read as literal text.
    """
    lines = text.splitlines()
    commands: list[str] = []
    unresolved: list[str] = []
    index = 0
    while index < len(lines):
        key = RUN_KEY.match(lines[index])
        index += 1
        if not key:
            continue

        depth, value = len(key.group(1)), key.group(2)
        body: list[str] = []
        while index < len(lines):
            line = lines[index]
            if line.strip() and len(line) - len(line.lstrip()) <= depth:
                break
            body.append(line)
            index += 1

        if BLOCK_HEADER.fullmatch(value):
            if value.startswith(">"):
                commands.append(" ".join(line.strip() for line in body if line.strip()))
            else:
                commands.extend(_continued(body))
        elif UNRESOLVED.match(value):
            unresolved.append(f"run: {value}")
        else:
            commands.extend(_continued([value, *body]))
    return commands, unresolved


def _continued(lines: list[str]) -> list[str]:
    """Join shell continuations, so a backslash-wrapped invocation is one command."""
    commands: list[str] = []
    pending = ""
    for line in lines:
        stripped = line.strip()
        if stripped.endswith("\\"):
            pending += stripped[:-1] + " "
            continue
        commands.append((pending + stripped).strip())
        pending = ""
    if pending:
        commands.append(pending.strip())
    return [command for command in commands if command]


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
        declared, unreadable = pins(requirements_text)
        for line in unreadable:
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
        installs, unreadable = workflow_pins(workflow_text)
        for line in unreadable:
            errors.append(f"{WORKFLOW.name} states {printable(line)}, which cannot be read")
        for name, pinned in sorted(set(installs)):
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
