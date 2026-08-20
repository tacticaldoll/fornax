#!/usr/bin/env python3
"""Render untrusted text so it cannot forge the report that quotes it.

Every check in this directory reads content it does not control — a manifest value, a
link destination, a registry scalar, the text of an OS error — and prints some of it
back. The exit code was never at risk; the report a human reads was, and the report
is the product.

Two attacks, one class. An escape sequence rewrites the line it sits in, so a value
could bend its own FAIL toward looking like a pass. A right-to-left override reverses
how the rest of the line renders, so "SKILL.md<RLO>dm.LLIKS ton" reads as
"SKILL.md not SKILL.md" — the report saying the opposite of what it says. The first
is Unicode category Cc; the second is Cf, and an earlier rule that matched a codepoint
*range* caught only the first.

So the test is the category, taken from the Unicode database rather than a list kept
here: Cc and Cf hide or redirect, Zl and Zp end a line where the file did not. Cs
cannot occur in text decoded from UTF-8, and Co renders as whatever a font chooses
rather than as a way to hide something, so neither is escaped.

One cost, recorded as a decision: U+200D ZERO WIDTH JOINER is Cf, so a joined emoji
sequence in a diagnostic renders as its parts. For a one-line report that is the right
trade against a line that can be reversed, and carving out an exception would put back
the hand-maintained list this rule exists to avoid.

Standard library only.
"""

from __future__ import annotations

import unicodedata

HIDDEN = frozenset({"Cc", "Cf", "Zl", "Zp"})


def _shown(character: str) -> str:
    """One hidden codepoint, in the width Python itself would use for it."""
    code = ord(character)

    if code < 0x100:
        return f"\\x{code:02x}"

    if code < 0x10000:
        return f"\\u{code:04x}"

    return f"\\U{code:08x}"


def printable(text: str) -> str:
    """One line of report text, with anything invisible shown rather than obeyed."""
    return "".join(
        _shown(character) if unicodedata.category(character) in HIDDEN else character
        for character in text
    )
