#!/usr/bin/env python3
"""Render untrusted text so it cannot forge the report that quotes it.

Every check in this directory reads content it does not control — a manifest value, a
link destination, a registry scalar, the text of an OS error — and prints some of it
back. A value carrying an escape sequence and a carriage return rewrites the line it
sits in, so a skill folder could make its own FAIL line render as OK on any terminal.
The exit code was never affected; the report a human reads was, and the report is the
product.

Control codepoints are escaped and nothing else is. These diagnostics use an em dash
and the collection is not ASCII-only, so every codepoint above the C1 range is left
exactly as written.

Standard library only.
"""

from __future__ import annotations

import re

CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f]")


def printable(text: str) -> str:
    """One line of report text, with any control codepoint shown rather than obeyed."""
    return CONTROL.sub(lambda found: f"\\x{ord(found.group()):02x}", text)
