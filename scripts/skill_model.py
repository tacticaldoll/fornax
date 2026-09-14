#!/usr/bin/env python3
"""The shared definition of the skill model the repository scripts read.

`FormatSchema` is the shape of that model, and `FORNAX_FORMAT` is this collection's
filling of it: the value space for `family` and `status`, the manifest fields a skill
must and must not declare, the resource keys it may bundle, whether the `**Input**:`
contract line is required, and the grammars for a folder name and a handoff. Several
of those were literals inside `validate_skills`, each decided where it was read.
Holding them in one value is what lets a collection state a different filling
without a second validator, and what keeps a check from being the place a new literal
lands.

`FAMILIES` is the single definition of the allowed `family` values, in the order
the README skill maps present them, mapped to their display titles — so a family
cannot be added without also giving it a title. `STATUSES` is the single
definition of the allowed `status` values, in lifecycle order. They, `NAME_PATTERN`
and `HANDOFF` stay module names because sibling scripts and the prose that cites them
read them there; each is bound to the schema's own field rather than restating it, so
the two cannot drift.

`NAME_PATTERN` is the shape a skill folder and the collection both take. Note that
the repository spells this rule in more than one place — `^[a-z0-9-]+$` here,
`^[a-z0-9]+(?:-[a-z0-9]+)*$` in development_knowns.py, and the same inline in
skill_interface.py's record pattern — and the first admits a leading, trailing or
doubled hyphen that the others reject. Unifying them changes what validates, so it is
a decision, not a cleanup. Gathering the values into a schema does not make that
decision: the other spellings stay where they are, outside this owner, deliberately.

`HANDOFF` is the single definition of how a skill writes a handoff, so the
validator and the map generator agree on what counts as one. Cross-skill record
interfaces are structural declarations read by ``skill_interface.py``, not prose
patterns kept here.

docs/skill-yaml-schema.md carries the prose definition of what each value means;
this module carries the values the scripts enforce, so adding a family, status,
or handoff phrasing is one edit rather than one per script. Imported by the
sibling scripts in this directory. Standard library only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class FormatSchema:
    """What one collection declares its portable skill format to be.

    Frozen because a check that reads a value must not be able to set it. The
    literals this gathers were each edited where they were read, which is the shape
    of defect `skill_model` already records under `NAME_PATTERN`: one rule, more than
    one spelling, no owner to notice.

    `forbidden_manifest_fields` carries each refused field with the reason it is
    refused, because the reason is most of the value of refusing it — a bare "not
    allowed" sends the reader to a governance document to find out which decision
    they hit.

    `requires_input_line` is here and the `**Input**:` label's grammar is not. The
    label does not vary: a collection that does not want the contract line omits the
    line rather than spelling it differently, so the grammar stays with the reader
    that owns it and only the requirement is declared. A grammar nobody varies, put
    where a collection may vary it, is an invitation and not a setting.
    """

    name_pattern: re.Pattern[str]
    families: dict[str, str]
    statuses: tuple[str, ...]
    handoff: re.Pattern[str]
    required_manifest_fields: tuple[str, ...]
    block_manifest_fields: tuple[str, ...]
    forbidden_manifest_fields: tuple[tuple[str, str], ...]
    description_prefix: str | None
    requires_input_line: bool
    resource_keys: tuple[str, ...]


FORNAX_FORMAT = FormatSchema(
    name_pattern=re.compile(r"^[a-z0-9-]+$"),
    families={
        "implementation": "Implementation",
        "knowledge": "Knowledge",
        "decisions": "Decisions & governance",
        "meta": "Meta (skills about the toolkit)",
    },
    statuses=("draft", "stable", "deprecated"),
    handoff=re.compile(
        r"\b(?:hand off to|handoff to|point to|route to)\s+`([a-z0-9-]+)`",
        re.IGNORECASE,
    ),
    required_manifest_fields=("name", "family", "description", "triggers", "entrypoint"),
    # Required fields whose value is the block beneath them rather than same-line text.
    block_manifest_fields=("triggers",),
    forbidden_manifest_fields=(
        ("version", "release versioning is the collection's (distribution.json)"),
    ),
    description_prefix="Use when ",
    requires_input_line=True,
    resource_keys=("scripts", "references", "assets"),
)

NAME_PATTERN = FORNAX_FORMAT.name_pattern
FAMILIES: dict[str, str] = FORNAX_FORMAT.families
STATUSES: tuple[str, ...] = FORNAX_FORMAT.statuses
HANDOFF = FORNAX_FORMAT.handoff


def listed(values) -> str:
    """Render an enumeration the way the validator messages read: 'a, b, or c'."""
    items = list(values)

    if len(items) < 2:
        return "".join(items)

    return f"{', '.join(items[:-1])}, or {items[-1]}"
