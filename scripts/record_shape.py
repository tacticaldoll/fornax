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

from outcome import paired

from diagnostic_text import printable
from markdown_links import heading_section, marked_code_blocks, table_rows
from read_whole import Unread, whole

ROOT = Path(__file__).resolve().parent.parent

CONTRACT = Path("skills/triage-findings/SKILL.md")
RECORDS = Path("docs/dispositions")
MARKER = "<!-- OUTPUT-TEMPLATE: disposition-record@1 text/markdown -->"

INTEGRITY = "Record integrity"
DISPOSITIONS = "Dispositions"
RESULT = "Result"

# The contract declares a Result as one of its three values, optionally followed by `, `
# and a qualifier saying why. Both halves matter and one was missing: the domain was
# tested with `startswith`, which is a prefix and not a read, so `passenger`,
# `mismatchable` and `not claimedly` all answered clean — a well-formed value passing
# its next comparison, which is the failure `AGENTS.md` names where it says to read a
# token whole and never a prefix of it. The qualifier grammar had no definition at all,
# so one comparison carried domain membership and qualifier parsing at once and had no
# token boundary anywhere.
QUALIFIER = ", "

# A cell is bounded by the pipe the table defines, and GFM lets a cell hold one by
# escaping it — which the contract's own Result column does. So the split reads to a
# delimiter the construct defines and honours the construct's escape, rather than
# guessing what a cell may contain. `AGENTS.md` is explicit that a reading of this kind
# needs no owning parser; inventing a terminator list is what does.


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
        paired(
            self._shape, self.reason,
            "declared holds the contract's shape or a reason, never both or neither",
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


@dataclass(frozen=True)
class Table:
    """One Markdown table's header and body, apart.

    Apart because every caller wanted the body and got a list whose first element was
    the header, so each skipped it by the same index and the concept had no name. Worse,
    a caller then read the Result by `[-1]` — the last cell of whatever the row happened
    to hold — so a row written without its trailing pipe lost a cell and the diagnostic
    named a neighbour as the verdict. A column is found by the name the header gives it
    now, which is the only thing that survives a row of the wrong width.
    """

    header: list[str]
    body: list[list[str]]

    def column(self, row: list[str], name: str) -> str | None:
        """One row's cell under the named column, or nothing when the header has none.

        The row cannot be too short. GFM inserts empty cells for a row with fewer than
        the header declares, and the parser does that before this sees it — which is why
        a row written without its optional trailing pipe carries every cell, and why the
        reader that dropped its last segment was wrong twice over. So the one way this
        answers nothing is a header that never declared the column.
        """
        if name not in self.header:
            return None
        return row[self.header.index(name)]


def table(text: str) -> Table | None:
    """The one table in *text*, header apart from body, or nothing when it holds none.

    The rows come from `markdown_links.table_rows`, which is the parser that owns the
    grammar. A reader written here instead read a backslash before any character as
    escaping it, so a legal `\\q` in a cell lost its backslash and two distinct finding
    ids collided under one; and it dropped the last segment of every row, so a row whose
    optional trailing pipe GFM permits omitting lost a cell and was reported as missing
    the column it in fact carried. Both are grammar the owner already knew.

    Which text is a table stays the caller's question: the contract's rows come from
    inside a fenced template and a record's from a heading section outside every fence.
    """
    rows = table_rows(text)
    if not rows:
        return None
    return Table(rows[0], rows[1:])


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
    declared_table = table(section)
    if declared_table is None or not declared_table.body:
        return Declared(None, f"the template's {INTEGRITY} table declares no rows")

    checks = tuple(row[0] for row in declared_table.body if row)
    domains = {
        tuple(v.strip() for v in (declared_table.column(row, RESULT) or "").split("|"))
        for row in declared_table.body
        if row
    }
    if len(domains) != 1:
        return Declared(
            None, f"the template's {INTEGRITY} rows declare differing Result domains"
        )
    return Declared(Shape(checks, domains.pop()), None)


def verdict_grammar(results: tuple[str, ...]) -> re.Pattern[str]:
    """One of the declared values, optionally qualified — built from the values, not fixed.

    Compiled from what the contract declares so a fourth value cannot appear here without
    appearing there, which is the same reason the keys are derived rather than copied. The
    qualifier is bounded by the delimiter the contract names, so this reads to a boundary
    the construct defines rather than guessing where a verdict gives out.
    """
    values = "|".join(re.escape(value) for value in results)
    return re.compile(f"(?:{values})(?:{re.escape(QUALIFIER)}.+)?")


def record_defects(path: Path, shape: Declared) -> list[Diagnostic]:
    """Every way one record's tables depart from the shape the contract declares."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []  # text hygiene owns unreadable files and reports them there

    found: list[Diagnostic] = []
    section = heading_section(text, INTEGRITY)
    integrity = table(section) if section is not None else None
    if section is not None and integrity is None:
        # A section that is there and holds no table this can read is not the same fact
        # as a record that carries no such section — one record legitimately carries
        # none. Collapsing the two would let a malformed table pass the way an unopened
        # corpus passed before it was made a failure.
        found.append(
            Diagnostic(path, f"{INTEGRITY} carries no table this can read")
        )
    if integrity is not None:
        for row in integrity.body:
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
                continue
            verdict = integrity.column(row, RESULT)
            if verdict is None:
                found.append(
                    Diagnostic(
                        path,
                        f"{INTEGRITY} declares no {RESULT} column in its header, so "
                        f"the verdict on row {row[0]!r} cannot be read",
                    )
                )
            else:
                read = whole(verdict, verdict_grammar(shape.results), "a declared verdict")
                if isinstance(read, Unread):
                    found.append(
                        Diagnostic(
                            path,
                            f"{INTEGRITY} row {row[0]!r} answers {verdict!r}, which is "
                            f"not one of {', '.join(shape.results)}, with or without a "
                            f"{QUALIFIER!r} qualifier",
                        )
                    )

    settled = heading_section(text, DISPOSITIONS)
    dispositions = table(settled) if settled is not None else None
    if dispositions is not None:
        seen: set[str] = set()
        for row in dispositions.body:
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
        return [Diagnostic(records, f"{RECORDS.as_posix()} is not a directory")]
    found = sorted(records.glob("*.md"))
    if not found:
        # A check that inspected nothing must not report what a check that inspected
        # everything reports. `check_sources` says the same about a missing interpreter,
        # and `workspace_files` about an unlistable workspace; this answered clean.
        return [Diagnostic(records, f"{RECORDS.as_posix()} holds no record to check")]
    return [
        problem for path in found for problem in record_defects(path, shape)
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
    read = len(list((root / RECORDS).glob("*.md")))
    print(printable(f"OK   record shape in {read} record(s)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
