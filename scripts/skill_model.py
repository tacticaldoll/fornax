#!/usr/bin/env python3
"""The shared definition of the skill model the repository scripts read.

`FormatSchema` is the shape of that model, and `FORNAX_FORMAT` is this collection's
filling of it: the value space for `family` and `status`, the manifest fields a skill
must and must not declare, the resource keys it may bundle, whether the `**Input**:`
contract line is required, and the grammars for a folder name and a handoff. Several
of those were literals inside `validate_skills`, each decided where it was read.
Holding them in one value is what keeps a check from being the place a new literal
lands.

How far that reaches is worth stating exactly, because the obvious wider claim is not
yet true. `validate_skills.validate_skill` takes a filling and passes it to every check
under it, so the per-skill verdict can be asked about a format other than this one.
Nothing else can: `skill_graph` and `distribution_manifest` read the bindings below and
are therefore pinned to `FORNAX_FORMAT`. A filling that differed from it would be
honoured by the validator and ignored by the map generator, which is why a second
collection needs those readers threaded before the schema is the collection's rather
than the validator's.

`FORNAX_FORMAT.families` is the single definition of the allowed `family` values, in
the order the README skill maps present them, mapped to their display titles — so a
family cannot be added without also giving it a title. `FORNAX_FORMAT.statuses` is the
single definition of the allowed `status` values, in lifecycle order. Add to either by
editing the declaration below, never a module name: the names under it are bindings
onto those fields, and a binding cannot drift from what it binds, but it can look like
the place to make a change.

Each binding is kept for a reader that names it, and the readers differ. `skill_graph`
reads `FAMILIES` and `HANDOFF` as values. `NAME_PATTERN` has no code reader left —
`distribution_manifest` was the last and now asks for a filling — and is kept because
AGENTS.md and `evidence_currency` cite it as a symbol, which the citation gate step
holds: rename it and the gate refuses the rename until both are corrected. That is a
reader, and naming which kind it is matters, because the two go stale differently. A
`STATUSES` binding had neither, so it is not here — a name kept for nobody is worse
than its absence.

`NAME_PATTERN` is the shape a skill folder and the collection both take. Note that
the repository spells this rule in more than one place — `^[a-z0-9-]+$` here,
`^[a-z0-9]+(?:-[a-z0-9]+)*$` in development_knowns.py, the same inline in
skill_interface.py's record pattern and in seam_contract.py's template marker, the
same again in the producer group of validate_skills.py's record-input pattern, and
`[a-z0-9-]+` once more in the capture group of `handoff` below — and the first admits a
leading, trailing or doubled hyphen that the others reject. Unifying them changes what
validates, so it is a decision, not a cleanup. Gathering the values into a schema does
not make that decision: the other spellings stay where they are, outside this owner,
deliberately.

The enumeration is the part that has to grow when this owner does, and it did not: the
schema took the pattern and the sentence still named the two spellings it named before,
while a third sat inside the same file the schema was extracted from and a fourth beside
the field itself.

`HANDOFF` binds `FORNAX_FORMAT.handoff`, so the validator and the map generator
agree on what counts as a handoff. Cross-skill record
interfaces are structural declarations read by ``skill_interface.py``, not prose
patterns kept here.

docs/skill-yaml-schema.md carries the prose definition of what each value means;
this module carries the values the scripts enforce, so adding a family, status,
or handoff phrasing is one edit rather than one per script. Imported by the
sibling scripts in this directory. Standard library only.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class FormatSchema:
    """What one collection declares its portable skill format to be.

    Frozen because a check that reads a value must not be able to set it — and the
    family mapping is proxied, because `dataclass(frozen=True)` refuses to rebind the
    field and says nothing about the object behind it. A plain mapping there was
    writable in place, and the module binding names the same object, so a write under
    either name would have been seen by the validator and the map generator both. The
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
    families: Mapping[str, str]
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
    families=MappingProxyType(
        {
            "implementation": "Implementation",
            "knowledge": "Knowledge",
            "decisions": "Decisions & governance",
            "meta": "Meta (skills about the toolkit)",
        }
    ),
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
FAMILIES: Mapping[str, str] = FORNAX_FORMAT.families
HANDOFF = FORNAX_FORMAT.handoff


def listed(values) -> str:
    """Render an enumeration the way the validator messages read: 'a, b, or c'."""
    items = list(values)

    if len(items) < 2:
        return "".join(items)

    return f"{', '.join(items[:-1])}, or {items[-1]}"
