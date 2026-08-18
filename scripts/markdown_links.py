#!/usr/bin/env python3
"""Shared inline Markdown-link parsing for repository maintenance checks."""

from __future__ import annotations

import re
import string
from dataclasses import dataclass
from typing import Iterator, Optional, Tuple


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


def _backtick_run(text: str, index: int) -> int:
    end = index
    while end < len(text) and text[end] == "`":
        end += 1
    return end - index


def _is_escaped(text: str, index: int) -> bool:
    backslashes = 0
    index -= 1
    while index >= 0 and text[index] == "\\":
        backslashes += 1
        index -= 1
    return backslashes % 2 == 1


def _mask_code_spans(text: str) -> str:
    masked = list(text)
    position = 0
    while position < len(text):
        if text[position] != "`" or _is_escaped(text, position):
            position += 1
            continue
        width = _backtick_run(text, position)
        search = position + width
        closing = None
        while search < len(text):
            candidate = text.find("`", search)
            if candidate < 0:
                break
            candidate_width = _backtick_run(text, candidate)
            if candidate_width == width:
                closing = candidate + width
                break
            search = candidate + candidate_width
        if closing is None:
            position += width
            continue
        masked[position:closing] = " " * (closing - position)
        position = closing
    return "".join(masked)


def _next_payload_start(masked: str, position: int) -> Optional[int]:
    while position < len(masked):
        if masked[position] == "\\" and position + 1 < len(masked):
            position += 2
            continue
        if masked[position] != "[":
            position += 1
            continue
        depth = 1
        index = position + 1
        while index < len(masked):
            if masked[index] == "\\" and index + 1 < len(masked):
                index += 2
                continue
            if masked[index] == "[":
                depth += 1
            elif masked[index] == "]":
                depth -= 1
                if depth == 0:
                    if index + 1 < len(masked) and masked[index + 1] == "(":
                        return index + 2
                    position += 1
                    break
            index += 1
        else:
            position += 1
    return None


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
    masked = _mask_code_spans(text)
    position = 0
    while True:
        start = _next_payload_start(masked, position)
        if start is None:
            return
        parsed = _payload(text, start)
        if parsed is None:
            position = start
            continue
        end, destination = parsed
        yield MarkdownLink(text[start:end], destination)
        position = end + 1


def local_target(destination: str) -> Optional[str]:
    """Return the filesystem portion of a local destination, if it has one."""
    target = destination.split("#", 1)[0]
    if not target or EXTERNAL_SCHEME.match(target):
        return None
    return target
