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

The run is counted on the line's own characters, never on a whitespace-stripped copy.
Bash decides on the character immediately before the newline, so a backslash followed by
a space escapes that space and does not continue the line — and stripping first erases
exactly the character it decides on. The function this replaced stripped before counting,
and the repair carried the strip across while fixing the parity beside it, so one
invisible trailing space folded the next command into the previous one and the install
there was reported by nothing. That is the fourth turn of this class in this grammar and
the first where the mechanism, rather than an instance of it, is what moved.

What is cut before counting is a comment, and only a comment. Bash ends one at the
newline whatever the last character is, so a backslash inside a comment continues
nothing — which is a different rule from the whitespace one above and not an exception
to it: the characters a comment hides were never going to be the ones bash decides on.

The claim this paragraph used to carry was that a corpus measured against bash showed
nothing read as fewer commands than bash runs. It was false, and a review found it with
a two-line input: the corpus covered a comment occupying a whole line and not one opening
partway along one, so a line whose comment ends in a backslash read as one line with the
command under it, where bash runs two. The claim is narrowed to what was actually
measured — the constructs and backslash runs the corpus enumerates, whole-line comments
among them, and now the inline case its own falsifier added. The corpus and its oracle
are described in `docs/guards.md` under this module's dated section.
"""

from __future__ import annotations

from agent_skill_format.read_whole import COMMENT, Line, Unread

HEREDOC = "<<"
QUOTES = ("'", '"')


def commands(script: str) -> list[Line] | Unread:
    """Every line of *script* that runs a command, or the script unread.

    A line, not a command: one of these may hold several, separated by the control
    operators `runtime_contract` splits at. What this settles is where a line ends, which
    is the question that had no owner.
    """
    lines = script.splitlines()
    if len(lines) <= 1:
        text = script.strip()
        if not text or text.startswith("#"):
            return []
        return [Line(text)]

    if HEREDOC in script:
        return Unread(script, "holds a heredoc operator, whose body is data and not commands")
    if any(quote in script for quote in QUOTES):
        return Unread(
            script,
            "spans lines and holds a quote, which may hold a command together across one",
        )

    found: list[Line] = []
    pending = ""
    for line in lines:
        stripped = line.strip()
        if not pending and stripped.startswith("#"):
            continue
        # A backslash inside a comment continues nothing: bash ends a comment at the
        # newline whatever the last character is. The whole-line case is the branch
        # above; this is the same rule for a comment opening partway along a line, which
        # was measured reading `echo ok # note \` and the command under it as one line
        # where bash runs two. The run is therefore counted on the code ahead of the
        # comment, and `COMMENT` is the owner of where one begins. No quote can hide a
        # hash here — a multi-line script holding one is declined above — so a hash
        # opening a word is a comment and nothing else.
        comment = COMMENT.search(line)
        code = line[: comment.start()] if comment else line
        trailing = len(code) - len(code.rstrip("\\"))
        if trailing % 2:
            pending += line[:-1].strip() + " "
            continue
        joined = (pending + stripped).strip()
        pending = ""
        if joined:
            found.append(Line(joined))
    if pending.strip():
        found.append(Line(pending.strip()))
    return found
