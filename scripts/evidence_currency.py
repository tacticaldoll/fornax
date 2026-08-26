#!/usr/bin/env python3
"""Keep recorded behavioral evidence tied to the wording it actually tested.

A micro-test or fresh-context scenario measures one version of one piece of prose.
The prose then moves and the recorded result stays, so a reader finds a dated number
that no longer describes what ships. This repository has already been there: the
`triage-findings` scenario went stale, `docs/review-record-contract.md` says so in
prose, and nothing failed.

What this can check is not whether the guidance still works — that needs model calls,
which do not belong in a fast deterministic gate. It checks the weaker thing that is
still decisive: whether the text a result claims to have measured is the text that is
there now. Drift is then a failure with a name instead of a caveat someone has to
remember to read.

An entry is `current` and its fingerprint must match, or `superseded` and must say
why. Which directory is a scenario root cannot be derived — a root and a grouping
level look alike from the tree — so the registry declares the roots and this derives
the other direction: every file under the scenario tree that no declared root
accounts for. Each half guards what the other cannot, which is the split the
install-pin check settled on for the same reason.

Depends on `markdown_links` for CommonMark parsing, which brings `markdown-it-py`
— pinned in requirements-maintenance.txt. Otherwise the standard library.

    .venv/bin/python scripts/evidence_currency.py --check
    .venv/bin/python scripts/evidence_currency.py --fingerprint <path> [heading]
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from constrained_yaml import raw_scalar
from diagnostic_text import printable
from host_paths import has_parent_segment_anywhere, is_absolute_anywhere
from markdown_links import heading_section
from path_boundary import Boundary, Verdict, resolve_within


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = Path("scripts/tests/scenarios/evidence.yaml")
SCENARIOS = Path("scripts/tests/scenarios")

ENTRY_START = re.compile(r"^  - id:\s+(.+?)\s*$")
ENTRY_FIELD = re.compile(r"^    ([a-z][a-z0-9-]*):(?:\s+(.*?))?\s*$")
SCHEMA_LINE = re.compile(r"^schema:\s+(.+?)\s*$")
WHOLE_FILE = "whole-file"

STATES = ("current", "superseded")
REQUIRED = {"id", "state", "tests", "section", "recorded", "record"}
OPTIONAL = {"fingerprint", "superseded-reason"}


class EvidenceError(ValueError):
    """The registry could not be read, or does not satisfy the entry model."""


@dataclass(frozen=True)
class Evidence:
    fields: dict[str, str]

    def get(self, name: str) -> str:
        return self.fields.get(name, "")


def _scalar(value: str, number: int) -> str:
    return raw_scalar(value, number, EvidenceError)


def load(path: Path) -> tuple[Evidence, ...]:
    """Read the registry's small YAML subset into entries, in file order."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeError as error:
        raise EvidenceError(f"{path} must use UTF-8: {error}") from error
    except OSError as error:
        raise EvidenceError(str(error)) from error

    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    seen_schema = False
    seen_evidence = False

    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        schema = SCHEMA_LINE.match(line)
        if schema is not None:
            if seen_schema or seen_evidence:
                raise EvidenceError(f"line {number}: schema must appear once, first")
            if _scalar(schema.group(1), number) != "1":
                raise EvidenceError(f"line {number}: schema must be 1")
            seen_schema = True
            continue
        if line.rstrip() == "evidence:":
            if not seen_schema:
                raise EvidenceError(f"line {number}: schema must precede evidence")
            seen_evidence = True
            continue
        start = ENTRY_START.match(line)
        if start is not None:
            if not seen_evidence:
                raise EvidenceError(f"line {number}: entries must sit under evidence")
            if current is not None:
                entries.append(current)
            current = {"id": _scalar(start.group(1), number)}
            continue
        field = ENTRY_FIELD.match(line)
        if field is None or current is None:
            raise EvidenceError(f"line {number}: unsupported line {line!r}")
        key, value = field.group(1), field.group(2)
        if key in current:
            raise EvidenceError(f"line {number}: {key} appears twice in {current['id']}")
        if key not in REQUIRED | OPTIONAL:
            raise EvidenceError(f"line {number}: unknown field {key}")
        current[key] = _scalar(value or "", number)

    if current is not None:
        entries.append(current)
    if not seen_schema:
        raise EvidenceError(f"{path} must declare schema: 1")
    return tuple(Evidence(entry) for entry in entries)


def validate(entries: tuple[Evidence, ...]) -> None:
    """Enforce the entry model, so a check never reads a half-declared claim."""
    seen: set[str] = set()
    for entry in entries:
        identifier = entry.get("id")
        if identifier in seen:
            raise EvidenceError(f"duplicate id {identifier}")
        seen.add(identifier)
        missing = sorted(REQUIRED - set(entry.fields))
        if missing:
            raise EvidenceError(f"{identifier}: missing {', '.join(missing)}")
        state = entry.get("state")
        if state not in STATES:
            raise EvidenceError(f"{identifier}: state must be one of {', '.join(STATES)}")
        if state == "current" and not entry.get("fingerprint"):
            raise EvidenceError(f"{identifier}: current evidence requires a fingerprint")
        if state == "superseded" and not entry.get("superseded-reason"):
            raise EvidenceError(f"{identifier}: superseded evidence requires a reason")
        tests = entry.get("tests")
        if not spelled_inside(tests):
            raise EvidenceError(
                f"{identifier}: tests must name a path inside the repository, relative "
                f"and with no parent segment — the fingerprint is of a file this "
                f"repository ships, and only record was bounded"
            )
        record = entry.get("record")
        if not scenario_root(record):
            raise EvidenceError(
                f"{identifier}: record must sit inside a scenario directory under "
                f"{SCENARIOS.as_posix()}, as a relative path with no parent segment — "
                f"its parent becomes the root that accounts for files, and a parent "
                f"outside or above a scenario accounts for the whole tree"
            )


def spelled_inside(candidate: str) -> bool:
    """Whether a path is *written* as something inside a repository.

    The entry model can judge spelling without a filesystem, which is what lets the
    registry be validated against any root. An absolute path or a parent segment names
    something outside whatever it resolves to, so both are refused.

    Asked through `host_paths`, which owns the question and asks both host grammars.
    Answering it here with `Path` alone gave the POSIX reading only, so `C:/x` and
    `..\\x` were spelled inside on this host — a third spelling of a path rule in a
    repository whose `skill_model.NAME_PATTERN` docstring already records what happens
    when one diverges.
    """
    if not candidate:
        return False
    return not is_absolute_anywhere(candidate) and not has_parent_segment_anywhere(candidate)


def resolved_inside(candidate: str, root: Path) -> bool:
    """Whether a path *resolves* to something inside `root`.

    Spelling is not enough where the next act is to read the file: a
    repository-relative symlink pointing at `/etc/hosts` is relative and has no parent
    segment, so a lexical rule passed it and its target was fingerprinted.
    `path_boundary` exists for this and states in its own contract that existence is
    asked of the resolved target, which is what makes a symlink escape read as one.

    Asked at the read rather than in `validate`, because resolution needs a root and the
    entry model must stay judgeable without one.
    """
    if not spelled_inside(candidate):
        return False
    return resolve_within(root / Path(candidate), Boundary.at(root)).verdict is Verdict.INSIDE


def scenario_root(record: str) -> Path | None:
    """Return the scenario directory a record declares, or None when it declares none.

    Stated as the shape a root may have rather than as the shapes to refuse. The list
    of refusals was one entry long — a parent equal to SCENARIOS — while `.`, `scripts`
    and `scripts/tests` all passed it and all cover the whole tree, and an absolute or
    parent-relative path passed too. A positive rule has no such remainder.

    A root is `SCENARIOS/<name>[/...]`: relative, no parent segment, and at least one
    directory below the tree that holds it. The parent of the record is that root, and
    it is what decides which files the entry accounts for.
    """
    if not record:
        return None
    path = Path(record)
    if path.is_absolute() or ".." in path.parts:
        return None
    parent = path.parent
    if parent == SCENARIOS or not parent.is_relative_to(SCENARIOS):
        return None
    return parent


def section_text(text: str, heading: str) -> str | None:
    """Return one Markdown section, heading line included, or None when absent.

    The grammar is delegated to `markdown_links`, which already owns the repository's
    CommonMark parser. The rule this replaced treated any `#`-prefixed line as a
    heading, so a shebang inside a fenced block ended the section and the fingerprint
    covered part of the text it named.
    """
    if heading == WHOLE_FILE:
        return text
    return heading_section(text, heading)


def fingerprint(root: Path, tests: str, heading: str) -> str | None:
    """Hash the text an entry claims to have measured, or None when it is gone.

    The path is resolved against the root before reading, so a symlink escaping the
    repository is `None` rather than a hash of whatever it points at.
    """
    if not resolved_inside(tests, root):
        return None
    try:
        text = (root / tests).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    found = section_text(text, heading)
    if found is None:
        return None
    return hashlib.sha256(found.encode("utf-8")).hexdigest()[:16]


def unaccounted_files(root: Path, registered: set[str]) -> list[str]:
    """Name every file under the scenario tree that no registered record accounts for.

    Files, not directories. Naming the directory claimed a grouping level as though it
    were a scenario, which stopped the registered scenarios beneath it from being
    enumerated at all — the behaviour a previous rewrite reported as a defect and then
    reproduced, because it changed which directory was chosen and not whether one was.
    A file has no children to mask.

    Which directory is a scenario root cannot be derived: a root and a grouping level
    both hold subdirectories that hold files, and only the registry knows which is
    which. So the registry declares the roots and this derives the other direction —
    every file no declared root contains. That is the split the install pin check
    settled on, and each half guards what the other cannot.
    """
    base = root / SCENARIOS
    if not base.is_dir():
        return []
    roots = [root / found for found in map(scenario_root, registered) if found is not None]
    found = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path == root / REGISTRY:
            continue
        if any(path.is_relative_to(claimed) for claimed in roots):
            continue
        found.append(path.relative_to(root).as_posix())
    return found


def check(root: Path, entries: tuple[Evidence, ...]) -> bool:
    """Report each entry as current, superseded, or drifted. True when any drifted."""
    failed = False
    for entry in entries:
        record = entry.get("record")
        if not resolved_inside(record, root) or not (root / record).is_file():
            print(
                printable(
                    f"FAIL {entry.get('id')} - its record {record} is not a file inside "
                    f"this repository; a claim pointing at a deleted result, or at a "
                    f"symlink out of the tree, is the defect one round later"
                )
            )
            failed = True

    registered = {entry.get("record") for entry in entries}
    for relative_path in unaccounted_files(root, registered):
        print(
            printable(
                f"FAIL {relative_path} - under the scenario tree with no registry entry "
                f"accounting for it; register the scenario it belongs to, or delete it"
            )
        )
        failed = True
    for entry in entries:
        identifier = entry.get("id")
        if entry.get("state") == "superseded":
            print(printable(f"SUPERSEDED {identifier} - {entry.get('superseded-reason')}"))
            continue
        found = fingerprint(root, entry.get("tests"), entry.get("section"))
        if found is None:
            print(
                printable(
                    f"FAIL {identifier} - {entry.get('tests')} no longer carries "
                    f"{entry.get('section')}"
                )
            )
            failed = True
            continue
        if found != entry.get("fingerprint"):
            print(
                printable(
                    f"FAIL {identifier} - {entry.get('tests')} changed since the evidence "
                    f"recorded {entry.get('recorded')}; re-run it and update the fingerprint, "
                    f"or mark the entry superseded"
                )
            )
            failed = True
            continue
        print(printable(f"OK   {identifier} {entry.get('recorded')}"))
    return failed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="verify every recorded claim")
    mode.add_argument("--fingerprint", nargs="+", metavar=("PATH", "HEADING"))
    arguments = parser.parse_args(argv)

    if arguments.fingerprint:
        path = arguments.fingerprint[0]
        heading = " ".join(arguments.fingerprint[1:]) or WHOLE_FILE
        found = fingerprint(ROOT, path, heading)
        if found is None:
            print(printable(f"FAIL {path} does not carry {heading}"), file=sys.stderr)
            return 1
        print(found)
        return 0

    try:
        entries = load(ROOT / REGISTRY)
        validate(entries)
    except EvidenceError as error:
        print(printable(f"FAIL {REGISTRY} - {error}"), file=sys.stderr)
        return 1
    if check(ROOT, entries):
        return 1
    print(printable(f"OK   {REGISTRY} ({len(entries)} claim(s))"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
