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
regexes this replaced did, more than once: one attributed a nested item to the key above
it, one returned an empty string for a key holding a block, and one trimmed quote
characters from a scalar that was never quoted. Each substitution was silent, and a
caller cannot guard what it is not told.

They also refused what YAML accepts, which is the same fault facing the other way: a
line indented past a list's items continues the plain scalar above it, and calling
that mixed indentation rejected a manifest every parser in the ecosystem reads.

``get_yaml_list`` and ``get_yaml_mapping_value`` carry the contract through ``Shape``.
``declares_key`` and ``declares_value`` were the line-bounded regexes left here,
described as having nothing to substitute; they did substitute, saying absent for a
quoted key every parser reads, so they read the parsed mapping too.
``get_top_level_yaml_value`` is **not yet** three-state — it returns ``None`` both for
an absent key and for one whose value is not a non-empty string. No defect has been
reported against that, and it is recorded here rather than left to be rediscovered.

**Ask ``unreadable`` first.** Every value reader answers UNREAD for a document that
will not parse. A caller that guards each field with ``if value`` then skips its
checks one at a time and reports nothing about why, which is how an entrypoint
carrying an escape sequence came to be validated by nothing at all.

``_Loader`` is ``BaseLoader`` corrected. YAML 1.1's implicit types read a
trigger written ``1:1`` as 61, ``no`` as False and ``007`` as 7 — a reader changing
what a manifest says, arriving from the library rather than a regex — so no implicit
resolver runs. And every loader takes a repeated key silently where these readers
answered UNREAD, so one is refused, nested keys included.
"""
from __future__ import annotations

import enum
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


@dataclass(frozen=True)
class Document:
    """One parse of one YAML document: the mapping it holds, or why it holds none.

    Exactly one of the two, checked here. The pair of optional fields was freely
    constructible, so `Document(None, None)` and `Document({}, "error")` were both
    states the type admitted and no code meant — and a type that admits a state nobody
    means is the shape this repository has been removing all round.

    Every accessor used to take the text and parse it again, so a manifest was parsed
    once per required field, once per resource key and once for the version check.
    Reading is one act, and its outcome is a value the readers are handed.

    Carrying the reason was supposed to make the failure unskippable, and the docstring
    said so, and it was not: `skill_graph` read a family straight out of an unreadable
    manifest and reported the family missing. So the mapping is reached through
    `require`, which raises when there is none. A caller that does not ask about
    `reason` first now fails loudly instead of being handed an answer about a document
    that does not exist.
    """

    mapping: dict[str, object] | None
    reason: str | None

    def __post_init__(self) -> None:
        if (self.mapping is None) == (self.reason is None):
            raise ValueError("a document holds a mapping or a reason, never both or neither")

    def require(self) -> dict[str, object]:
        """The mapping, for a caller that has already dealt with `reason`."""
        if self.mapping is None:
            raise Unreadable(self.reason or "")
        return self.mapping


class Unreadable(ValueError):
    """A reader was asked about a document that did not parse."""


def parse(content: str) -> Document:
    """Parse one document once."""
    try:
        loaded = yaml.load(content, Loader=_Loader)
    except yaml.YAMLError as error:
        return Document(None, str(error).replace("\n", " "))
    if loaded is None:
        return Document(None, "declares nothing")
    if not isinstance(loaded, dict):
        return Document(None, "is not a mapping")
    return Document(loaded, None)


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


def declares_key(document: Document, key: str) -> bool:
    """Whether the document declares this key at all, whatever it is written as.

    Read from the parsed mapping, not from the source. A regex over the source line said
    absent for `"name": example`, which is an ordinary quoted key every parser reads —
    and "declared as something else" reported as "never declared" is the substitution
    this module's contract forbids, made by the very functions the contract had named
    as having nothing to substitute.
    """
    return key in document.require()


def declares_value(document: Document, key: str) -> bool:
    """Whether the key declares a non-empty scalar, which is what its callers require.

    Scalar on purpose. Every field asked about here — a name, a family, a description,
    an entrypoint — is one in the schema, and answering yes for a key holding a block
    would put the caller back where it was: declaration seen, `get_top_level_yaml_value`
    returning None because the value is not a string, and the check after it silently
    skipped. A block under one of these keys is a shape the field does not have, and
    saying so is the same answer as saying it declares nothing usable.

    An empty entrypoint once reported itself as "not found: triggers:" by matching the
    line beneath it, and an empty frontmatter name passed by matching "description:".
    Neither is reachable from a parsed mapping.
    """
    value = document.require().get(key)
    return isinstance(value, str) and bool(value.strip())


def get_top_level_yaml_value(document: Document, key: str) -> str | None:
    value = document.require().get(key)
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def get_yaml_mapping_value(document: Document, parent_key: str, child_key: str) -> ScalarRead:
    """Read one child scalar under a parent key, or say the child holds a block.

    A child declared with no same-line scalar is ``UNREAD``, not absent. Returning
    an empty string for it let a caller's ``if value`` treat "declared as a nested
    block" as "never declared", so a resources key naming nothing was skipped in
    silence while the schema calls the value a relative path.
    """
    mapping = document.require()

    parent = mapping.get(parent_key)
    if parent is None and parent_key not in mapping:
        return ScalarRead(Shape.ABSENT)
    if not isinstance(parent, dict) or child_key not in parent:
        return ScalarRead(Shape.ABSENT if isinstance(parent, dict) else Shape.UNREAD)

    child = parent[child_key]
    if not isinstance(child, str) or not child.strip():
        return ScalarRead(Shape.UNREAD)
    return ScalarRead(Shape.READ, child.strip())


def get_yaml_list(document: Document, key: str) -> ListRead:
    """Read one key's list of strings, or say the key holds a shape this does not read.

    The schema calls these lists of strings, so a list holding a mapping is a shape
    this declines rather than a shorter list: attributing a nested item to the key let
    a key that declares no list of its own satisfy the rule.
    """
    mapping = document.require()
    if key not in mapping:
        return ListRead(Shape.ABSENT)

    value = mapping[key]
    if not isinstance(value, list):
        return ListRead(Shape.UNREAD)

    items = tuple(item.strip() for item in value if isinstance(item, str))
    if len(items) != len(value):
        return ListRead(Shape.UNREAD, items)
    return ListRead(Shape.READ, items)
