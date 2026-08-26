"""Read a token whole, or report it unread. There is no third answer.

Five rounds of repairs to this repository's matchers closed the same path each time:
a function that could return a shorter, well-formed value than the text it was given.
`ruff==0.16.1|x` read as `0.16.1`, `@v1.2.3;other` as `v1.2.3`, `tool==1.0#x` as
`1.0` — every one a truncation that then compared equal to what it was checked
against and answered clean. Widening the alphabet closed the instance and left the
path open, which is why the fifth repair reopened it three lines above the fourth.

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
import shlex
from dataclasses import dataclass

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
    """A token read to its end. Construct it through `whole()`, never directly."""

    match: re.Match[str]

    @property
    def value(self) -> str:
        return self.match.group(0)

    def group(self, index: int | str) -> str:
        return self.match.group(index)


Read = Whole | Unread


def whole(text: str, pattern: re.Pattern[str], what: str) -> Read:
    """Read all of *text* as *pattern*, or report it unread. Never part of it."""
    match = pattern.fullmatch(text)
    if match is None:
        return Unread(text, f"is not {what}")
    return Whole(match)


def shell_words(command: str) -> list[str] | Unread:
    """Split a shell command into its words, with quoting decided by a real lexer.

    Quoting is what bounds a word, and every hand-written attempt at that boundary
    here has been a list of characters that may not follow — short by `+`, then by
    `;`, `|` and `>`, then by `_` and `/`. `shlex` owns this grammar and does not
    guess: an operator ends a word, a quote holds one together, and text it cannot
    finish reading raises rather than returning the part it managed.

    Its comment rule is not the shell's, though. `shlex` ends a word at any `#`, so
    `tool==1.0#x` lexes to `tool==1.0` — a silent truncation, the very kind this
    module exists to stop, arriving from the library instead of from a hand-written
    matcher. `bash -c 'echo tool==1.0#x'` prints `tool==1.0#x`. So commenting is
    turned off here and cut beforehand by the rule the shell actually uses: a `#`
    that begins a word.
    """
    lexer = shlex.shlex(
        COMMENT.split(command, maxsplit=1)[0], posix=True, punctuation_chars=True
    )
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError as error:
        return Unread(command, f"is not a shell command: {error}")
