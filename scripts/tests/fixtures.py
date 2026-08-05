"""Skill fixtures built from the enforced manifest schema.

Both suites need skills that pass validation, so the field set lives here
rather than in each of them — the same reason skill_model.py holds the values
the scripts enforce. A schema change is then one edit, not one per suite.

Not named `test_*`, so unittest discovery does not collect it.
"""

from __future__ import annotations

from pathlib import Path

DESCRIPTION = (
    "Use when an agent needs the thing this fixture stands for; does the thing, "
    "rather than doing the other thing."
)


def manifest(name: str, family: str = "implementation") -> str:
    return (
        f"name: {name}\n"
        f"family: {family}\n"
        "status: draft\n"
        f"description: {DESCRIPTION}\n"
        "triggers:\n"
        f"  - user asks for {name}\n"
        "entrypoint: SKILL.md\n"
    )


def skill_md(name: str, handoff: str | None = None) -> str:
    body = (
        "---\n"
        f"name: {name}\n"
        f"description: {DESCRIPTION}\n"
        "---\n"
        f"\n# {name}\n"
        "\n**Input**: the thing this fixture consumes — if none is given, ask for it.\n"
    )

    if handoff:
        body += f"\nIf it is structural, hand off to `{handoff}`.\n"

    return body


def write_skill(
    parent: Path,
    name: str,
    family: str = "implementation",
    handoff: str | None = None,
    manifest_text: str | None = None,
    skill_md_text: str | None = None,
) -> Path:
    """Write a skill that passes validation, or the overriding text given instead."""
    skill_dir = parent / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "skill.yaml").write_text(
        manifest_text if manifest_text is not None else manifest(name, family), encoding="utf-8"
    )
    (skill_dir / "SKILL.md").write_text(
        skill_md_text if skill_md_text is not None else skill_md(name, handoff), encoding="utf-8"
    )
    return skill_dir
