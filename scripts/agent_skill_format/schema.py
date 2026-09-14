#!/usr/bin/env python3
"""The shape a collection declares its portable skill format in.

The type only. What Fornax fills it with is Fornax's, and lives with the bindings
its own scripts read — that split is the carve-out in one sentence, and it is why
this module knows the names of the fields and none of their values.

Standard library only.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass


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
