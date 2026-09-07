#!/usr/bin/env python3
"""Read a contract as it stood when a record was settled against it.

A check that holds a record to a contract has to choose which revision of the contract
it means, and holding every archived record to the one in the working tree was measured
as the wrong answer: rewording a single declared label reported the whole corpus rather
than the change, and the only exits were editing history, an exemption list `AGENTS.md`
refuses, or an unstated freeze on the contract's wording. This repository took the first
of those once, for one record, which is the finding this module answers.

So a record settled in the past is read against the past. Which past needs no stamp in
the record — git already knows, from the commit that added the file — and that matters
beyond convenience: stamping would have meant editing every archived record to repair a
check about editing archived records.

Three states, and the middle one is the important one.

- A record git has never seen is being written **now**, so the working tree's contract is
  the one it is settled against. This is the record each round produces, and it is held to
  the current wording in full.
- A record with an adding commit is read against the contract at that commit.
- A root with no history at all — a release tarball, a `git archive` export, a test's
  temporary directory — has no past to read, and its contract and its records are one
  snapshot. Holding them to that snapshot is the strict answer rather than a skip, and the
  caller is told which reason applied so a silent fallback cannot pass for a reading.

`workspace_files.listed` is the precedent for the last of those: a check must not read an
unlistable workspace as an empty one, and the difference here is only that a historyless
snapshot is a legitimate thing to be pointed at rather than a failure.

Standard library only.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from outcome import paired

WORKING_TREE = "the working tree"


@dataclass(frozen=True)
class Source:
    """A contract's text, and which revision it was read from.

    One value rather than two fields on `Settled`, because they travel together and
    `outcome.paired` answers about one payload. `record_shape.Declared` was repaired for
    exactly the shape this avoids: two payload fields under a guard that ranged over the
    first alone.
    """

    text: str
    where: str


@dataclass(frozen=True)
class Past:
    """Whether this root carries history, and which reason it does not.

    `why` is set only when there is no history, and it is not an error field. An export
    legitimately has none; what would be a defect is answering as though a reading had
    happened, so the reason travels to the caller and into its summary line.
    """

    available: bool
    why: str | None = None


@dataclass(frozen=True)
class Settled:
    """The contract a record was settled against, or why it could not be read."""

    _source: Source | None
    reason: str | None

    def __post_init__(self) -> None:
        paired(
            self._source, self.reason,
            "settled holds the contract it was read from or a reason, never both or neither",
        )

    @property
    def source(self) -> Source:
        if self._source is None:
            raise ValueError(self.reason or "")
        return self._source


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True, capture_output=True, text=True,
    )


def past(root: Path) -> Past:
    """Whether *root* is a worktree git can be asked about.

    Asked once for a corpus rather than once per record, and answered before any lookup,
    so a historyless root reads its contract once instead of failing a lookup per record.
    """
    try:
        inside = _git(root, "rev-parse", "--is-inside-work-tree").stdout.strip()
    except FileNotFoundError:
        return Past(False, "git is not on PATH")
    except (OSError, subprocess.CalledProcessError):
        return Past(False, "the root is not a git worktree")
    if inside != "true":
        return Past(False, "the root is not a git worktree")
    return Past(True)


def settled(root: Path, record: Path, contract: Path, history: Past) -> Settled:
    """The contract *record* was settled against, read from the revision that adds it."""
    if not history.available:
        return _working_tree(root, contract)

    relative = record.relative_to(root).as_posix()
    try:
        adding = _git(
            root, "log", "--diff-filter=A", "--format=%h", "--", relative
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError) as error:
        return Settled(None, f"git could not be asked which commit added {relative}: {error}")

    if not adding:
        return _working_tree(root, contract)

    # The oldest, which is the commit that first added the file: `git log` answers newest
    # first, and a path deleted and restored carries more than one addition.
    commit = adding[-1]
    try:
        text = _git(root, "show", f"{commit}:{contract.as_posix()}").stdout
    except (OSError, subprocess.CalledProcessError) as error:
        return Settled(
            None, f"{contract.as_posix()} could not be read at {commit}: {error}"
        )
    return Settled(Source(text, commit), None)


def _working_tree(root: Path, contract: Path) -> Settled:
    try:
        text = (root / contract).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return Settled(None, f"{contract.as_posix()} could not be read: {error}")
    return Settled(Source(text, WORKING_TREE), None)
