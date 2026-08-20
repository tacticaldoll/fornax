#!/usr/bin/env python3
"""Generate per-domain skill maps (Mermaid) from skill families and handoffs.

Reads each skill's `family` from skill.yaml and its handoff targets from
SKILL.md, using the shared handoff pattern in skill_model.py, then prints
Markdown with one Mermaid flowchart per family. Cross-family edges appear as
bridges to nodes owned by another family.

A family this module cannot place is a failure, not an omission. render() selects
members by matching FAMILIES, so an unreadable or unknown value silently dropped
the skill from every chart at exit 0, and `--check` agreed because the committed
block recorded the same absence.

The manifest read goes through skill_yaml rather than a pattern kept here. A
private one diverged from it twice: ``\\s`` around the colon crossed the newline, so
an empty `family:` read the line beneath it, and trimming quote *characters* could
not tell a quoted scalar from a plain one, so `family: "meta'` read as `meta` here
while the validator refused the manifest. Two readers disagreeing about one key is
the thing this module has no reason to own.

The maps live in README.md between the SKILL-MAPS markers. `--write` splices
them in so the block never has to be pasted by hand; `--check` fails when the
committed block no longer matches the skills.

Usage:
    .venv/bin/python scripts/skill_graph.py            # print the maps Markdown to stdout
    .venv/bin/python scripts/skill_graph.py --write    # splice the maps into README.md
    .venv/bin/python scripts/skill_graph.py --check    # fail if README.md is out of date
"""

from __future__ import annotations

import argparse
from pathlib import Path

import generated_block
from generated_block import BlockError, Markers, Rendered
from skill_model import FAMILIES, HANDOFF, listed
from skill_yaml import get_top_level_yaml_value

ROOT = Path(__file__).resolve().parent.parent
MARKERS = Markers("SKILL-MAPS", "scripts/skill_graph.py")
LABEL = "skill maps"
TARGET = Path("README.md")


def where(path: Path) -> str:
    """Bind the shared formatter to this module's root, which the suites patch."""
    return generated_block.where(path, ROOT)


def read(path: Path) -> str:
    """Bind the shared reader to this module's root, which the suites patch."""
    return generated_block.read(path, ROOT)


def load(skills_dir: Path):
    try:
        names = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())
    except OSError as error:
        raise BlockError(f"{where(skills_dir)} - {error}") from error

    family: dict[str, str] = {}

    for name in names:
        declared = get_top_level_yaml_value(read(skills_dir / name / "skill.yaml"), "family")
        if declared not in FAMILIES:
            # Not an omission. render() places a skill by matching its family against
            # FAMILIES, so anything else dropped it from every chart and still exited
            # 0 — the one outcome a generated block exists to prevent, and invisible
            # to `--check` because the committed block agreed about the absence.
            states = (
                "declares no readable family" if declared is None else f"declares {declared!r}"
            )
            raise BlockError(
                f"skills/{name}/skill.yaml - family must be {listed(FAMILIES)}; {states}"
            )
        family[name] = declared

    edges: list[tuple[str, str]] = []

    for name in names:
        for target in sorted(set(HANDOFF.findall(read(skills_dir / name / "SKILL.md")))):
            if target in family:
                edges.append((name, target))

    return names, family, edges


def render(names, family, edges) -> Rendered:
    lines = [MARKERS.start]

    for fam, title in FAMILIES.items():
        members = [n for n in names if family.get(n) == fam]

        if not members:
            continue

        lines.append(f"\n### {title}\n")
        lines.append("```mermaid")
        lines.append("flowchart LR")

        for name in members:
            lines.append(f"    {name}")

        for source, target in edges:
            if family.get(source) == fam:
                lines.append(f"    {source} --> {target}")

        lines.append("```")

    lines.append(f"\n{MARKERS.end}")
    return Rendered("\n".join(lines))


def run(args: argparse.Namespace) -> int:
    names, family, edges = load(ROOT / "skills")
    block = generated_block.Block(ROOT, TARGET, MARKERS, LABEL)
    return block.sync(args, render(names, family, edges))


def main(argv: list[str] | None = None) -> int:
    return generated_block.dispatch(
        argv, run, description="Generate the README skill maps.", label=LABEL
    )


if __name__ == "__main__":
    raise SystemExit(main())
