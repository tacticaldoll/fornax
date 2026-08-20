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

import re


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


def get_yaml_mapping_value(content: str, parent_key: str, child_key: str) -> str | None:
    lines = content.splitlines()
    in_parent = False

    for line in lines:
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
                return clean_yaml_scalar(value)

    return None


def get_yaml_list(content: str, key: str) -> list[str]:
    lines = content.splitlines()
    in_key = False
    items: list[str] = []

    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if not line.startswith((" ", "\t")):
            in_key = line.split(":", 1)[0].strip() == key
            continue

        if in_key and line.lstrip().startswith("- "):
            items.append(clean_yaml_scalar(line.lstrip()[2:]))

    return items


def clean_yaml_scalar(value: str) -> str:
    return value.strip().strip("'").strip('"')
