#!/usr/bin/env python3
"""Keep the declared maintenance runtime consistent with everything that reads it.

.python-version is the single source for the floor, so what follows must agree with
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
`agent-skill-deployer @ git+…@v0.1.2`, or the maintenance requirements install the builder from a
tagged VCS reference. This check does not compare those refs as package versions; repository release
policy guards their immutable tags.
"""

from __future__ import annotations

import re
import shlex
import sys
from importlib.metadata import PackageNotFoundError, version as installed_version
from pathlib import Path
from typing import Callable

import yaml

from packaging.requirements import InvalidRequirement, Requirement

from agent_skill_format.diagnostic_text import printable
from agent_skill_format.read_whole import COMMENT, Unread


ROOT = Path(__file__).resolve().parent.parent
PYTHON_VERSION = re.compile(r"^(\d+)\.(\d+)$")
RUFF_TARGET = re.compile(r'^target-version\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
REQUIREMENTS = Path("requirements-maintenance.txt")
WORKFLOW = Path(".github/workflows/validate.yml")
CONTROL = frozenset({";", "&&", "||", "|", "&"})
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
PIP = re.compile(r"(?:.*/)?pip[0-9.]*")
PYTHON = re.compile(r"(?:.*/)?python[0-9.]*")
# GitHub's expression language, which nothing here parses: what it expands to
# is decided at run time and may well be an install.
EXPRESSION = re.compile(r"\$\{\{")
SETUP = "run the maintenance environment setup from README.md"


def requirement(token: str) -> tuple[str, str] | Unread | None:
    """The exact pin a token states — unread if it states one that will not parse, and
    None if it states no exact pin at all.

    PEP 508 is `packaging`'s grammar and this is `packaging` reading it. Hand-writing it
    fails in both directions, measured: a terminator list runs past `|` and yields a
    malformed pin that fails loudly, while the version's own alphabet stops there and
    keeps the prefix, turning that into a pin which passes its comparison. The alphabet
    also omits the `_` PEP 440 admits in a local version, so a valid declaration reads as
    a different pin.

    `Requirement` is total the way `whole()` is, and for the same reason: it consumes
    the string or raises, and there is no answer in between for a caller to compare
    against something. A range, a bare name and an `-r` line state no exact pin, which
    is not a failed read.
    """
    if "==" not in token:
        return None
    try:
        parsed = Requirement(token)
    except InvalidRequirement as error:
        return Unread(token, f"is not a requirement: {str(error).splitlines()[0]}")
    stated = list(parsed.specifier)
    if len(stated) != 1 or stated[0].operator != "==":
        return None
    return parsed.name, stated[0].version


def pins(text: str) -> tuple[dict[str, str], list[str]]:
    """Every exact pin a declaration states, and every one it states unreadably.

    A requirements line may carry a trailing comment or an environment marker, and a
    pyproject dependency arrives wrapped in quotes and a comma. All three are legal and
    all three otherwise end up inside the version, so each is removed before it is read.

    An environment marker needs no handling: `packaging` owns PEP 508 and reads the
    marker as part of the requirement. What is left here belongs to two formats it does
    not own. The comment cut is pip's requirements-file rule, which is the shell's — a
    `#` starts one at the beginning of a word, not wherever it appears, and cutting at
    the first one read `tool==1.0#x` as `1.0`. The quote and comma stripping is TOML's,
    for a pyproject dependency string; `tomllib` owns that grammar and arrives in
    Python 3.11, which `.python-version` does not declare, so it stays hand-written and
    `development-knowns.yaml` records it.
    """
    found: dict[str, str] = {}
    unreadable: list[str] = []
    for line in text.splitlines():
        stated = COMMENT.split(line, maxsplit=1)[0].strip().rstrip(",").strip()
        # A pyproject dependency arrives as a quoted TOML string. Unwrap only when the
        # line is one: stripping a trailing quote unconditionally cut the closing quote
        # off an environment marker, which PEP 508 puts inside the requirement.
        if len(stated) > 1 and stated[0] == stated[-1] and stated[0] in "\"'":
            stated = stated[1:-1]
        read = requirement(stated)
        if read is None:
            continue
        if isinstance(read, Unread):
            unreadable.append(read.text)
            continue
        found[read[0]] = read[1]
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


def direct_pins(text: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Every exact pin the workflow states where it installs, and what it states unreadably.

    The workflow installs from `REQUIREMENTS`, which is the one place a maintenance
    version is written, so stating a pin in a step's `run` is the defect rather than
    something to reconcile. `requirement` is `packaging` reading PEP 508, and the shell
    reconstruction this replaced needed a grammar with no installed owner.

    Where a pin sits is YAML's question and PyYAML answers it. Reading the file's text
    instead made a version in a comment, a step `name` or an `env` value into a pin the
    workflow installs — measured, all three, and none of them is an install.

    What a word is, is `shlex`'s. Splitting on whitespace lost `pip install "tool == 1.0"`
    entirely: a legal exact pin, held together by quoting, read as three tokens that are
    each no requirement at all. That is the direction this must not fail in — the
    workflow states a pin and the gate says nothing. Quoting has an owner and always did;
    what had none was where a comment begins, and this does not ask.

    Not asking costs a pin written inside a `run` comment, which is reported as stated.
    Refusing that is the conservative direction and needs no grammar.

    A token carrying `==` that `packaging` will not parse is reported rather than
    dropped, which is the channel the return type and the caller already promised. It
    costs a shell comparison written with `==` in a `run` block, which is reported and
    is not one this repository's workflow contains.
    """
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as error:
        return [], [f"is not readable YAML: {error}"]
    found: list[tuple[str, str]] = []
    unreadable: list[str] = []
    for value in _run_values(document):
        if not isinstance(value, str):
            unreadable.append(f"run: {value!r}")
            continue
        lexer = shlex.shlex(value, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = ""
        try:
            words = list(lexer)
        except ValueError as error:
            unreadable.append(f"run: {value} is not a shell command: {error}")
            continue
        for word in words:
            read = requirement(word)
            if isinstance(read, tuple):
                found.append(read)
            elif isinstance(read, Unread):
                unreadable.append(str(read))
    return found, unreadable


def _run_values(document: object) -> list[object]:
    """Every value a step's `run` key carries, by where it sits and not by its name.

    Selecting every key named `run` anywhere in the document made a mapping under
    `env:` or a matrix entry into a command the workflow runs. Nothing executes those,
    and the pin one of them mentions is not a pin the workflow installs.

    So the shape is walked: `jobs`, each job, its `steps`, each step, and that step's
    `run`. A step whose `run` is not a string is returned as it is, and the caller
    reports it rather than skipping it.

    Only a workflow's shape. A composite action states its steps under a top-level
    `runs`, and reading that here made a workflow carrying one — which no runner
    executes, because a workflow has no such key — contribute pins. The one caller
    passes `.github/workflows/validate.yml` and nothing else, so the second root was
    an input this never receives and a shape it should not accept. A composite action
    would need its own manifests found and its own kind stated, not a branch here.
    """
    found: list[object] = []
    if not isinstance(document, dict):
        return found

    jobs = document.get("jobs")
    for container in jobs.values() if isinstance(jobs, dict) else ():
        if not isinstance(container, dict):
            continue
        steps = container.get("steps")
        if not isinstance(steps, list):
            continue
        for step in steps:
            if isinstance(step, dict) and "run" in step:
                found.append(step["run"])
    return found


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
    declared: dict[str, str] = {}
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
        stated, unreadable = direct_pins(workflow_text)
        for line in unreadable:
            errors.append(f"{WORKFLOW.name} states {printable(line)}, which cannot be read")
        for name, pinned in sorted(set(stated)):
            errors.append(
                f"{WORKFLOW.name} states {name}=={pinned}; it installs from "
                f"{REQUIREMENTS.name}, which is the one place a maintenance pin is written"
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
