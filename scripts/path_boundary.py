#!/usr/bin/env python3
"""Resolve a candidate path and decide whether it stays inside a declared boundary.

Several checks in this repository read paths they do not control: a Markdown link
destination, a git index entry, a manifest field. Each needs the same three facts —
can the path be resolved, does it stay inside the root that reader declares, and is
anything actually there — and each answers to a different root, phrases its own
diagnostic, and disagrees about severity. A tracked file missing from the working
tree is a deletion git already reports; a missing link target is a defect.

So this module returns facts and never diagnostics, never severity, and never a
judgement about what kind of file the target is. Callers map a verdict to their own
message, which is what keeps the two validators independently runnable with distinct
scopes and wording. Standard library only.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from pathlib import Path


class Verdict(enum.Enum):
    """What resolving one candidate against one boundary established."""

    UNRESOLVABLE = "unresolvable"
    OUTSIDE = "outside"
    ABSENT = "absent"
    INSIDE = "inside"


@dataclass(frozen=True)
class Boundary:
    """A root already resolved, so a loop over many candidates resolves it once."""

    root: Path

    @classmethod
    def at(cls, root: Path) -> "Boundary":
        return cls(root.resolve())


@dataclass(frozen=True)
class Resolved:
    """One verdict, the resolved path when there is one, and the resolution error."""

    verdict: Verdict
    path: Path | None = None
    error: Exception | None = None


def resolve_within(candidate: Path, boundary: Boundary) -> Resolved:
    """Classify one candidate path against one boundary.

    The order is part of the contract. Resolution failure comes first because
    nothing else is knowable without it. Containment comes before existence so that
    a path which both escapes and is missing reads as an escape — calling it "not
    found" would send the reader to the wrong problem. Existence is asked of the
    resolved target, which is why a symlink pointing inside the boundary at nothing
    is ABSENT rather than INSIDE.
    """
    try:
        resolved = candidate.resolve()
    except (OSError, RuntimeError) as error:
        return Resolved(Verdict.UNRESOLVABLE, error=error)

    if not resolved.is_relative_to(boundary.root):
        return Resolved(Verdict.OUTSIDE, resolved)

    if not resolved.exists():
        return Resolved(Verdict.ABSENT, resolved)

    return Resolved(Verdict.INSIDE, resolved)
