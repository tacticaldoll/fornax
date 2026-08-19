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
    if value in {"|", ">"}:
        raise error_factory(f"line {number}: multiline scalars are unsupported")
    if re.search(r"(?:^|\s)#", value):
        raise error_factory(f"line {number}: comments are unsupported")
    if re.search(r"(?:^|\s)[&*!][^\s]+", value):
        raise error_factory(f"line {number}: YAML anchors, aliases, and tags are unsupported")
    return value
