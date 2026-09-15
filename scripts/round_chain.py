#!/usr/bin/env python3
"""Check that each round record names the round before it.

A round's range is a base and the head it reviewed, and those ranges do not tile:
one stretch of this history starts from the release tag, a later one from the
previous settle commit, so consecutive ranges overlap and a commit outside all of
them is not by itself a hole. `AGENTS.md` says so under Testing Strategy, and says
what carries the chain instead — the `Prior round` field.

That field is what drifted with nothing to catch it. One record named a round other
than its neighbour, and every id the skipped rounds had left open lost its lifecycle
home: no later record mentions them, and the record that skipped them declared an
older round's open set out of scope in their place. The ledger had no other way to
notice, because a record's own text is the only place the chain was written.

Neither grammar here is guessed. Git owns revision syntax and is asked to resolve
each half of a record's name; `markdown-it-py` owns the field, read as the inline
code following a `Prior round` emphasis. What is left is this repository's own file
naming, read whole through `read_whole.whole` so a name this cannot read is reported
rather than shortened into one it can.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from agent_skill_format.read_whole import Unread, Whole, whole
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
RECORDS = Path("docs/dispositions")
BRANCH = "main"
FIELD = "Prior round"

#: The one declared exception. A second reading settles the range it re-reads in the
#: same turn, so it names that record rather than its chronological neighbour, and the
#: round after it names the first reading. Written as the single suffix the naming
#: admits rather than as a shape any suffix could satisfy: inventing a terminator is
#: what reopens a hole, and this one is enumerable.
SECOND_READING = "second-reading"
RECORD_NAME = re.compile(
    r"(?P<base>[^.]+(?:\.[^.]+)*?)\.\.(?P<head>[^.]+?)"
    rf"(?:\.(?P<suffix>{SECOND_READING}))?\.md"
)

PARSER = MarkdownIt("commonmark")


@dataclass(frozen=True)
class Record:
    """One round record, named for the range it settled."""

    name: str
    base: str
    head: str
    second_reading: bool
    prior: str | None


@dataclass(frozen=True)
class Unresolved:
    """A revision this repository resolves to no commit at all."""

    revision: str

    def __str__(self) -> str:
        return f"{self.revision}, which this repository resolves to no commit"


@dataclass(frozen=True)
class OffBranch:
    """A revision that resolves, to a commit the reviewed branch does not hold."""

    revision: str
    name: str

    def __str__(self) -> str:
        return f"{self.revision}, which {BRANCH} does not hold"


#: A place on the branch, or the reason there is none. The two absences are separate
#: types because they call for different repairs and the caller has to say which it
#: met: a name nothing resolves is a record naming a revision that was never written,
#: and one the branch does not hold is a record naming a revision written elsewhere.
#: Collapsing them reported the first as the second, which sent a reader looking on the
#: branch for something no branch has.
Placed = int | Unresolved | OffBranch


@dataclass(frozen=True)
class History:
    """Where each written revision sits on the branch the rounds reviewed."""

    #: Full object name of every commit on the branch, mapped to its distance from
    #: that branch's head.
    order: Mapping[str, int]
    #: What each written revision resolves to, absent when nothing resolves it.
    resolved: Mapping[str, str]

    def name_of(self, revision: str) -> str:
        """The commit a written revision resolves to, or a tag that resolves to nothing.

        An unresolved revision is tagged rather than returned as itself, so it can
        equal another record that wrote it the same way and can never equal a commit.
        Falling back to the written text would put the textual comparison back one
        level down, where nothing would name it.
        """
        resolved = self.resolved.get(revision)
        return resolved if resolved is not None else f"unresolved:{revision}"

    def identity(self, record: "Record") -> tuple[str, str]:
        """The pair of commits a record settles, resolved rather than as written."""
        return (self.name_of(record.base), self.name_of(record.head))

    def place(self, revision: str) -> Placed:
        name = self.resolved.get(revision)
        if name is None:
            return Unresolved(revision)
        position = self.order.get(name)
        if position is None:
            return OffBranch(revision, name)
        return position


def _git(root: Path, *arguments: str) -> str | None:
    result = subprocess.run(
        ["git", *arguments], cwd=root, capture_output=True, text=True, check=False
    )
    return None if result.returncode else result.stdout.strip()


def read_record(name: str, text: str) -> Record | Unread:
    """Read one record's name and the round it points at, or report it unread."""
    read = whole(name, RECORD_NAME, "a round record name")
    if isinstance(read, Unread):
        return read
    assert isinstance(read, Whole)
    parts = read.match
    return Record(
        name=name,
        base=parts.group("base"),
        head=parts.group("head"),
        second_reading=parts.group("suffix") is not None,
        prior=prior_field(text),
    )


def prior_field(text: str) -> str | None:
    """The record `Prior round` names, taken from the parser that owns the markup.

    The whole path is kept. Reducing it to the last segment made a field naming a
    record under another directory compare equal to one naming a disposition, so the
    chain would have accepted a pointer into a directory it does not run through.
    """
    for token in PARSER.parse(text):
        if token.type != "inline" or not token.children:
            continue
        children = token.children
        for index, child in enumerate(children):
            if child.type != "strong_open":
                continue
            label = children[index + 1] if index + 1 < len(children) else None
            if label is None or label.content != FIELD:
                continue
            for follower in children[index + 2 :]:
                if follower.type == "code_inline":
                    return PurePosixPath(follower.content).as_posix()
    return None


def read_history(root: Path, records: list[Record]) -> History | str:
    """Resolve every record's head against the branch, or say why it cannot be."""
    listed = _git(root, "rev-list", BRANCH)
    if listed is None:
        return f"cannot list {BRANCH}; this check needs the reviewed branch"
    order = {name: position for position, name in enumerate(listed.split())}
    resolved = {}
    for record in records:
        for revision in (record.base, record.head):
            if revision in resolved:
                continue
            name = _git(root, "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}")
            if name is not None:
                resolved[revision] = name
    return History(order=order, resolved=resolved)


def neighbours(records: list[Record], history: History) -> list[tuple[Record, Record]]:
    """Pair each round with the round before it, second readings left out of the chain.

    A second reading settles the range it re-reads, in the same turn, so it is part of
    that round rather than a round of its own — and the chain runs between rounds. The
    records say so themselves: every round following a second reading names the first
    reading, not the second, and one second reading has no first reading kept beside it
    at all. Sorting them into the chain instead produced a failure against each of those
    rounds, which is the ordering being wrong rather than the records.

    So their own field is not read either. The two kept here disagree about what a second
    reading points at — one names the round before the range, one names the reading it
    re-reads — and nothing downstream consumes either, so this reports neither.
    """
    placed = {
        record.name: history.place(record.head)
        for record in records
        if not record.second_reading
    }
    rounds = [record for record in records if isinstance(placed.get(record.name), int)]
    ordered = sorted(rounds, key=lambda record: -placed[record.name])
    return list(zip(ordered, ordered[1:]))


def names_for(
    round_record: Record, records: list[Record], history: History
) -> set[str]:
    """Every path a later round may write to name *round_record*, second readings included.

    A range read twice is settled by more than one record, and the records disagree
    about which of them a later round should name: some name the reading, one names
    the second reading. Both name the same round, so both identify it, and the
    disagreement is a spelling this accepts rather than a drift to report. Choosing
    one spelling instead would have failed rounds whose field was never wrong —
    a rule manufacturing findings against records that kept the convention they had.

    Which records settle one round is asked of `History.identity` rather than of the
    text: git already resolved every half of every name for the placement above, and
    comparing the written halves beside that resolver made one range spelled two ways
    two rounds.
    """
    settled = history.identity(round_record)
    return {
        PurePosixPath(RECORDS / other.name).as_posix()
        for other in (round_record, *records)
        if other.name == round_record.name
        or (other.second_reading and history.identity(other) == settled)
    }


def report(failures: list[str]) -> int:
    """The one exit: every failure found, whatever stopped the run from finding more."""
    for failure in failures:
        print(failure, file=sys.stderr)
    if failures:
        return 1
    print("OK   round chain")
    return 0


def check(root: Path = ROOT) -> int:
    """Report every record whose `Prior round` is not the round before it."""
    directory = root / RECORDS
    records: list[Record] = []
    failures: list[str] = []
    for path in sorted(directory.glob("*.md")):
        read = read_record(path.name, path.read_text(encoding="utf-8"))
        if isinstance(read, Unread):
            failures.append(f"FAIL {RECORDS}/{read.text} {read.reason}")
            continue
        records.append(read)
    history = read_history(root, records)
    if isinstance(history, str):
        # Reported through the one exit below rather than returned from here. The
        # records this already failed to read were collected above, and returning at
        # this point dropped every one of them: the run that could say least about the
        # tree was also the run that said least about what it had already found.
        failures.append(f"FAIL round chain - {history}")
        return report(failures)
    for record in records:
        placed = history.place(record.head)
        if not isinstance(placed, int):
            failures.append(f"FAIL {RECORDS}/{record.name} reviewed {placed}")
    for earlier, later in neighbours(records, history):
        accepted = names_for(earlier, records, history)
        if later.prior not in accepted:
            failures.append(
                f"FAIL {RECORDS}/{later.name} names {later.prior} as the round before "
                f"it; the round before it is {earlier.name}"
            )
    return report(failures)


if __name__ == "__main__":
    raise SystemExit(check())
