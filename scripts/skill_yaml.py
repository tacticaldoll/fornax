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
"not found: triggers:".

**Reader contract.** A reader returns the value the key declares, or says the key
is declared in a shape it does not read. It never substitutes a reading of its own
for a shape it does not handle. Three readers used to: one attributed a nested
item to the key above it, one returned an empty string for a key holding a block,
and one trimmed quote characters from a scalar that was never quoted. Each
substitution was silent, and a caller cannot guard what it is not told.

``get_yaml_list`` and ``get_yaml_mapping_value`` carry the contract through
``Shape``. ``declares_key`` and ``declares_value`` answer about declaration only,
so they have nothing to substitute. ``clean_yaml_scalar`` returns the text as
declared when it cannot parse a quote pair. ``get_top_level_yaml_value`` is **not
yet** three-state: it returns ``None`` both for an absent key and for one declared
without a same-line scalar. No defect has been reported against that, and it is
recorded here rather than left to be rediscovered as an oversight.

Standard library only.
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
    found: ScalarRead | None = None

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
                if found is not None:
                    # Declared twice under one parent; which value is meant is not
                    # readable. The list reader answers a repeated key the same way.
                    return ScalarRead(Shape.UNREAD)
                scalar = clean_yaml_scalar(value)
                found = ScalarRead(Shape.READ, scalar) if scalar else ScalarRead(Shape.UNREAD)

    if found is None:
        return ScalarRead(Shape.ABSENT)

    return found


def _declares_mapping(item: str) -> bool:
    """Whether a list item's own text makes it a mapping rather than a string.

    ``- name: x`` is a mapping in YAML while the schema calls triggers a list of
    strings, so the item is a shape this reader declines. A colon not followed by
    space or end of line keeps a plain scalar plain — ``1:1`` is text — and a
    quoted item is a scalar however many colons it holds.
    """
    if item[:1] in "'\"":
        return False
    return bool(re.search(r":(\s|$)", item))


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

        if "\t" in indent:
            unread = True
            continue

        if stripped.startswith("- "):
            if item_indent is None:
                item_indent = indent
            elif indent != item_indent:
                unread = True
                continue
            item = stripped[2:].strip()
            if _declares_mapping(item):
                unread = True
                continue
            items.append(clean_yaml_scalar(item))
            continue

        # Not an item. Indented past the items, YAML folds this into the preceding
        # plain scalar, so refusing it would reject an ordinary multi-line trigger.
        # At or above their indentation it is a nested structure instead, and the
        # key declares no list of its own. A plain scalar may not hold ": " on any
        # of its lines, so a continuation that opens a mapping is not one.
        if (
            item_indent is not None
            and items
            and len(indent) > len(item_indent)
            and not _declares_mapping(stripped)
        ):
            items[-1] = f"{items[-1]} {clean_yaml_scalar(stripped)}"
            continue

        unread = True

    if not seen_key:
        return ListRead(Shape.ABSENT)
    if unread or item_indent is None:
        return ListRead(Shape.UNREAD, tuple(items))
    return ListRead(Shape.READ, tuple(items))


def clean_yaml_scalar(value: str) -> str:
    """One scalar with surrounding space and at most one matched quote pair removed.

    Trimming quote *characters* could not tell a quoted scalar from a plain one that
    happens to end in a quote, so ``Use when the user asks "why"`` came back without
    its closing quote, and mismatched or repeated quotes came back as though they had
    been paired. Exactly one matched pair is removed; anything else is returned as
    declared, so a malformed manifest fails on its own content rather than on this
    reader's guess about it.
    """
    scalar = value.strip()

    if len(scalar) >= 2 and scalar[0] in "'\"" and scalar[-1] == scalar[0]:
        return scalar[1:-1]

    return scalar
