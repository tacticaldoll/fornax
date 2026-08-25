"""Skill fixtures built from the enforced manifest schema.

Both suites need skills that pass validation, so the field set lives here
rather than in each of them — the same reason skill_model.py holds the values
the scripts enforce. A schema change is then one edit, not one per suite.

Not named `test_*`, so unittest discovery does not collect it.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import distribution_manifest
import validate_skills

DESCRIPTION = (
    "Use when an agent needs the thing this fixture stands for; does the thing, "
    "rather than doing the other thing."
)

# A fixture default, not the identity under test. A suite that needs the publisher to
# mean something asks for its own — hardcoding one here let a check that ignored the
# collection's declared identity pass every test that used this fixture.
PUBLISHER_ID = "9d0f3c1a-7b2e-4e61-8d45-2a6f90c3b817"


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


def write_worktree(root: Path) -> None:
    """Make the root a git worktree, which is what the pin scan asks for its file list."""
    if not (root / ".git").exists():
        subprocess.run(["git", "init", "-q", str(root)], check=True)


def write_install_docs(
    root: Path, version: str, relatives: tuple[str, ...] | None = None
) -> None:
    """Write one pinned install document per path the pin check requires to carry one.

    The paths are a parameter so a test can patch the registry the check reads without
    also emptying the tree it reads it against. Deriving them from the constant under
    test made the emptied-registry test pass through the route its own comment said it
    had removed: zero documents written, `carrying` empty, and the guard the test exists
    for deletable with the test still green.
    """
    for relative in (
        relatives if relatives is not None else distribution_manifest.PINNED_INSTALL_DOCS
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "Install:\n\n```sh\n"
            f"pipx install \"git+https://example.invalid/fixture.git@v{version}"
            "#subdirectory=tools/cli\"\n```\n",
            encoding="utf-8",
        )


def write_distribution(
    root: Path,
    description: str = "Portable skills that do the thing, rather than the other thing.",
    version: str = "1.2.3",
    name: str = "fixture",
    publisher_id: str = PUBLISHER_ID,
    install_docs: tuple[str, ...] | None = None,
) -> None:
    """A canonical distribution plus the host manifests that project it.

    Two things the pin check needs come from named helpers rather than from this
    body: making the root a worktree, and writing the install documents. Folding
    them in here gave one fixture three jobs and made every test that touches a
    distribution depend on `git` for reasons most of them do not assert.
    """
    (root / "distribution.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "name": name,
                "publisher_id": publisher_id,
                "display_name": "Fixture",
                "description": description,
                "version": version,
                "repository": "https://example.invalid/fixture",
                "skills_directory": "skills",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    for relative in validate_skills.HOST_VERSION_MANIFESTS:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"name": name, "version": version, "description": description}, indent=2)
            + "\n",
            encoding="utf-8",
        )

    write_worktree(root)
    write_install_docs(root, version, install_docs)

    marketplace = root / ".claude-plugin" / "marketplace.json"
    marketplace.parent.mkdir(parents=True, exist_ok=True)
    marketplace.write_text(
        json.dumps(
            {
                "name": name,
                "description": description,
                "plugins": [{"name": name, "description": description, "source": "./"}],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_skill(
    parent: Path,
    name: str,
    family: str = "implementation",
    handoff: str | None = None,
    manifest_text: str | None = None,
    skill_md_text: str | None = None,
    interface_text: str | None = None,
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
    if interface_text is not None:
        (skill_dir / "skill-interface.yaml").write_text(interface_text, encoding="utf-8")
    return skill_dir
