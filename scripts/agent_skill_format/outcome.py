#!/usr/bin/env python3
"""Own the one predicate five types in this directory had each written by hand.

A reader here answers with what it read or with why it could not, never both and never
neither, and the types carrying that pair all guard it the same way. Five of them had
written the guard out: `skill_yaml.Document`, `path_boundary.Boundary`,
`check_citations.Symbols`, `evidence_currency.Fingerprint` and `record_shape.Declared`.

The fifth is why this module exists rather than the first four. It was written last, from
the shape of its siblings rather than from a shared function, and it diverged twice in one
type: the guard was spelled differently from all four it named as its model, and it ranged
over one of two payload fields, so a state the type denied was constructible and the
accessor for the missing field raised with an empty message. The argument that five copies
are safe because they have held was an argument from a sample that excluded the next copy,
and the next copy is what a new module always writes.

So what is owned here is the predicate and nothing else, because the predicate is the only
thing the five share. Their accessors do not: `skill_yaml.Document.require` raises its
module's own `Unreadable`, three raise `ValueError`, and `path_boundary.Boundary` has no
raising accessor at all. A shared accessor would have to take an error factory the way
`constrained_yaml.raw_scalar` does, and no defect has ever occurred in one of them — so
that divergence is recorded rather than unified on speculation.

`paired` takes the message rather than supplying it. Each site's sentence says what its
own pair means — "a boundary holds a resolved root or the failure" tells a reader what
"exactly one state required" does not — and a shared owner that flattened them would trade
a real diagnostic for a line of code.

**Every implementation of this behaviour, and where each one stands.** `AGENTS.md` asks
for the enumeration and not only the extraction, because a participant left outside a new
owner without a record has been a defect here more than once.

Routed through it: the five types above.

Outside it, each for its own reason and none by exemption:

- `path_boundary.Resolved` carries a verdict and an optional error and **no payload** —
  the resolved path is deliberately absent — so there is no pair to guard.
- `read_whole.Whole` guards a different invariant: that a match spans the whole of its
  subject. `Whole | Unread` is a union rather than a pair of optional fields.
- `skill_yaml.ListRead` and `ScalarRead` are **three-state** through `skill_yaml.Shape`,
  and carry no reason field at all; presence is implied by the shape. `check_text.Bytes`
  is the same, through `check_text.Content`.
- `workspace_files.listed`, `check_sources.yaml_documents`,
  `distribution_manifest.read_json_object` and `validate_skills.child_directories` answer
  with a `tuple` rather than a type, so they have no `__post_init__` to share. They admit
  the states this predicate refuses — `(None, None)` is constructible in each — and that
  is worth recording: no defect has occurred there, and converting four signatures and
  their callers on that basis would be a wide change driven by nothing measured. They are
  the first candidates if one does.

Standard library only.
"""

from __future__ import annotations


def paired(payload: object | None, reason: object | None, message: str) -> None:
    """Refuse a payload-or-reason pair that holds both or neither.

    Called from a frozen dataclass's `__post_init__`, where returning normally is the
    whole of the success case. It answers about one payload: a type carrying two fields
    that travel together cannot be handed here, which is the signal to make them one
    value rather than to widen this.
    """
    if (payload is None) == (reason is None):
        raise ValueError(message)
