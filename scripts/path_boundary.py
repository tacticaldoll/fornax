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
    """A root resolved once, or the failure that resolving it produced.

    Resolving a root can fail for the same reasons resolving a candidate can, so it
    would be incoherent for one to be a fact and the other an exception. The callers
    showed why it matters: one caught OSError but not RuntimeError, the other guarded
    nothing at all. A failed root is remembered instead, and every candidate measured
    against it comes back UNRESOLVABLE carrying the root's own error.
    """

    root: Path | None
    error: Exception | None = None

    @classmethod
    def at(cls, root: Path) -> "Boundary":
        try:
            return cls(root.resolve())
        except (OSError, RuntimeError) as error:
            return cls(None, error)


@dataclass(frozen=True)
class Resolved:
    """One verdict, plus the resolution error when there was one.

    The resolved path is deliberately not carried. No caller needs it, and a field
    nothing reads is the same debt as a capability nobody calls. Add it back when a
    diagnostic actually wants to name the target it resolved to.
    """

    verdict: Verdict
    error: Exception | None = None


def resolve_within(candidate: Path, boundary: Boundary) -> Resolved:
    """Classify one candidate path against one boundary.

    The order is part of the contract. Resolution failure comes first because
    nothing else is knowable without it. Containment comes before existence so that
    a path which both escapes and is missing reads as an escape — calling it "not
    found" would send the reader to the wrong problem. Existence is asked of the
    resolved target, which is why a symlink pointing inside the boundary at nothing
    is ABSENT rather than INSIDE. A boundary that could not be resolved at all comes
    ahead of even that: nothing can be inside a root that does not resolve.
    """
    if boundary.root is None:
        return Resolved(Verdict.UNRESOLVABLE, boundary.error)

    try:
        resolved = candidate.resolve()
    except (OSError, RuntimeError) as error:
        return Resolved(Verdict.UNRESOLVABLE, error)

    if not resolved.is_relative_to(boundary.root):
        return Resolved(Verdict.OUTSIDE)

    if not resolved.exists():
        return Resolved(Verdict.ABSENT)

    return Resolved(Verdict.INSIDE)
