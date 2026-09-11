#!/usr/bin/env python3
"""Hold a Disposition Record's tables to the shape its own contract declares.

The contract states a set of checks for a Record integrity table, a closed domain for
each Result, and — in more than one place, `AGENTS.md` among them — that Record integrity
audits the input while Self-check audits the record being written. All of it is prose,
and prose is what round after round of these records failed against: table after table
carried a row the contract never declared, one of them convicting a producer that was
following the contract, and that one reached the shared branch inside a record that read
as settled.

What this checks and what it cannot. A row asserts that the input claimed X, that
reconciling X against the input's own contents gives Y, and therefore a Result — three
axes, and only the third is a verdict. **This module cannot read a row's subject.** No
check decides whose conduct a sentence judges, so the closed key set is the proxy: a row
whose subject is the triager rather than the input has no seat to sit in, and that is how
a `Probe disclosure` is refused rather than by understanding it. Whether an `Input claim`
cell names a claim the input actually made has no proxy at all, and is not checked.

The keys are derived from the marked output template rather than copied here. A copy
is a second list that can disagree with the contract, which is the failure this repository
has recorded more than once — most recently as a check enumerating what an input named
instead of what the tree holds. The template became reachable when it gained its
`OUTPUT-TEMPLATE` marker; before that a table inside an unmarked fence was the reason this
check was priced as needing a parser it does not need.

**Which revision of the contract, and why that is not the current one.** Holding every
archived record to the working tree's contract was measured as the wrong reading: rewording
one declared label reported the whole corpus rather than the change, and the only exits
were editing history, an exemption list `AGENTS.md` refuses, or an unstated freeze on the
wording. So a record is judged against the contract at the commit that added it, which
`contract_revision` reads and which needs no stamp in the record — stamping would have
meant editing every archived record to repair a check about editing archived records.

A record git has never seen is the one this round is writing, and it answers to the working
tree in full. That is what keeps the check useful rather than historical.

What this stops claiming as an exception. A record settled before the template carried its
`OUTPUT-TEMPLATE` marker had no declared shape to answer to, so it is reported as unjudged
and counted, which is neither clean nor defective. The record carrying none of these
sections is the clearest case and needs no special mention: its revision declared nothing,
so the absence is derived rather than excused. A predicate written to excuse it would be
the list of files `AGENTS.md` refuses, one entry long.

Depends on `markdown_links` for CommonMark, which is what keeps a `##` inside a fenced
quotation from being read as this document's own heading. Otherwise the standard library.
"""

from __future__ import annotations

import argparse
import enum
import re
import sys
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from outcome import paired

from diagnostic_text import printable
import contract_revision
from markdown_links import (
    heading_section,
    heading_texts,
    marked_code_blocks,
    table_rows,
)
from read_whole import Unread, whole

ROOT = Path(__file__).resolve().parent.parent

CONTRACT = Path("skills/triage-findings/SKILL.md")
RECORDS = Path("docs/dispositions")
MARKER = "<!-- OUTPUT-TEMPLATE: disposition-record@1 text/markdown -->"

INTEGRITY = "Record integrity"
DISPOSITIONS = "Dispositions"
SELF_CHECK = "Self-check"
RESULT = "Result"
DISPOSITION = "Disposition"

# The contract declares a Result as one of its three values, optionally followed by `, `
# and a qualifier saying why. Both halves matter and one was missing: the domain was
# tested with `startswith`, which is a prefix and not a read, so `passenger`,
# `mismatchable` and `not claimedly` all answered clean — a well-formed value passing
# its next comparison, which is the failure `AGENTS.md` names where it says to read a
# token whole and never a prefix of it. The qualifier grammar had no definition at all,
# so one comparison carried domain membership and qualifier parsing at once and had no
# token boundary anywhere.
QUALIFIER = ", "

# The contract declares what may follow a finding's id and admits no third form, so this
# reads to a boundary the document defines rather than to one invented here. The id itself
# is the part a later round matches on across rounds.
SEPARATOR = " — "
ALTERNATIVE = ", alternative "
FINDING_KEY = re.compile(
    rf"(?P<id>[A-Z][A-Z0-9-]*)(?:{re.escape(SEPARATOR)}.+|{re.escape(ALTERNATIVE)}.+)?",
    re.S,
)


class Subject(enum.Enum):
    """Whose conduct a section's rows judge, which is what decides its key discipline.

    Measured across every record here, and the asymmetry has a reason. A row under
    `THE_INPUT` accuses a producer, so a label the contract does not declare is an
    accusation with nothing behind it and the key set closes — that seat now carries no
    undeclared row anywhere in the corpus. A row under `THIS_RECORD` judges the record
    writing it, so an extra one is an author holding themselves to more than the template
    asks: label after label across the corpus that the template never declared, among them
    commit reachability, guards-row presence and citation existence. There the declared
    labels are a floor and not a ceiling.

    `AGENTS.md` states the separation these two express — "Keep facts about the input
    apart from facts about the record being written… A self-check folded into an audit of
    the input hides which of the two failed" — and it had been prose beside two tables.
    Declaring it here is what lets it pick a rule rather than be remembered.
    """

    THE_INPUT = "the input"
    THE_FINDINGS = "the findings this round settles"
    THIS_RECORD = "this record"


@dataclass(frozen=True)
class Seat:
    """One section the contract declares, and whose conduct its rows judge.

    A declaration and not a behaviour. Its rules come from `rules_for`, derived from the
    subject rather than listed here, so a seat cannot be given the wrong discipline by
    whoever adds it — and a first sketch of this carried optional `keys`, `verdict_column`
    and `unique_column` fields, which is the shape admitting states nobody means that
    this module has been repaired for three times.
    """

    heading: str
    subject: Subject


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    message: str


@dataclass(frozen=True)
class Shape:
    """What the contract's template declares, per section that declares anything.

    `keys` maps a section's heading to the row labels the template lists under it. It was
    one tuple for one section, which is why every seat but that one had to be checked by
    hand or not at all — and the template declares labels for `Self-check` too, whose
    subject is this record rather than the input and whose discipline is therefore
    different.
    """

    keys: dict[str, tuple[str, ...]]
    #: Per seat, per column, the alternatives that column's template cell spells with
    #: `|`. Derived for every such column rather than for one, because the seats
    #: carrying a verdict declare different domains — `Record integrity` answers
    #: pass/mismatch/not claimed and `Dispositions` accept/decline/defer. It was one
    #: tuple for one column, which is why the seat with a declared domain and no domain
    #: rule went unchecked while the other was held to its. Which of these a rule reads
    #: is `rules_for`'s answer; deriving them all keeps that wiring from also having to
    #: state what the contract already says.
    domains: dict[str, dict[str, tuple[str, ...]]]


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
    def keys(self) -> dict[str, tuple[str, ...]]:
        return self.shape.keys

    @property
    def results(self) -> tuple[str, ...]:
        """The `Record integrity` verdict domain, which is the one callers named first."""
        return self.shape.domains[INTEGRITY][RESULT]


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
    """The shape the contract in *root* declares, or why it could not be read.

    Reading is this function's job; parsing is `shape_of`'s. They were one body until a
    record had to be judged against the contract revision it was settled under, which
    supplies its text from git rather than from a path — the same split
    `check_citations.prose` took, and for the same reason its docstring gives.
    """
    path = root / CONTRACT
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return Declared(None, f"{CONTRACT.as_posix()} could not be read: {error}")
    return shape_of(text)


def shape_of(text: str) -> Declared:
    """The checks and the Result domain *text*'s marked template declares."""
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

    template = marked[0].content
    section = heading_section(template, INTEGRITY)
    if section is None:
        return Declared(None, f"the template declares no {INTEGRITY} table")
    declared_table = table(section)
    if declared_table is None or not declared_table.body:
        return Declared(None, f"the template's {INTEGRITY} table declares no rows")

    results = {
        tuple(v.strip() for v in (declared_table.column(row, RESULT) or "").split("|"))
        for row in declared_table.body
        if row
    }
    if len(results) != 1:
        return Declared(
            None, f"the template's {INTEGRITY} rows declare differing {RESULT} domains"
        )
    if results == {("",)}:
        # A template whose integrity table declares no verdict column is a contract this
        # cannot read, not a domain of one empty string. Mapping the missing column to ""
        # built a shape that looked usable and then reported every record's verdict as
        # outside a domain of nothing — a misread contract answering as though the records
        # were at fault.
        return Declared(None, f"the template's {INTEGRITY} table declares no {RESULT} column")

    # Every seat's labels, not one seat's. A seat the template declares nothing for gets
    # no entry, which is how a rule asks whether the contract said anything at all.
    keys: dict[str, tuple[str, ...]] = {}
    domains: dict[str, dict[str, tuple[str, ...]]] = {}
    for seat in SEATS:
        found = heading_section(template, seat.heading)
        if found is None:
            continue
        seat_table = table(found)
        if seat_table is None or not seat_table.body:
            continue
        keys[seat.heading] = tuple(row[0] for row in seat_table.body if row)
        domains[seat.heading] = _domains(seat_table)
    return Declared(Shape(keys, domains), None)


def _domains(declared_table: "Table") -> dict[str, tuple[str, ...]]:
    """Every column whose template cell spells alternatives, and what they are.

    Read from the first row that declares any, because the template writes one row per
    kind and a later row abbreviates with a repeated-value mark. A column whose cell
    carries no `|` declares no domain and gets no entry, which is how `ValueReadWhole`
    asks whether the contract governs a column at all.
    """
    found: dict[str, tuple[str, ...]] = {}
    for row in declared_table.body:
        if not row:
            continue
        for column in declared_table.header:
            cell = declared_table.column(row, column)
            if cell is None or "|" not in cell or column in found:
                continue
            found[column] = tuple(value.strip() for value in cell.split("|"))
    return found


def verdict_grammar(results: tuple[str, ...]) -> re.Pattern[str]:
    """One of the declared values, optionally qualified — built from the values, not fixed.

    Compiled from what the contract declares so a fourth value cannot appear here without
    appearing there, which is the same reason the keys are derived rather than copied. The
    qualifier is bounded by the delimiter the contract names, so this reads to a boundary
    the construct defines rather than guessing where a verdict gives out.
    """
    values = "|".join(re.escape(value) for value in results)
    return re.compile(f"(?:{values})(?:{re.escape(QUALIFIER)}.+)?")


class Rule(ABC):
    """One contract clause, asked of one section's table.

    Yields strings and never `Diagnostic`s, so a rule cannot learn which file it is
    judging — the path belongs to the caller, for the reason `path_boundary` returns
    verdicts and never diagnostics. A rule that wants a second document is not a `Rule`
    at all; that is the trigger for a record-level abstraction this module deliberately
    does not have, because it would today hold one member.
    """

    @abstractmethod
    def defects(self, seat: "Seat", found: "Table", shape: Shape) -> Iterator[str]:
        """Every way this table departs from the clause this rule carries."""


class ClosedKeys(Rule):
    """No row may carry a label the contract does not declare for this seat."""

    def defects(self, seat: "Seat", found: "Table", shape: Shape) -> Iterator[str]:
        declared_keys = shape.keys.get(seat.heading)
        if declared_keys is None:
            return
        for row in found.body:
            if row and row[0] not in declared_keys:
                yield (
                    f"{seat.heading} carries the row {row[0]!r}, which "
                    f"{CONTRACT.as_posix()} does not declare. This table's subject is "
                    f"{seat.subject.value}; a row about anything else has no seat here"
                )


class RequiredKeys(Rule):
    """Every label the contract declares for this seat must be present.

    A floor rather than a ceiling, which is what a seat judging its own record earns: an
    extra self-check is an author holding themselves to more, and a missing one is the
    gap the contract asked them to close.
    """

    def defects(self, seat: "Seat", found: "Table", shape: Shape) -> Iterator[str]:
        declared_keys = shape.keys.get(seat.heading)
        if declared_keys is None:
            return
        present = {row[0] for row in found.body if row}
        for label in declared_keys:
            if label not in present:
                yield (
                    f"{seat.heading} answers none of {label!r}, which "
                    f"{CONTRACT.as_posix()} declares it must"
                )


@dataclass(frozen=True)
class ValueReadWhole(Rule):
    """One column's value must be a declared verdict, read whole and not by its prefix."""

    column: str

    def defects(self, seat: "Seat", found: "Table", shape: Shape) -> Iterator[str]:
        domain = shape.domains.get(seat.heading, {}).get(self.column)
        if domain is None:
            yield (
                f"{CONTRACT.as_posix()} declares no {self.column} domain for "
                f"{seat.heading}, so this rule has nothing to hold its rows to"
            )
            return
        grammar = verdict_grammar(domain)
        # One diagnostic per row: where `ClosedKeys` runs, it has already reported an
        # undeclared label and the verdict on that row is not a second finding. Where it
        # does not, the declared labels are a placeholder rather than a key set — the
        # findings seat declares the single label `id` — and skipping every row whose key
        # is not that word skipped every row there was. Asked of the wiring rather than
        # restated, so the two cannot disagree.
        closed = any(isinstance(rule, ClosedKeys) for rule in rules_for(seat.subject))
        declared_keys = shape.keys.get(seat.heading) if closed else None
        for row in found.body:
            if not row or (declared_keys is not None and row[0] not in declared_keys):
                continue
            value = found.column(row, self.column)
            if value is None:
                yield (
                    f"{seat.heading} declares no {self.column} column in its header, so "
                    f"the verdict on row {row[0]!r} cannot be read"
                )
            elif isinstance(whole(value, grammar, "a verdict"), Unread):
                yield (
                    f"{seat.heading} row {row[0]!r} answers {value!r} under "
                    f"{self.column}, which is not one of {', '.join(domain)}, with or "
                    f"without a {QUALIFIER!r} qualifier"
                )


class UniqueFirstColumn(Rule):
    """No two rows may key alike, reading each row's key whole rather than by a prefix.

    This took the text before an invented `" — "` and used it as the key. Two rows keying
    the same finding under a different separator spelling therefore compared unequal and
    the duplicate went unreported — falsified by construction, three rows keying one id
    with a plain hyphen and the check saying nothing. It is the defect `AGENTS.md` names
    where it says to read a token whole and never a prefix of it, sitting one rule away
    from `ValueReadWhole`.

    So the separator is the contract's now rather than this module's, and a cell in
    neither declared form is `Unread` and reported. That is what stops a duplicate
    hiding: a misspelled separator can no longer quietly turn a cell into its own key.
    """

    def defects(self, seat: "Seat", found: "Table", shape: Shape) -> Iterator[str]:
        seen: set[str] = set()
        for row in found.body:
            if not row:
                continue
            read = whole(row[0], FINDING_KEY, "a finding id, alone or with one declared separator")
            if isinstance(read, Unread):
                yield (
                    f"{seat.heading} row {row[0]!r} does not open with a finding id "
                    f"followed by nothing, {SEPARATOR!r} or {ALTERNATIVE!r}, so it has no "
                    f"key a later round can match"
                )
                continue
            identifier = read.match.group("id")
            if identifier in seen:
                yield f"{seat.heading} keys {identifier!r} more than once"
            seen.add(identifier)


class RecordRule(ABC):
    """One contract clause asked of a whole record rather than of one of its tables.

    Deliberately not built when `Rule` landed, on the ground that it would hold a single
    member — the malformed-table reading, which stayed inline saying so. Three clauses want
    it now: a governed section that is absent, one that appears twice, and one whose table
    cannot be read. The ground for declining is gone rather than overruled, and the third
    moves in with the other two, because an abstraction holding two of its three kinds is
    the inconsistency the decline was trying to avoid.

    Asked of one seat, and only of a seat the contract declares rows for. It used to
    take the whole record and the declared shape, and decide for itself which seats to
    range over — which `RequiredSections` did and the other two did not, so a record
    settled under a revision declaring nothing for a seat was still convicted of
    duplicating that section or of carrying an unreadable table under it. A parameter
    two of three implementations ignore is not a scope decision; it is an invitation to
    skip one. So the decision moved to `record_defects`, and the parameter went with it:
    a rule that is never handed an undeclared seat cannot judge one.

    The predecessor of that parameter is worth keeping in view. It was typed `Shape`
    while every caller handed a `Declared` satisfying the annotation by proxying two
    accessors, and the proxy ran out the moment a rule needed a third — an
    `AttributeError` where a diagnostic belonged. Passing the inner shape fixed the
    type and left the scoping unmade, which is the half this repair finishes.
    """

    @abstractmethod
    def defects(self, seat: "Seat", text: str) -> Iterator[str]:
        """Every way this record departs from the clause this rule carries, at *seat*."""


class RequiredSections(RecordRule):
    """A seat the contract declares rows for must have a section in the record.

    Requiredness is derived, not declared: the contract listing labels under a heading is
    what makes that heading owed. A `required` field on `Seat` would be a second list able
    to disagree with the template, which is the failure this module derives its keys to
    avoid — and a record predating the template's marker is never judged at all, so no
    exemption is needed for the one that carries none of these sections.
    """

    def defects(self, seat: "Seat", text: str) -> Iterator[str]:
        if heading_section(text, seat.heading) is None:
            yield (
                f"{seat.heading} is absent, and {CONTRACT.as_posix()} declares rows "
                f"for it. Deleting the section skipped every rule for a seat whose "
                f"subject is {seat.subject.value}"
            )


class OneSectionEach(RecordRule):
    """A governed heading may appear once, because only the first is ever read.

    `heading_section` answers with the first match, so a second section carrying an
    undeclared label and a verdict outside the domain was judged by nothing at all. The
    count comes from the parser that owns the grammar rather than from a scan here.
    """

    def defects(self, seat: "Seat", text: str) -> Iterator[str]:
        seen = heading_texts(text).count(seat.heading)
        if seen > 1:
            yield (
                f"{seat.heading} appears {seen} times; only "
                f"the first is read, so every later one is judged by nothing"
            )


class ReadableTable(RecordRule):
    """A governed section that is present must hold a table this can read.

    A section that is there and holds no readable table is not the same fact as a record
    carrying no such section. Collapsing the two let a malformed table pass the way an
    unopened corpus passed before it was made a failure.
    """

    def defects(self, seat: "Seat", text: str) -> Iterator[str]:
        section = heading_section(text, seat.heading)
        if section is not None and table(section) is None:
            yield f"{seat.heading} carries no table this can read"


RECORD_RULES: tuple[RecordRule, ...] = (
    RequiredSections(), OneSectionEach(), ReadableTable(),
)

SEATS = (
    Seat(INTEGRITY, Subject.THE_INPUT),
    Seat(DISPOSITIONS, Subject.THE_FINDINGS),
    Seat(SELF_CHECK, Subject.THIS_RECORD),
)


def rules_for(subject: Subject) -> tuple[Rule, ...]:
    """The rules a seat gets, derived from whose conduct its rows judge.

    Derived rather than listed against each seat, which is what makes `Subject`
    load-bearing instead of decorative: a seat added to `SEATS` cannot be given the wrong
    discipline, and changing a seat's subject changes its discipline with it. A field
    nothing reads is the debt `path_boundary.Resolved` names; this one picks the rule.
    """
    if subject is Subject.THE_INPUT:
        return (ClosedKeys(), ValueReadWhole(RESULT))
    if subject is Subject.THIS_RECORD:
        return (RequiredKeys(),)
    return (UniqueFirstColumn(), ValueReadWhole(DISPOSITION))


def record_defects(path: Path, shape: Declared) -> list[Diagnostic]:
    """Every way one record's tables depart from the shape the contract declares."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []  # text hygiene owns unreadable files and reports them there

    found: list[Diagnostic] = []
    for seat in SEATS:
        if seat.heading not in shape.keys:
            # The contract declares no rows for this seat, so it owes this record
            # nothing — not a section, not one section, and not a readable table. One
            # decision, made where every rule below has to pass through it.
            continue
        for record_rule in RECORD_RULES:
            found.extend(
                Diagnostic(path, message) for message in record_rule.defects(seat, text)
            )
        section = heading_section(text, seat.heading)
        if section is None:
            continue  # RequiredSections reported it, where the contract declares rows
        seated = table(section)
        if seated is None:
            continue  # ReadableTable reported it
        for rule in rules_for(seat.subject):
            found.extend(
                Diagnostic(path, message)
                for message in rule.defects(seat, seated, shape.shape)
            )
    return found


@dataclass(frozen=True)
class Audit:
    """What one run judged, what it could not, and every departure it found.

    `unjudged` is a field rather than a silence. A record settled under a revision whose
    contract declares no readable shape is neither clean nor defective, and reporting it
    as either is wrong — so it is counted and named in the summary. The whole reason this
    type exists is that a count nobody prints is the failure this module was repaired for
    twice.
    """

    problems: list[Diagnostic]
    judged: list[Path]
    unjudged: list[tuple[str, str]]
    history: contract_revision.Past

    @property
    def read(self) -> int:
        return len(self.judged) + len(self.unjudged)


def audit(root: Path) -> Audit:
    """Judge every record against the contract revision it was settled under.

    The working tree's contract must read and declare a shape whatever the corpus holds:
    it is the one an uncommitted record — the record the current round is writing — is
    settled against, so a broken contract now is a failure now.

    A committed record is read against its own revision instead. Before the template
    gained its `OUTPUT-TEMPLATE` marker there was no shape to declare, so a record older
    than the marker is unjudgeable rather than compliant, and says so.
    """
    working = declared(root)
    if working.reason is not None:
        broken = Diagnostic(root / CONTRACT, working.reason)
        return Audit([broken], [], [], contract_revision.past(root))
    records = root / RECORDS
    history = contract_revision.past(root)
    if not records.is_dir():
        return Audit(
            [Diagnostic(records, f"{RECORDS.as_posix()} is not a directory")], [], [], history
        )
    found = sorted(records.glob("*.md"))
    if not found:
        # A check that inspected nothing must not report what a check that inspected
        # everything reports. `check_sources` says the same about a missing interpreter,
        # and `workspace_files` about an unlistable workspace; this answered clean.
        return Audit(
            [Diagnostic(records, f"{RECORDS.as_posix()} holds no record to check")],
            [], [], history,
        )

    problems: list[Diagnostic] = []
    judged: list[Path] = []
    unjudged: list[tuple[str, str]] = []
    shapes: dict[str, Declared] = {contract_revision.WORKING_TREE: working}
    for path in found:
        settled = contract_revision.settled(root, path, CONTRACT, history)
        if settled.reason is not None:
            problems.append(Diagnostic(path, settled.reason))
            continue
        source = settled.source
        if source.where not in shapes:
            shapes[source.where] = shape_of(source.text)
        shape = shapes[source.where]
        if shape.reason is not None:
            unjudged.append((path.name, f"{shape.reason}"))
            continue
        judged.append(path)
        problems.extend(record_defects(path, shape))
    return Audit(problems, judged, unjudged, history)


def check(root: Path) -> list[Diagnostic]:
    """Every record's departures from the contract, plus a contract that will not read."""
    return audit(root).problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=None, help="Repository root to check.")
    args = parser.parse_args(argv)
    root = Path(args.root) if args.root else ROOT

    result = audit(root)
    for problem in result.problems:
        where = problem.path
        if where.is_relative_to(root):
            where = where.relative_to(root)
        print(printable(f"FAIL {where} - {problem.message}"), file=sys.stderr)
    if result.problems:
        return 1

    # The unjudged count is printed, not held. A record this could not judge is not a
    # record it found clean, and the only thing that keeps those two apart for a reader
    # is this line saying which is which.
    summary = f"OK   record shape in {len(result.judged)} of {result.read} record(s)"
    if not result.history.available:
        summary += f", all against the working tree ({result.history.why})"
    print(printable(summary))
    # Grouped by reason rather than one line per record: the corpus shares a single
    # reason today, and twenty-four identical lines would bury the count they carry.
    reasons: dict[str, int] = {}
    for _, reason in result.unjudged:
        reasons[reason] = reasons.get(reason, 0) + 1
    for reason, count in sorted(reasons.items()):
        print(printable(f"     {count} not judged: {reason}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
