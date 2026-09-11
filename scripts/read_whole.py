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
import shlex
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


def shell_words(command: str) -> list[str] | Unread:
    """Split a shell command into its words, with quoting decided by a real lexer.

    Quoting is what bounds a word, and every hand-written attempt at that boundary here
    has been a list of characters that may not follow — short by `+`, then by `;`, `|`
    and `>`, then by `_` and `/`. `shlex` owns this grammar and does not guess: an
    operator ends a word, a quote holds one together, and text it cannot finish reading
    raises rather than returning the part it managed.

    Its comment rule is not the shell's, though. `shlex` ends a word at any `#`, so
    `tool==1.0#x` lexes to `tool==1.0` — a silent truncation, the very kind this module
    exists to stop, arriving from the library instead of from a hand-written matcher.
    `bash -c 'echo tool==1.0#x'` prints `tool==1.0#x`. So commenting is turned off and the
    shell's own rule applied instead: a `#` that begins a word.

    Where that rule was applied is what this had wrong. A regex ran over the raw command
    before the lexer saw it, so a quoted hash was cut and `echo "value # kept"` came back
    unread for a closing quote the text actually had. Widening the regex is the repair the
    round before made, and it is why the hole reopened one character to the left: the
    guess had to go rather than grow.

    So the comment is found by a scan that keeps quotes, and the words are read from the
    text itself. Both readings are the lexer's and neither is this module's.

    The scan places each word by searching the text for it, not by asking where the lexer
    is. A word it hands back appears in the command verbatim and in order, and what lies
    between two words is the whitespace it consumed, so a `find` from a running cursor is
    exact. `instream.tell()` is not: it runs one character of lookahead ahead of the
    token except at end of input, and subtracting that character would be this module's
    own mistake in a smaller place.

    A token beginning with `#` is not yet a comment. The scan ends a token at a closing
    quote, so a hash touching one opens a token where the shell opens no word, and asking
    only whether a token began read `echo "a"#b` as `echo a` — dropping the word and
    every word after it. That was this module's own rule wearing the lexer's name, and it
    was the same defect as the regex it replaced, one character to the right. What makes
    a word begin is asked of the text instead: the command starts there, or unconsumed
    text separates it from the token before, or that token was an operator, which the
    lexer's own `punctuation_chars` decides rather than a list written here.

    Where that question cannot be answered the command is refused. The scan does not
    resolve escapes, so a token ending in a backslash leaves a separator this cannot
    tell from an escaped space — `echo a\\ #b` is one word to bash — and reading it
    short would be the quiet failure again. An `Unread` is the loud one.

    The words then come from posix `shlex` over the raw text up to the comment, never
    from rejoining what the scan returned. A scan that keeps quotes reads `"x"'y'` as two
    tokens where the shell has one word, so rejoining invents a boundary that slicing
    cannot.
    """
    scan = shlex.shlex(command, posix=False, punctuation_chars=True)
    scan.whitespace_split = True
    scan.commenters = ""
    cut, cursor, previous = len(command), 0, None
    try:
        for token in scan:
            start = command.find(token, cursor)
            if start < 0:
                return Unread(command, "holds a word the scan did not take from its text")
            gap = command[cursor:start]
            cursor = start + len(token)
            if token.startswith("#"):
                if previous is not None and previous.endswith("\\"):
                    return Unread(
                        command,
                        "ends a word with an escape this cannot resolve before a hash",
                    )
                operator = previous is not None and all(
                    character in scan.punctuation_chars for character in previous
                )
                if start == 0 or gap or operator:
                    cut = start
                    break
            previous = token
    except ValueError as error:
        return Unread(command, f"is not a shell command: {error}")

    lexer = shlex.shlex(command[:cut], posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError as error:
        return Unread(command, f"is not a shell command: {error}")
