#!/usr/bin/env python3
"""CommonMark link and section extraction for repository maintenance checks.

This module owns the repository's CommonMark parser. Both operations that need the
grammar live here rather than beside their callers: link destinations, and the text
under one heading. Writing the grammar again beside a caller is how a fingerprint came
to cover part of the section it named.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Iterator, Optional
from urllib.parse import unquote

from markdown_it import MarkdownIt
from markdown_it.token import Token

from host_paths import is_absolute_anywhere


EXTERNAL_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
PARSER = MarkdownIt("commonmark")


@dataclass(frozen=True)
class MarkdownLink:
    shown_target: str
    destination: str


@dataclass(frozen=True)
class MarkedBlock:
    """A fenced code block and the HTML comment that introduces it."""

    marker: str
    info: str
    content: str


def _markdown_link(token: Token, attribute: str) -> Optional[MarkdownLink]:
    encoded_destination = token.attrGet(attribute)
    if encoded_destination is None:
        return None
    shown_destination = unquote(encoded_destination)
    title = token.attrGet("title")
    if title is None:
        shown_target = shown_destination
    else:
        shown_title = title.replace('"', '\\"')
        shown_target = f'{shown_destination} "{shown_title}"'
    return MarkdownLink(shown_target, encoded_destination)


def _iter_token_links(tokens: Iterable[Token]) -> Iterator[MarkdownLink]:
    for token in tokens:
        if token.type == "link_open":
            link = _markdown_link(token, "href")
            if link is not None:
                yield link
        elif token.type == "image":
            link = _markdown_link(token, "src")
            if link is not None:
                yield link
        if token.children:
            yield from _iter_token_links(token.children)


def iter_markdown_links(text: str) -> Iterator[MarkdownLink]:
    """Yield links and images recognized by the CommonMark parser."""
    yield from _iter_token_links(PARSER.parse(text))


def heading_section(text: str, heading: str) -> Optional[str]:
    """Return one heading's section, the heading line included, or None when absent.

    Delegates the grammar to the same CommonMark parser the link walk uses. A
    hand-written rule that treats any `#`-prefixed line as a heading truncates a
    section at a shebang inside a fenced block, which is how a fingerprint came to
    cover part of the text it claimed.

    The heading is named by its text, not its `#` prefix — the registry that reads
    this cannot express a scalar opening with `#`.
    """
    tokens = list(PARSER.parse(text))
    lines = text.splitlines()
    for index, token in enumerate(tokens):
        if token.type != "heading_open" or token.map is None:
            continue
        inline = tokens[index + 1] if index + 1 < len(tokens) else None
        if inline is None or inline.content.strip() != heading:
            continue
        start = token.map[0]
        depth = int(token.tag[1:])
        for later in tokens[index + 1 :]:
            if later.type != "heading_open" or later.map is None:
                continue
            if int(later.tag[1:]) <= depth:
                return "\n".join(lines[start : later.map[0]])
        return "\n".join(lines[start:])
    return None


def heading_texts(text: str, depths: Iterable[int] = (2, 3)) -> list[str]:
    """Every heading's text at the given depths, in document order.

    Same parser, same reason as `heading_section`: `^#{2,3} (.+)$` counts a `##` inside
    a fenced block as a heading, so a template carrying a fenced example would have its
    example's headings inventoried as its own.
    """
    tokens = list(PARSER.parse(text))
    wanted = {f"h{depth}" for depth in depths}
    found = []
    for index, token in enumerate(tokens):
        if token.type != "heading_open" or token.tag not in wanted:
            continue
        if index + 1 < len(tokens):
            found.append(tokens[index + 1].content.strip())
    return found


def marked_code_blocks(text: str) -> list[MarkedBlock]:
    """Every fenced code block introduced by an HTML comment, in document order.

    A third operation that needs the grammar, here for the reason the module docstring
    gives. `seam_contract` read the fence itself, with `^```markdown\n(.*?)^```` and
    `DOTALL`: the body ended at the first line opening with three backticks, so a
    template fenced as `~~~markdown` was not found at all and one fenced with four
    backticks around a three-backtick example was cut at the example — measured, the
    declared shape lost its last section and the caller saw a shorter shape rather than
    a read it could not make.

    The fence's extent is the parser's answer here. What the parser cannot answer is
    intent: CommonMark closes a fence at the first line of at least as many backticks,
    so a template fenced with three backticks around a three-backtick example truncates
    for the parser exactly as it did for the regex, because that is what the document
    says. `development-knowns.yaml` records that residue.
    """
    tokens = list(PARSER.parse(text))
    blocks = []
    for index, token in enumerate(tokens):
        if token.type != "fence" or index == 0:
            continue
        introduction = tokens[index - 1]
        if introduction.type != "html_block":
            continue
        blocks.append(MarkedBlock(introduction.content.strip(), token.info, token.content))
    return blocks


def local_target(destination: str) -> Optional[str]:
    """Return the filesystem portion of a local destination, if it has one."""
    if destination.startswith("//"):
        return None
    # Split by hand, and not for want of an owner: `urlsplit(...).path` answers a
    # different question. It drops the scheme and authority, which the tests below
    # still need — `C:/docs/x.md` came back as `/docs/x.md` and an external
    # `https://example.com/guide` as `/guide`, so both were judged as local paths. What
    # is wanted here is everything before the fragment, and `#` and `?` are where URL
    # syntax says those begin; a literal one in a path is percent-encoded.
    target = destination.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    decoded = unquote(target)
    if is_absolute_anywhere(decoded):
        # Before the scheme test on purpose: a Windows drive letter is a valid
        # one-character scheme, so "C:/docs/x.md" matched as external and skipped the
        # absolute-link rule entirely. Returning it lets each caller refuse it.
        return decoded
    if EXTERNAL_SCHEME.match(decoded):
        # Both tests read the decoded destination. Judging the encoded one made
        # "%68ttps://example.com" a local path, so an external link was reported as
        # a missing file.
        return None
    return decoded
