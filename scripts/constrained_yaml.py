#!/usr/bin/env python3
"""Shared plain-scalar rules for the repository's constrained YAML readers.

The readers own their document grammars and public error types. This module owns
only the scalar syntax they deliberately share, so unsupported YAML features
cannot drift between otherwise independent parsers.
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
    if re.search(r"(?:^|\s)[&*!][^\s]+", value):
        raise error_factory(f"line {number}: YAML anchors, aliases, and tags are unsupported")
    return value
