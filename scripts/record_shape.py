#!/usr/bin/env python3
"""Hold a Disposition Record's tables to the shape its own contract declares.

The contract states five checks for a Record integrity table, a three-value domain for
each Result, and — in two places, plus a third in `AGENTS.md` — that Record integrity
audits the input while Self-check audits the record being written. All of it is prose,
and prose is what a round after round of these records failed against: four tables
carried a sixth row, one of them convicting a producer that was following the contract,
and that one reached the shared branch inside a record that read as settled.

What this checks and what it cannot. A row asserts that the input claimed X, that
reconciling X against the input's own contents gives Y, and therefore a Result — three
axes, and only the third is a verdict. **This module cannot read a row's subject.** No
check decides whose conduct a sentence judges, so the closed key set is the proxy: a row
whose subject is the triager rather than the input has no seat to sit in, and that is how
a `Probe disclosure` is refused rather than by understanding it. Whether an `Input claim`
cell names a claim the input actually made has no proxy at all, and is not checked.

The five keys are derived from the marked output template rather than copied here. A copy
is a second list that can disagree with the contract, which is the failure this repository
has recorded more than once — most recently as a check enumerating what an input named
instead of what the tree holds. The template became reachable when it gained its
`OUTPUT-TEMPLATE` marker; before that a table inside an unmarked fence was the reason this
check was priced as needing a parser it does not need.

The rule applies to a section that exists. One record carries no Record integrity table at
all — the round recorded as accepted debt in `development-knowns.yaml`, whose Review
Record was never persisted — and a predicate covering that costs nothing, where a list of
files it does not apply to is the shape `AGENTS.md` refuses.

Depends on `markdown_links` for CommonMark, which is what keeps a `##` inside a fenced
quotation from being read as this document's own heading. Otherwise the standard library.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from diagnostic_text import printable
from markdown_links import heading_section, marked_code_blocks

ROOT = Path(__file__).resolve().parent.parent

CONTRACT = Path("skills/triage-findings/SKILL.md")
RECORDS = Path("docs/dispositions")
MARKER = "<!-- OUTPUT-TEMPLATE: disposition-record@1 text/markdown -->"

INTEGRITY = "Record integrity"
DISPOSITIONS = "Dispositions"

# A cell is bounded by the pipe the table defines, and GFM lets a cell hold one by
# escaping it — which the contract's own Result column does. So the split reads to a
# delimiter the construct defines and honours the construct's escape, rather than
# guessing what a cell may contain. `AGENTS.md` is explicit that a reading of this kind
# needs no owning parser; inventing a terminator list is what does.
CELL = re.compile(r"(?<!\\)\|")
SEPARATOR = re.compile(r"^[\s:|-]+$")


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    message: str


@dataclass(frozen=True)
class Shape:
    """The two things the contract's template declares about a Record integrity table."""

    checks: tuple[str, ...]
    results: tuple[str, ...]


@dataclass(frozen=True)
class Declared:
    """The shape the contract declares, or why it could not be read.

    Never both and never neither, for the reason `skill_yaml.Document`,
    `path_boundary.Boundary`, `check_citations.Symbols` and
    `evidence_currency.Fingerprint` all carry: a caller that cannot tell an unread
    contract from an empty one reports the wrong thing, and here it would report every
    record as carrying an undeclared key.

    One payload, which the first version of this type did not have. It held the checks
    and the Result domain as two fields and the guard ranged over the first alone, so
    `Declared(("a",), None, None)` was a state the type admitted and no code meant.
    Reading `.results` there did the right thing with nothing to say: the accessor
    correctly found its own field empty and raised the reason, and the reason was `None`
    because the guard that would have required one had not run — an exception with an
    empty message. The four types above each hold exactly one payload, which is why
    their single guard is complete; copying their shape for two fields copied the guard
    and not the completeness. `Shape` makes the pair one payload again, which is also
    what lets this type call a shared predicate at all.
    """

    _shape: "Shape | None"
    reason: str | None

    def __post_init__(self) -> None:
        if (self._shape is None) == (self.reason is None):
            raise ValueError(
                "declared holds the contract's shape or a reason, never both or neither"
            )

    @property
    def shape(self) -> "Shape":
        if self._shape is None:
            raise ValueError(self.reason or "")
        return self._shape

    @property
    def checks(self) -> tuple[str, ...]:
        return self.shape.checks

    @property
    def results(self) -> tuple[str, ...]:
        return self.shape.results


def rows(text: str) -> list[list[str]]:
    """Every table row in *text*, as its cells, separator rows dropped.

    Given text rather than a document, because which text is a table is the caller's
    question: the contract's rows come from inside a fenced template and a record's come
    from a heading section outside every fence. A reader that decided for both would
    answer one of them wrongly.
    """
    found = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or SEPARATOR.match(stripped):
            continue
        cells = [c.replace("\\|", "|").strip() for c in CELL.split(stripped)]
        found.append([c for c in cells[1:-1]] if len(cells) > 2 else [])
    return found


def declared(root: Path) -> Declared:
    """The checks and the Result domain the contract's template declares."""
    path = root / CONTRACT
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return Declared(None, f"{CONTRACT.as_posix()} could not be read: {error}")
    # Taken from the parser rather than by splitting on the marker string. The template
    # sits inside a fence, so `heading_section` over the raw text finds nothing — a `###`
    # inside a fenced block is not a heading, which is the property that keeps an archived
    # record's quoted headings out of every reading here. `marked_code_blocks` hands back
    # the fence's content, where those headings are the template's own.
    marked = [b for b in marked_code_blocks(text) if b.marker == MARKER]
    if not marked:
        return Declared(None, f"{CONTRACT.as_posix()} carries no {MARKER}")
    if len(marked) > 1:
        return Declared(None, f"{CONTRACT.as_posix()} marks more than one such template")

    section = heading_section(marked[0].content, INTEGRITY)
    if section is None:
        return Declared(None, f"the template declares no {INTEGRITY} table")
    table = rows(section)
    if len(table) < 2:
        return Declared(None, f"the template's {INTEGRITY} table declares no rows")

    body = table[1:]
    checks = tuple(row[0] for row in body if row)
    domains = {tuple(v.strip() for v in row[-1].split("|")) for row in body if len(row) > 1}
    if len(domains) != 1:
        return Declared(None, f"the template's {INTEGRITY} rows declare differing Result domains"
        )
    return Declared(Shape(checks, domains.pop()), None)


def record_defects(path: Path, shape: Declared) -> list[Diagnostic]:
    """Every way one record's tables depart from the shape the contract declares."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []  # text hygiene owns unreadable files and reports them there

    found: list[Diagnostic] = []
    section = heading_section(text, INTEGRITY)
    if section is not None:
        for row in rows(section)[1:]:
            if not row:
                continue
            if row[0] not in shape.checks:
                found.append(
                    Diagnostic(
                        path,
                        f"{INTEGRITY} carries the row {row[0]!r}, which "
                        f"{CONTRACT.as_posix()} does not declare. The table's subject is the "
                        "input's own claims; a row about anything else has no seat here",
                    )
                )
            elif len(row) > 1 and not any(row[-1].startswith(v) for v in shape.results):
                found.append(
                    Diagnostic(
                        path,
                        f"{INTEGRITY} row {row[0]!r} answers {row[-1]!r}, which begins with "
                        f"none of {', '.join(shape.results)}",
                    )
                )

    settled = heading_section(text, DISPOSITIONS)
    if settled is not None:
        seen: set[str] = set()
        for row in rows(settled)[1:]:
            if not row:
                continue
            identifier = row[0].split(" — ")[0].strip()
            if identifier in seen:
                found.append(
                    Diagnostic(path, f"{DISPOSITIONS} keys {identifier!r} more than once")
                )
            seen.add(identifier)
    return found


def check(root: Path) -> list[Diagnostic]:
    """Every record's departures from the contract, plus a contract that will not read."""
    shape = declared(root)
    if shape.reason is not None:
        return [Diagnostic(root / CONTRACT, shape.reason)]
    records = root / RECORDS
    if not records.is_dir():
        return []
    return [
        problem
        for path in sorted(records.glob("*.md"))
        for problem in record_defects(path, shape)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=None, help="Repository root to check.")
    args = parser.parse_args(argv)
    root = Path(args.root) if args.root else ROOT

    problems = check(root)
    for problem in problems:
        where = problem.path
        if where.is_relative_to(root):
            where = where.relative_to(root)
        print(printable(f"FAIL {where} - {problem.message}"), file=sys.stderr)
    if problems:
        return 1
    print(printable(f"OK   record shape in {len(sorted((root / RECORDS).glob('*.md')))} record(s)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
