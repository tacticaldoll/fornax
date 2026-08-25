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
why. The set that must be registered is derived from the scenario directories on
disk rather than maintained here, so a scenario nobody registered is a failure
instead of an absence — the same reason the install-pin check reads the workspace
rather than a list.

Standard library only.

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


def section_text(text: str, heading: str) -> str | None:
    """Return one Markdown section, heading line included, or None when absent.

    The heading is named by its text, not by its `#` prefix: a plain scalar may not
    open with `#` in this repository's YAML subset, and the level is readable from
    the document anyway.
    """
    if heading == WHOLE_FILE:
        return text
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("#") or line.lstrip("#").strip() != heading:
            continue
        depth = len(line) - len(line.lstrip("#"))
        for offset in range(index + 1, len(lines)):
            candidate = lines[offset]
            if candidate.startswith("#"):
                level = len(candidate) - len(candidate.lstrip("#"))
                if level <= depth:
                    return "\n".join(lines[index:offset])
        return "\n".join(lines[index:])
    return None


def fingerprint(root: Path, tests: str, heading: str) -> str | None:
    """Hash the text an entry claims to have measured, or None when it is gone."""
    try:
        text = (root / tests).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    found = section_text(text, heading)
    if found is None:
        return None
    return hashlib.sha256(found.encode("utf-8")).hexdigest()[:16]


def scenario_directories(root: Path) -> list[str]:
    """Every checked-in scenario, as the registry would name its record."""
    base = root / SCENARIOS
    if not base.is_dir():
        return []
    found = []
    for path in sorted(base.rglob("README.md")):
        found.append(path.relative_to(root).as_posix())
    return found


def check(root: Path, entries: tuple[Evidence, ...]) -> bool:
    """Report each entry as current, superseded, or drifted. True when any drifted."""
    failed = False
    registered = {entry.get("record") for entry in entries}
    for record in scenario_directories(root):
        if record not in registered:
            print(
                printable(
                    f"FAIL {record} - a checked-in scenario with no registry entry; "
                    f"record what wording it measured, or delete it"
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
