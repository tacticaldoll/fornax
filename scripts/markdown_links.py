#!/usr/bin/env python3
"""CommonMark link extraction for repository maintenance checks."""

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


def local_target(destination: str) -> Optional[str]:
    """Return the filesystem portion of a local destination, if it has one."""
    if destination.startswith("//"):
        return None
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
