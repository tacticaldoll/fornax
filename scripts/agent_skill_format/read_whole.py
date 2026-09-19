"""Read a token whole, or report it unread. There is no third answer.

Round after round of repairs to this repository's matchers closed the same path:
a function that could return a shorter, well-formed value than the text it was given.
`ruff==0.16.1|x` read as `0.16.1`, `@v1.2.3;other` as `v1.2.3`, `tool==1.0#x` as
`1.0` — every one a truncation that then compared equal to what it was checked
against and answered clean. Widening the alphabet closed the instance and left the
path open, which is why a later repair reopened it just above the one before.

So the path is what this module removes rather than the instances. A read is `Whole`
or `Unread`; there is no `Partial`, and `Whole` is constructed only by `whole()`,
which only calls `fullmatch`. A caller holding an `Unread` has no nearly-right value
to compare against anything, so the only thing left to do with it is report it. The
loud direction becomes the one the type admits, instead of the one care preserves.

A wrong guess about a grammar is still a wrong guess. What changes is that it now
shows up as a document this cannot read, not as a document that reads as something
else.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
# Where a requirements line's comment begins, which is the one grammar this still reads
# by hand. `runtime_contract.pins` is the only caller left: pip ends a requirement at a
# `#` that begins a word, and such a line carries no shell quoting for the matcher to
# misread. The operator form is gone with the shell: pip ends such a comment at a hash
# beginning a line or following whitespace, nothing here exercised the operator case,
# and its owner is not installed, so an unexercised rule whose correctness cannot be
# settled buys nothing. A line it therefore leaves whole reaches `packaging`, which
# refuses it loudly rather than comparing a truncation clean.
#
# `shell_words` shared this and no longer does. A shell command can quote a hash, and a
# matcher that cannot read a quote cut `echo "value # kept"` into an unterminated command
# and refused it. What decides a comment there is now the lexer that owns the quoting.
COMMENT = re.compile(r"(?:(?<=\s)|^)#")


@dataclass(frozen=True)
class Unread:
    """Text a reader could not finish, kept exactly as it was written."""

    text: str
    reason: str

    def __str__(self) -> str:
        return f"{self.text} {self.reason}"


@dataclass(frozen=True)
class Whole:
    """A token read to its end, which is checked here rather than promised elsewhere.

    Saying "construct this through `whole()`" is a convention, and a convention is
    what the rounds before it already had. `Whole(PATTERN.match(text))` built a prefix and
    reported its `.value` as a complete read, which is the defect this module claims
    to make inexpressible — expressible, through the door the dataclass opens for free.

    So the invariant is enforced where it is stated: a match that does not span its
    whole subject is not a `Whole`, whoever built it and whichever method produced it.
    """

    match: re.Match[str]

    def __post_init__(self) -> None:
        if self.match.start() != 0 or self.match.end() != len(self.match.string):
            raise ValueError(
                f"{self.match.group(0)!r} is part of {self.match.string!r}, not all of it"
            )

    @property
    def value(self) -> str:
        return self.match.group(0)


Read = Whole | Unread


def whole(text: str, pattern: re.Pattern[str], what: str) -> Read:
    """Read all of *text* as *pattern*, or report it unread. Never part of it."""
    match = pattern.fullmatch(text)
    if match is None:
        return Unread(text, f"is not {what}")
    return Whole(match)
