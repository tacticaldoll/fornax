#!/usr/bin/env python3
"""Say where one command ends in a shell script, or decline the script.

Standard library only.

This owns a question that had two homes and no owner. `runtime_contract` joined
continued lines and `read_whole.shell_words` answered for whatever text that produced,
with a rule true only of one line. They disagreed about the same text: a comment line
ending in a backslash was joined onto the next, and the command after it disappeared
into the comment. A workflow could install a pin the gate then reported nothing about.

The shell's statement grammar has no owner this repository may install — `bashlex`
parses it and is GPLv3+ against an MIT tree — so this is hand-written, and
`development-knowns.yaml` registers it. What keeps a hand-written reading honest here is
the same thing that worked at the word level: answer only what needs no grammar, and
decline the rest.

Three rules, and the third is exact only because the second removed what would make it a
guess:

- A script of one line has no boundary question at all. It is one command, or none when
  it is blank or a comment.
- A script of more than one line is declined whole when it holds a quote or a heredoc
  operator. A quote may span the newline, and a heredoc body is data rather than
  commands; deciding either needs the parser this may not have.
- Otherwise a comment line is whole and does not continue — bash ends a comment at the
  newline whatever the last character is, which is the defect this module exists for —
  and a line ending in an **odd** run of backslashes continues onto the next. Parity is
  countable here because a quote would have declined the script already.

Measured against bash over a corpus covering each of those constructs and backslash runs
of one through four: nothing is read as fewer commands than bash runs. The corpus and its
oracle are described in `docs/guards.md` under this module's dated section.
"""

from __future__ import annotations

from dataclasses import dataclass

from read_whole import Unread

HEREDOC = "<<"
QUOTES = ("'", '"')


@dataclass(frozen=True)
class Command:
    """One command's text, holding no newline.

    The invariant is enforced here rather than promised by the caller, for the reason
    `read_whole.Whole` gives about its own: a convention is what the rounds before it
    already had. A reader that takes a `Command` may say "one line" and be right, instead
    of assuming it and being wrong about a text someone joined across a newline.
    """

    text: str

    def __post_init__(self) -> None:
        if "\n" in self.text:
            raise ValueError(f"{self.text!r} holds a newline, so it is not one command")


def commands(script: str) -> list[Command] | Unread:
    """Every command *script* runs, or the script unread when that cannot be settled."""
    lines = script.splitlines()
    if len(lines) <= 1:
        text = script.strip()
        if not text or text.startswith("#"):
            return []
        return [Command(text)]

    if HEREDOC in script:
        return Unread(script, "holds a heredoc operator, whose body is data and not commands")
    if any(quote in script for quote in QUOTES):
        return Unread(
            script,
            "spans lines and holds a quote, which may hold a command together across one",
        )

    found: list[Command] = []
    pending = ""
    for line in lines:
        stripped = line.strip()
        if not pending and stripped.startswith("#"):
            continue
        trailing = len(stripped) - len(stripped.rstrip("\\"))
        if trailing % 2:
            pending += stripped[:-1].rstrip() + " "
            continue
        joined = (pending + stripped).strip()
        pending = ""
        if joined:
            found.append(Command(joined))
    if pending.strip():
        found.append(Command(pending.strip()))
    return found
