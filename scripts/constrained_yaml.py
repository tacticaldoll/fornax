#!/usr/bin/env python3
"""Shared plain-scalar rules for the repository's constrained YAML readers.

The readers own their document grammars and public error types. This module owns
only the scalar syntax they deliberately share, so unsupported YAML features
cannot drift between otherwise independent parsers.

Both readers skip a whole-line comment before reaching this module, so the rule
about comments here concerns the other kind: one sharing a line with a value. YAML
would treat that as a comment and end the scalar before it; a reader that kept it
would store a value nothing else agrees on. Rejecting is the only answer that does
not silently diverge.

The anchor, alias, and tag rule tests the first character only, because that is
the one position where YAML reads &, * or ! as a node property. Anywhere else they
are ordinary text, and a wider rule would refuse prose the registry needs.

The block-scalar rule tests the first character for the same reason, and it has to.
Comparing the whole value against "|" and ">" caught only a bare indicator: a
chomping or indentation indicator makes the header "|-", ">-" or "|2", and each of
those was stored as the field's value — a registry statement reading ">-" while a
real YAML parser reads a folded scalar there. YAML forbids an indicator as a plain
scalar's first character, so nothing legitimate is refused by this; a value that
must begin with one cannot be expressed in this subset at all, which quoting would
not fix either.
"""

from __future__ import annotations

import re
from typing import Callable


ErrorFactory = Callable[[str], ValueError]


def raw_scalar(value: str, number: int, error_factory: ErrorFactory) -> str:
    """Return one supported raw scalar or raise the caller's public error type."""
    if not value:
        raise error_factory(f"line {number}: scalar must not be empty")
    if value[0] in "'\"[{":
        raise error_factory(f"line {number}: quoted and flow-style scalars are unsupported")
    if value[0] in "|>":
        raise error_factory(f"line {number}: multiline scalars are unsupported")
    if re.search(r"(?:^|\s)#", value):
        raise error_factory(f"line {number}: comments are unsupported")
    if value[0] in "&*!":
        raise error_factory(f"line {number}: YAML anchors, aliases, and tags are unsupported")
    return value
