#!/usr/bin/env python3
"""Generate the record inventory for every producer→consumer seam between skills.

A seam is a consumer and producer whose optional ``skill-interface.yaml`` files name the
same record identity. The list is **derived** rather than maintained, so every matching pair
the corpus declares is counted without editing anything here — the same reason the README
skill maps come from each skill's handoffs rather than from a list somebody keeps.

Zero seams is a clean answer, not a failure. A check that failed on none would become a
reason to keep a seam alive, which is the opposite of what this is for.

**What this does not observe.** It does not judge whether each element the producer emits is
read, nor whether the consumer names an element the producer never writes. Those are the two
defects this repository found by hand, and both were found by reading an inventory beside the
prose that described it — not by an assertion a script could make without guessing which of a
producer's fields a consumer is obliged to care about. The inventory is generated so that it
cannot go stale while the prose beside it does; reconciling the two stays a human act.

The block lives in docs/review-record-contract.md between the SEAM-INVENTORY markers.
Standard library only.

Usage:
    .venv/bin/python scripts/seam_contract.py            # print the block to stdout
    .venv/bin/python scripts/seam_contract.py --write    # splice it into the contract
    .venv/bin/python scripts/seam_contract.py --check    # fail when the contract is out of date
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Tuple

import generated_block
from generated_block import BlockError, Markers, Rendered
from skill_interface import (
    INTERFACE_FILE,
    InterfaceError,
    RecordIdentity,
    SkillInterface,
    load as load_interface,
)

ROOT = Path(__file__).resolve().parent.parent

CONTRACT = Path("docs/review-record-contract.md")
MARKERS = Markers("SEAM-INVENTORY", "scripts/seam_contract.py")
LABEL = "seam inventory"

OUTPUT_TEMPLATE = re.compile(
    r"^<!-- OUTPUT-TEMPLATE: ([a-z0-9]+(?:-[a-z0-9]+)*)@([1-9][0-9]*) "
    r"([a-z0-9][a-z0-9!#$&^_.+-]*/[a-z0-9][a-z0-9!#$&^_.+-]*) -->\n"
    r"```markdown\n(.*?)^```",
    re.MULTILINE | re.DOTALL,
)
HEADER_FIELD = re.compile(r"^\*\*([^*]+)\*\*\s*:", re.MULTILINE)
SECTION = re.compile(r"^#{2,3} (.+)$", re.MULTILINE)

RecordShape = List[Tuple[str, str]]
Seam = Tuple[str, str, str, RecordShape]


class SeamError(BlockError):
    """A seam the corpus declares but cannot support, reported like any block failure.

    A subclass rather than an alias: a producer missing its marked template is a fact
    about the corpus, not about the block protocol, and dispatch still catches it.
    """


def where(path: Path) -> str:
    """Bind the shared formatter to this module's root, which the suites patch."""
    return generated_block.where(path, ROOT)


def read(path: Path) -> str:
    """Bind the shared reader to this module's root, which the suites patch."""
    return generated_block.read(path, ROOT)


def elements(skill_md: str, record: RecordIdentity) -> RecordShape:
    """The record shape a producer states: its header fields, then its sections.

    Read only the explicitly marked output template for this record. Other Markdown
    examples cannot silently become the contract merely by appearing first.
    """
    key = (record.record_type, str(record.major), record.media_type)
    templates: dict[tuple[str, str, str], list[str]] = {}
    for found_type, major, media_type, template in OUTPUT_TEMPLATE.findall(skill_md):
        templates.setdefault((found_type, major, media_type), []).append(template)
    if len(templates.get(key, [])) > 1:
        raise SeamError(
            f"duplicate marked output template for {record.record_type}@{record.major} "
            f"{record.media_type}"
        )
    if key not in templates:
        return []
    template = templates[key][0]

    return [(name.strip(), "field") for name in HEADER_FIELD.findall(template)] + [
        (name.strip(), "section") for name in SECTION.findall(template)
    ]


def load(skills_dir: Path) -> list[Seam]:
    """Every seam the corpus declares, as (consumer, producer, record, elements)."""
    try:
        names = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())
    except OSError as error:
        raise SeamError(f"{where(skills_dir)} - {error}") from error

    body = {name: read(skills_dir / name / "SKILL.md") for name in names}
    interfaces: list[SkillInterface] = []
    for name in names:
        sidecar = skills_dir / name / INTERFACE_FILE
        if not sidecar.exists():
            continue
        try:
            interfaces.append(load_interface(sidecar, name))
        except InterfaceError as error:
            raise SeamError(f"{where(sidecar)} - {error}") from error
    seams: list[Seam] = []

    for consumer in interfaces:
        for consumed in consumer.consumes:
            for producer in interfaces:
                if producer.skill == consumer.skill or consumed not in producer.produces:
                    continue
                record = (
                    f"{consumed.record_type.replace('-', ' ').title()} "
                    f"v{consumed.major} ({consumed.media_type})"
                )
                shape = elements(body[producer.skill], consumed)
                if not shape:
                    raise SeamError(
                        f"skills/{producer.skill}/SKILL.md - produced record "
                        f"{consumed.record_type}@{consumed.major} {consumed.media_type} "
                        "needs a marked output template"
                    )
                seams.append((consumer.skill, producer.skill, record, shape))

    return seams


def render(seams: list[Seam]) -> Rendered:
    lines = [MARKERS.start, ""]

    if not seams:
        lines.append(
            "No matching producer and consumer sidecars declare a record seam. Nothing to hold."
        )
        lines.append("")
        lines.append(MARKERS.end)
        return Rendered("\n".join(lines), f"({len(seams)} seam(s))")

    for consumer, producer, record, items in sorted(seams):
        lines.append(f"### `{producer}` → `{consumer}` — {record}")
        lines.append("")

        lines.append("| Element | Kind |")
        lines.append("|---|---|")

        for name, kind in items:
            lines.append(f"| `{name}` | {kind} |")

        lines.append("")

    lines.append(MARKERS.end)
    return Rendered("\n".join(lines), f"({len(seams)} seam(s))")


def run(args: argparse.Namespace) -> int:
    seams = load(ROOT / "skills")
    block = generated_block.Block(ROOT, CONTRACT, MARKERS, LABEL)
    return block.sync(args, render(seams))


def main(argv: list[str] | None = None) -> int:
    return generated_block.dispatch(
        argv, run, description="Generate the seam record inventory.", label=LABEL
    )


if __name__ == "__main__":
    raise SystemExit(main())
