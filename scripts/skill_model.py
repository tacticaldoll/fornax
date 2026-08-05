#!/usr/bin/env python3
"""The shared definition of the skill model the repository scripts read.

`FAMILIES` is the single definition of the allowed `family` values, in the order
the README skill maps present them, mapped to their display titles — so a family
cannot be added without also giving it a title. `STATUSES` is the single
definition of the allowed `status` values, in lifecycle order.

docs/skill-yaml-schema.md carries the prose definition of what each value means;
this module carries the values the scripts enforce, so adding a family or status
is one edit rather than one per script. Imported by the sibling scripts in this
directory. Standard library only.
"""

from __future__ import annotations

FAMILIES: dict[str, str] = {
    "implementation": "Implementation",
    "knowledge": "Knowledge",
    "decisions": "Decisions & governance",
    "meta": "Meta (skills about the toolkit)",
}

STATUSES: tuple[str, ...] = ("draft", "stable", "deprecated")


def listed(values) -> str:
    """Render an enumeration the way the validator messages read: 'a, b, or c'."""
    items = list(values)

    if len(items) < 2:
        return "".join(items)

    return f"{', '.join(items[:-1])}, or {items[-1]}"
