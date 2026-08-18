#!/usr/bin/env python3
"""Shared inline Markdown-link parsing for repository maintenance checks."""

from __future__ import annotations

import re
import string
from dataclasses import dataclass
from typing import Iterator, Optional, Tuple


LINK_OPEN = re.compile(r"\[[^\]\n]+\]\(")
EXTERNAL_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)


@dataclass(frozen=True)
class MarkdownLink:
    raw_target: str
    destination: str


def _unescape_destination(value: str) -> str:
    result = []
    index = 0
    while index < len(value):
        if (
            value[index] == "\\"
            and index + 1 < len(value)
            and value[index + 1] in string.punctuation
        ):
            index += 1
        result.append(value[index])
        index += 1
    return "".join(result)


def _after_title(text: str, index: int) -> Optional[int]:
    while index < len(text) and text[index] in " \t":
        index += 1
    if index < len(text) and text[index] == ")":
        return index
    return None


def _quoted_title_end(text: str, index: int, delimiter: str) -> Optional[int]:
    index += 1
    while index < len(text):
        if text[index] == "\\" and index + 1 < len(text):
            index += 2
            continue
        if text[index] == delimiter:
            return _after_title(text, index + 1)
        if text[index] == "\n":
            return None
        index += 1
    return None


def _parenthesized_title_end(text: str, index: int) -> Optional[int]:
    depth = 1
    index += 1
    while index < len(text):
        if text[index] == "\\" and index + 1 < len(text):
            index += 2
            continue
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return _after_title(text, index + 1)
        elif text[index] == "\n":
            return None
        index += 1
    return None


def _payload(text: str, start: int) -> Optional[Tuple[int, str]]:
    index = start
    if index >= len(text) or text[index] in " \t\n)":
        return None

    if text[index] == "<":
        destination_start = index + 1
        index += 1
        while index < len(text):
            if text[index] == "\\" and index + 1 < len(text):
                index += 2
                continue
            if text[index] == ">":
                destination = text[destination_start:index]
                index += 1
                break
            if text[index] in "<\n":
                return None
            index += 1
        else:
            return None
    else:
        destination_start = index
        depth = 0
        while index < len(text):
            if text[index] == "\\" and index + 1 < len(text):
                index += 2
                continue
            if text[index] == "(":
                depth += 1
            elif text[index] == ")":
                if depth == 0:
                    return index, _unescape_destination(text[destination_start:index])
                depth -= 1
            elif text[index] in " \t" and depth == 0:
                break
            elif text[index] == "\n":
                return None
            index += 1
        else:
            return None
        destination = text[destination_start:index]

    while index < len(text) and text[index] in " \t":
        index += 1
    if index >= len(text):
        return None
    if text[index] == ")":
        return index, _unescape_destination(destination)
    if text[index] in "\"'":
        end = _quoted_title_end(text, index, text[index])
    elif text[index] == "(":
        end = _parenthesized_title_end(text, index)
    else:
        return None
    if end is None:
        return None
    return end, _unescape_destination(destination)


def iter_markdown_links(text: str) -> Iterator[MarkdownLink]:
    """Yield inline links whose destination and optional title parse completely."""
    position = 0
    while True:
        match = LINK_OPEN.search(text, position)
        if match is None:
            return
        parsed = _payload(text, match.end())
        if parsed is None:
            position = match.end()
            continue
        end, destination = parsed
        yield MarkdownLink(text[match.end() : end], destination)
        position = end + 1


def local_target(destination: str) -> Optional[str]:
    """Return the filesystem portion of a local destination, if it has one."""
    target = destination.split("#", 1)[0]
    if not target or EXTERNAL_SCHEME.match(target):
        return None
    return target
