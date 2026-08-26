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

A double-quoted scalar is admitted, and its content is read by the parser rather
than unquoted here. The subset refused every quote, which left it unable to express
values its own files needed: YAML forbids ": " inside a plain scalar, and both
registries carried some — a heading named "Gate 5: Responsibility & Boundaries",
prose reading "settle it: the ...". They were stored as written and no YAML parser
could read either file, which is the divergence the paragraph above says this module
exists to prevent, in the files it was written for. Single-quoted and flow scalars
stay refused: one quoting style is enough to express anything, and each extra style
is another grammar to agree on.

A plain scalar carrying ": " is refused for the same reason it caused: YAML would
end the key there and this reader would not, so the value would be one nothing else
agrees on. Quoting is how such a value is written now, and there is a way to write
it, which there was not before.

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

import yaml


ErrorFactory = Callable[[str], ValueError]


def raw_scalar(value: str, number: int, error_factory: ErrorFactory) -> str:
    """Return one supported raw scalar or raise the caller's public error type."""
    if not value:
        raise error_factory(f"line {number}: scalar must not be empty")
    if value[0] == '"':
        return _double_quoted(value, number, error_factory)
    if value[0] in "'[{":
        raise error_factory(
            f"line {number}: single-quoted and flow-style scalars are unsupported"
        )
    if value[0] in "|>":
        raise error_factory(f"line {number}: multiline scalars are unsupported")
    if re.search(r"(?:^|\s)#", value):
        raise error_factory(f"line {number}: comments are unsupported")
    if value[0] in "&*!":
        raise error_factory(f"line {number}: YAML anchors, aliases, and tags are unsupported")
    if ": " in value or value.endswith(":"):
        raise error_factory(
            f"line {number}: a plain scalar may not hold ': '; write the value in double quotes"
        )
    return value


def _double_quoted(value: str, number: int, error_factory: ErrorFactory) -> str:
    """The content of one double-quoted scalar, read by the parser that owns quoting.

    `BaseLoader` resolves no implicit type, so what comes back is the text the quotes
    hold. Anything after the closing quote makes this not one scalar, and the parser
    says so rather than this module deciding where the quote ended — which is the
    guess that took four forms elsewhere in this repository.
    """
    try:
        read = yaml.load(value, Loader=yaml.BaseLoader)
    except yaml.YAMLError as error:
        raise error_factory(f"line {number}: {str(error).splitlines()[0]}") from error
    if not isinstance(read, str):
        raise error_factory(f"line {number}: a quoted scalar must hold one string")
    return read
