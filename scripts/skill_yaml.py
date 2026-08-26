#!/usr/bin/env python3
"""Read the YAML a skill.yaml manifest is written in.

Deliberately more liberal than constrained_yaml.py, and the two are not
interchangeable. That module enforces a narrow subset on files this repository alone
writes, so it refuses anything it does not recognise. skill.yaml is a published
interface that registries and third-party installers also parse, so a reader here
that refused an ordinary manifest would reject something the ecosystem accepts. It
therefore reads whatever YAML says, and answers about the shapes the schema names.

**Reader contract.** A reader returns the value the key declares, or says the key is
declared in a shape it does not read. It never substitutes a reading of its own. The
regexes this replaced did, three times: one attributed a nested item to the key above
it, one returned an empty string for a key holding a block, and one trimmed quote
characters from a scalar that was never quoted. Each substitution was silent, and a
caller cannot guard what it is not told.

They also refused what YAML accepts, which is the same fault facing the other way: a
line indented past a list's items continues the plain scalar above it, and calling
that mixed indentation rejected a manifest every parser in the ecosystem reads.

``get_yaml_list`` and ``get_yaml_mapping_value`` carry the contract through ``Shape``.
``declares_key`` and ``declares_value`` are the two line-bounded regexes left: they
answer about declaration only, so they have nothing to substitute.
``get_top_level_yaml_value`` is **not yet** three-state — it returns ``None`` both for
an absent key and for one whose value is not a non-empty string. No defect has been
reported against that, and it is recorded here rather than left to be rediscovered.

**Ask ``unreadable`` first.** Every value reader answers UNREAD for a document that
will not parse. A caller that guards each field with ``if value`` then skips its
checks one at a time and reports nothing about why, which is how an entrypoint
carrying an escape sequence came to be validated by nothing at all.

``_Loader`` is ``BaseLoader`` with two corrections. YAML 1.1's implicit types read a
trigger written ``1:1`` as 61, ``no`` as False and ``007`` as 7 — a reader changing
what a manifest says, arriving from the library rather than a regex — so no implicit
resolver runs. And every loader takes a repeated key silently where these readers
answered UNREAD, so one is refused, nested keys included.
"""
from __future__ import annotations

import enum
import re
from dataclasses import dataclass

import yaml


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


def unreadable(content: str) -> str | None:
    """Why this manifest is not a mapping this can read, or None when it is one.

    A caller has to ask this before reading fields. Every value reader answers UNREAD
    for a document that will not parse, and a caller that guards each field with
    `if value` then skips its checks one by one and reports nothing about why — which
    is how an entrypoint carrying an escape sequence came to be validated by nothing at
    all: the manifest was not YAML, the declaration reader still saw the key declared,
    and the path check quietly did not run.
    """
    try:
        document = yaml.load(content, Loader=_Loader)
    except yaml.YAMLError as error:
        return str(error).replace("\n", " ")
    if document is None:
        return "declares nothing"
    if not isinstance(document, dict):
        return "is not a mapping"
    return None


def _document(content: str) -> dict[str, object] | None:
    """The manifest as a mapping, or None when it is not one this can read.

    `BaseLoader` rather than `safe_load`, because YAML 1.1's implicit types answer a
    different question than this schema asks. Every value here is a string or a list
    of strings, and `safe_load` reads a trigger written `1:1` as the integer 61, `no`
    as False and `007` as 7 — a reader that changes what a manifest says is the
    substitution this module's contract forbids, and it would arrive from the library
    rather than from a regex. `BaseLoader` applies no implicit resolver, so a scalar
    is the text it was written as.

    A repeated key is refused rather than resolved. Both loaders take the last one
    silently; the readers this replaced answered UNREAD, and dropping that would have
    lost a guarantee by adopting a parser. The refusal reaches nested keys too, which
    the hand-written readers only managed for two cases.
    """
    if unreadable(content) is not None:
        return None
    return yaml.load(content, Loader=_Loader)


class _Loader(yaml.BaseLoader):
    """Scalars as written, and a repeated key refused."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict:
        seen: set[str] = set()
        for key_node, _ in node.value:
            # A key must be a scalar before it can be compared. YAML admits a complex
            # key — `? [a, b]` — and constructing one gives a list, so testing set
            # membership with it raised TypeError out of a function whose caller was
            # promised a diagnostic. The schema has no complex keys, so refusing one
            # is both the honest answer and the one that keeps the promise.
            if not isinstance(key_node, yaml.ScalarNode):
                raise yaml.constructor.ConstructorError(
                    None, None, "a key must be a scalar", key_node.start_mark
                )
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, f"duplicate key {key!r}", key_node.start_mark
                )
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


def get_top_level_yaml_value(content: str, key: str) -> str | None:
    document = _document(content)
    if document is None:
        return None
    value = document.get(key)
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def get_yaml_mapping_value(content: str, parent_key: str, child_key: str) -> ScalarRead:
    """Read one child scalar under a parent key, or say the child holds a block.

    A child declared with no same-line scalar is ``UNREAD``, not absent. Returning
    an empty string for it let a caller's ``if value`` treat "declared as a nested
    block" as "never declared", so a resources key naming nothing was skipped in
    silence while the schema calls the value a relative path.
    """
    document = _document(content)
    if document is None:
        return ScalarRead(Shape.UNREAD)

    parent = document.get(parent_key)
    if parent is None and parent_key not in document:
        return ScalarRead(Shape.ABSENT)
    if not isinstance(parent, dict) or child_key not in parent:
        return ScalarRead(Shape.ABSENT if isinstance(parent, dict) else Shape.UNREAD)

    child = parent[child_key]
    if not isinstance(child, str) or not child.strip():
        return ScalarRead(Shape.UNREAD)
    return ScalarRead(Shape.READ, child.strip())


def get_yaml_list(content: str, key: str) -> ListRead:
    """Read one key's list of strings, or say the key holds a shape this does not read.

    The schema calls these lists of strings, so a list holding a mapping is a shape
    this declines rather than a shorter list: attributing a nested item to the key let
    a key that declares no list of its own satisfy the rule.
    """
    document = _document(content)
    if document is None:
        return ListRead(Shape.UNREAD)
    if key not in document:
        return ListRead(Shape.ABSENT)

    value = document[key]
    if not isinstance(value, list):
        return ListRead(Shape.UNREAD)

    items = tuple(item.strip() for item in value if isinstance(item, str))
    if len(items) != len(value):
        return ListRead(Shape.UNREAD, items)
    return ListRead(Shape.READ, items)
