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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import shell_script

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


def shell_words(command: "shell_script.Line") -> list[str] | Unread:
    """Split a shell command into its words, or report the whole text unread.

    Quoting is what bounds a word, and every hand-written attempt at that boundary here
    has been a list of characters that may not follow — short by `+`, then by `;`, `|`
    and `>`, then by `_` and `/`. `shlex` owns this grammar and does not guess: an
    operator ends a word, a quote holds one together, and text it cannot finish reading
    raises rather than returning the part it managed.

    Its comment rule is not the shell's. `shlex` ends a word at any `#`, so `tool==1.0#x`
    lexes to `tool==1.0` — a silent truncation arriving from the library. So commenting
    is turned off, and the question of where the shell's comment begins is **declined
    rather than answered**.

    That is the repair three rounds did not make. Nothing installable here owns the
    question: `shlex` does not answer it, which is why commenting is off, and `bashlex`
    is refused on licensing. `AGENTS.md` permits a hand-written matcher in exactly that
    position, provided the grammar and its absent owner are registered, which
    `development-knowns.yaml` does for this one — so declining is chosen on evidence and
    not compelled by a rule. The evidence is that three hand-written readings were
    written and each was wrong one character further out: a regex before the lexer, then
    a token-begins test, then an operator test over a scan whose tokens are not the
    shell's words. Each closed the reported instance and reopened the class beside it.

    The caller never needed the answer. `runtime_contract.workflow_pins` needs only never
    to be told a pin bash would not install, and the two directions are not symmetric: a
    refusal is loud and a short read is silent. So this declines.

    A whole-line comment is `shell_script`'s to drop, not this function's to detect. This
    took a string and answered for it with a rule about a line, which was true of a line
    and false of a text someone had joined across a newline; it takes a `shell_script`
    command now, whose type holds no newline, so the case is gone rather than guarded.

    What is left is the question with no owner: a word opening with `#` leaves the
    command unread, because telling that word from a comment needs the quoting that
    posix `shlex` has already removed. `tool==1.0#x` is unaffected — the hash is inside
    the word, not opening it.

    What this costs, in the forms it actually takes. An inline comment is refused, and
    the comment moves to a line of its own. An escaped hash is refused, posix `shlex`
    unescaping it into the token a comment produces. And a hash the author *quoted* is
    refused too — `echo "### building"` among them — because the predicate reads words
    after quote removal, where the quoting that would settle it is already gone. The
    third form is the one this docstring first omitted, and it is the one whose advice
    does not follow: moving a comment elsewhere does nothing for a word that is not a
    comment, so the diagnostic names both ways out. Nothing in this repository carries
    any of the three.
    """
    text = command.text
    lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        words = list(lexer)
    except ValueError as error:
        return Unread(text, f"is not a shell command: {error}")
    if any(word.startswith("#") for word in words):
        return Unread(
            text,
            "holds a word opening with a hash, which no reader here can tell from a "
            "comment; move a comment to a line of its own, or give a word that only "
            "looks like one a form that does not open with a hash",
        )
    return words
