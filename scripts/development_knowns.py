#!/usr/bin/env python3
"""Validate and query the repository's project-centered development knowns.

The registry deliberately accepts a constrained YAML subset so the workspace gate
remains standard-library-only. It is not a general YAML reader: mappings are flat,
list-valued fields contain scalars, and multiline values, aliases, anchors, tags,
flow collections, and quoted scalars are rejected.

Usage:
    python3 scripts/development_knowns.py --check
    python3 scripts/development_knowns.py --list backlog
    python3 scripts/development_knowns.py --list watchlist
    python3 scripts/development_knowns.py --list accepted
    python3 scripts/development_knowns.py --list resolved
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = Path("development-knowns.yaml")

ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
TOP_FIELD = re.compile(r"^(schema|knowns):(?:\s+(.*?))?\s*$")
KNOWN_START = re.compile(r"^  - id:\s+(.+?)\s*$")
KNOWN_FIELD = re.compile(r"^    ([a-z][a-z0-9-]*):(?:\s+(.*?))?\s*$")
LIST_ITEM = re.compile(r"^      -\s+(.+?)\s*$")

SCALAR_FIELDS = {
    "id",
    "statement",
    "kind",
    "treatment",
    "rationale",
    "repair",
    "verification",
    "reconsider-when",
    "work",
    "updated",
}
LIST_FIELDS = {"evidence", "declined-changes"}
REQUIRED = {"id", "statement", "kind", "treatment", "rationale", "evidence", "updated"}
KINDS = {"defect", "risk", "constraint", "debt"}
TREATMENTS = {"remediate", "monitor", "accept", "resolved"}
WORK_STATES = {"backlog", "in-progress", "done"}
VIEWS = {"backlog", "watchlist", "accepted", "resolved"}


class KnownError(ValueError):
    """An invalid registry with a concise user-facing diagnostic."""


@dataclass(frozen=True)
class Known:
    values: dict[str, str | tuple[str, ...]]

    def scalar(self, field: str) -> str:
        value = self.values.get(field, "")
        assert isinstance(value, str)
        return value


def _scalar(value: str, number: int) -> str:
    if not value:
        raise KnownError(f"line {number}: scalar must not be empty")
    if value[0] in "'\"[{":
        raise KnownError(f"line {number}: quoted and flow-style scalars are unsupported")
    if value in {"|", ">"}:
        raise KnownError(f"line {number}: multiline scalars are unsupported")
    if re.search(r"(?:^|\s)[&*!][^\s]+", value):
        raise KnownError(f"line {number}: YAML anchors, aliases, and tags are unsupported")
    return value


def load(path: Path) -> tuple[Known, ...]:
    """Load a registry using only the documented constrained YAML shape."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise KnownError(str(error)) from error

    schema: str | None = None
    saw_knowns = False
    entries: list[dict[str, str | list[str]]] = []
    current: dict[str, str | list[str]] | None = None
    active_list: str | None = None

    for number, raw in enumerate(lines, start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        top = TOP_FIELD.fullmatch(raw)
        if top:
            key, value = top.groups()
            if key == "schema":
                if saw_knowns:
                    raise KnownError(f"line {number}: schema must precede knowns")
                if schema is not None:
                    raise KnownError(f"line {number}: duplicate schema")
                schema = _scalar(value or "", number)
            else:
                if saw_knowns:
                    raise KnownError(f"line {number}: duplicate knowns")
                if schema is None:
                    raise KnownError(f"line {number}: knowns must follow schema")
                if value:
                    raise KnownError(f"line {number}: knowns must be a block list")
                saw_knowns = True
            current = None
            active_list = None
            continue
        start = KNOWN_START.fullmatch(raw)
        if start:
            if not saw_knowns:
                raise KnownError(f"line {number}: known entry appears before knowns")
            current = {"id": _scalar(start.group(1), number)}
            entries.append(current)
            active_list = None
            continue
        field = KNOWN_FIELD.fullmatch(raw)
        if field:
            if current is None:
                raise KnownError(f"line {number}: known field has no entry")
            key, value = field.groups()
            if key not in SCALAR_FIELDS | LIST_FIELDS:
                raise KnownError(f"line {number}: unknown field {key}")
            if key in current:
                raise KnownError(f"line {number}: duplicate {key}")
            if key in LIST_FIELDS:
                if value:
                    raise KnownError(f"line {number}: {key} must be a block list")
                current[key] = []
                active_list = key
            else:
                current[key] = _scalar(value or "", number)
                active_list = None
            continue
        item = LIST_ITEM.fullmatch(raw)
        if item:
            if current is None or active_list is None:
                raise KnownError(f"line {number}: list item has no list field")
            values = current[active_list]
            assert isinstance(values, list)
            values.append(_scalar(item.group(1), number))
            continue
        raise KnownError(f"line {number}: unsupported YAML shape")

    if schema != "1":
        raise KnownError("schema must be 1")
    if not saw_knowns:
        raise KnownError("missing knowns")

    knowns = tuple(
        Known(
            {
                key: tuple(value) if isinstance(value, list) else value
                for key, value in row.items()
            }
        )
        for row in entries
    )
    validate(knowns)
    return knowns


def validate(knowns: tuple[Known, ...]) -> None:
    """Enforce entry identity, treatment, evidence, and authorization invariants."""
    seen: set[str] = set()
    for known in knowns:
        missing = sorted(REQUIRED - known.values.keys())
        if missing:
            raise KnownError(f"{known.scalar('id') or '<unknown>'}: missing {', '.join(missing)}")
        known_id = known.scalar("id")
        if not ID.fullmatch(known_id):
            raise KnownError(f"{known_id}: id must use lowercase hyphen-case")
        if known_id in seen:
            raise KnownError(f"{known_id}: duplicate id")
        seen.add(known_id)
        if known.scalar("kind") not in KINDS:
            raise KnownError(f"{known_id}: kind must be one of {', '.join(sorted(KINDS))}")
        treatment = known.scalar("treatment")
        if treatment not in TREATMENTS:
            raise KnownError(
                f"{known_id}: treatment must be one of {', '.join(sorted(TREATMENTS))}"
            )
        if not DATE.fullmatch(known.scalar("updated")):
            raise KnownError(f"{known_id}: updated must use YYYY-MM-DD")
        evidence = known.values["evidence"]
        assert isinstance(evidence, tuple)
        if not evidence:
            raise KnownError(f"{known_id}: evidence must contain at least one item")

        work = known.scalar("work")
        if work and work not in WORK_STATES:
            raise KnownError(
                f"{known_id}: work must be one of {', '.join(sorted(WORK_STATES))}"
            )
        if treatment == "remediate":
            if not known.scalar("repair"):
                raise KnownError(f"{known_id}: remediate requires repair")
            if work == "done":
                raise KnownError(f"{known_id}: remediate work cannot be done")
        elif treatment == "monitor":
            if not known.scalar("reconsider-when"):
                raise KnownError(f"{known_id}: monitor requires reconsider-when")
            if work:
                raise KnownError(f"{known_id}: monitor must not authorize work")
        elif treatment == "accept":
            if work:
                raise KnownError(f"{known_id}: accept must not authorize work")
        elif treatment == "resolved":
            if not known.scalar("verification"):
                raise KnownError(f"{known_id}: resolved requires verification")
            if work and work != "done":
                raise KnownError(f"{known_id}: resolved work must be done")


def select(knowns: tuple[Known, ...], view: str) -> list[Known]:
    if view == "backlog":
        return sorted(
            (known for known in knowns if known.scalar("work") in {"backlog", "in-progress"}),
            key=lambda known: known.scalar("id"),
        )
    treatment = {"watchlist": "monitor", "accepted": "accept", "resolved": "resolved"}[view]
    return sorted(
        (known for known in knowns if known.scalar("treatment") == treatment),
        key=lambda known: known.scalar("id"),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and query development knowns.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="validate the canonical registry")
    mode.add_argument("--list", choices=sorted(VIEWS), help="print one read-only derived view")
    args = parser.parse_args(argv)

    try:
        knowns = load(ROOT / REGISTRY)
    except KnownError as error:
        print(f"FAIL {REGISTRY} - {error}")
        return 1
    if args.check:
        print(f"OK   {REGISTRY} ({len(knowns)} known(s))")
        return 0
    assert args.list is not None
    matches = select(knowns, args.list)
    for known in matches:
        suffix = f" [{known.scalar('work')}]" if known.scalar("work") else ""
        print(f"{known.scalar('id')}{suffix}: {known.scalar('statement')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
