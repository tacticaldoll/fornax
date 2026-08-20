#!/usr/bin/env python3
"""Read the YAML subset a skill.yaml manifest is written in.

Deliberately more liberal than constrained_yaml.py, and the two are not
interchangeable. That module enforces a narrow subset on files this repository alone
writes, so it refuses anything it does not recognise. skill.yaml is a published
interface that registries and third-party installers also parse, so a reader here
that refused an ordinary manifest would reject something the ecosystem accepts. This
one therefore reads what it needs and stays quiet about the rest.

Every pattern uses ``[^\\S\\n]`` rather than ``\\s`` between a key and its value.
Whitespace allowed to cross the newline lets a key with no value match the line
beneath it, which is how an empty entrypoint once reported itself as
"not found: triggers:". Standard library only.
"""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass


class Shape(enum.Enum):
    """What reading one key established.

    ``UNREAD`` is the state this module used to lack. A key declared in a shape a
    reader does not handle is not the same fact as a key nobody declared, and
    collapsing the two let a caller treat "declared as something else" as "absent"
    — silently, because there was no value to report and no way to say why.
    """

    ABSENT = "absent"
    READ = "read"
    UNREAD = "unread"


@dataclass(frozen=True)
class ListRead:
    """Items a key declares as a block list, or why they were not read."""

    shape: Shape
    items: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScalarRead:
    """The scalar a key declares, or why it was not read."""

    shape: Shape
    value: str | None = None


def declares_key(text: str, key: str) -> bool:
    """Whether one key appears at all, for a key whose value is the block beneath it."""
    return bool(re.search(rf"^{re.escape(key)}[^\S\n]*:", text, re.MULTILINE))


def declares_value(text: str, key: str) -> bool:
    r"""Whether one key names a value on its own line.

    ``[^\S\n]`` rather than ``\s`` throughout: whitespace that may cross the newline
    lets an empty key match the next line, which is how an empty entrypoint came to
    report itself as "not found: triggers:" and how an empty frontmatter name passed
    by matching "description:".
    """
    return bool(re.search(rf"^{re.escape(key)}[^\S\n]*:[^\S\n]*\S", text, re.MULTILINE))


def get_top_level_yaml_value(content: str, key: str) -> str | None:
    pattern = re.compile(
        rf"^{re.escape(key)}[^\S\n]*:[^\S\n]*([^\n]+?)[^\S\n]*$", re.MULTILINE
    )
    match = pattern.search(content)

    if not match:
        return None

    return clean_yaml_scalar(match.group(1))


def get_yaml_mapping_value(content: str, parent_key: str, child_key: str) -> ScalarRead:
    """Read one child scalar under a parent key, or say the child holds a block.

    A child declared with no same-line scalar is ``UNREAD``, not absent. Returning
    an empty string for it let a caller's ``if value`` treat "declared as a nested
    block" as "never declared", so a resources key naming nothing was skipped in
    silence while the schema calls the value a relative path.
    """
    in_parent = False

    for line in content.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if not line.startswith((" ", "\t")):
            in_parent = line.split(":", 1)[0].strip() == parent_key
            continue

        if in_parent:
            stripped = line.strip()

            if ":" not in stripped:
                continue

            key, value = stripped.split(":", 1)

            if key.strip() == child_key:
                scalar = clean_yaml_scalar(value)
                if not scalar:
                    return ScalarRead(Shape.UNREAD)
                return ScalarRead(Shape.READ, scalar)

    return ScalarRead(Shape.ABSENT)


def get_yaml_list(content: str, key: str) -> ListRead:
    """Read one key's block list, or say the key holds a shape this does not read.

    A block list is every line under the key being a ``-`` item at one indentation
    of spaces. Anything else — a nested mapping, items at mixed indentation, a
    same-line scalar — is ``UNREAD`` rather than a shorter list, because attributing
    a nested item to the key let a key that declares no list of its own satisfy a
    rule that the schema states as "list of strings".

    Indentation must be spaces: YAML forbids tabs for indentation, so a tab-indented
    item is a shape this reader declines rather than one it silently accepts.
    """
    seen_key = False
    in_key = False
    items: list[str] = []
    item_indent: str | None = None
    unread = False

    for line in content.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if not line.startswith((" ", "\t")):
            head, _, tail = line.partition(":")
            in_key = head.strip() == key
            if in_key:
                if seen_key:
                    # The key is declared twice; which list is meant is not readable.
                    return ListRead(Shape.UNREAD, tuple(items))
                seen_key = True
                if tail.strip():
                    unread = True
            continue

        if not in_key:
            continue

        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]

        if "\t" in indent or not stripped.startswith("- "):
            unread = True
            continue

        if item_indent is None:
            item_indent = indent
        elif indent != item_indent:
            unread = True
            continue

        items.append(clean_yaml_scalar(stripped[2:]))

    if not seen_key:
        return ListRead(Shape.ABSENT)
    if unread or item_indent is None:
        return ListRead(Shape.UNREAD, tuple(items))
    return ListRead(Shape.READ, tuple(items))


def clean_yaml_scalar(value: str) -> str:
    return value.strip().strip("'").strip('"')
