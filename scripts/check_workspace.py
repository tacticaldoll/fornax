#!/usr/bin/env python3
"""Run every fast, deterministic workspace invariant through one entry point."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Step:
    """One gate step: what it is called, what it checks, and how it is run.

    The description sits here rather than in README.md because a transcribed list of
    these went stale: the README named fewer checks than ran, and called some of the
    missing ones CI-only after the gate had absorbed them. scripts/gate_steps.py
    derives that list from this tuple.
    """

    label: str
    description: str
    argv: tuple[str, ...]


STEPS = (
    Step(
        "runtime contract",
        "the maintenance runtime contract — `.python-version`, Ruff's target, and the "
        "running interpreter",
        ("scripts/runtime_contract.py",),
    ),
    Step(
        "production skills",
        "production skill structure, including any optional interface sidecar",
        ("scripts/validate_skills.py",),
    ),
    Step(
        "skill template",
        "the same structure for `templates/skill`",
        (
            "scripts/validate_skills.py",
            "--skills-path",
            "templates",
            "--allow-template-placeholders",
        ),
    ),
    Step(
        "skill maps",
        "the generated README skill maps",
        ("scripts/skill_graph.py", "--check"),
    ),
    Step(
        "record seams",
        "the generated record-seam inventory",
        ("scripts/seam_contract.py", "--check"),
    ),
    Step(
        "development knowns",
        "the `development-knowns.yaml` registry",
        ("scripts/development_knowns.py", "--check"),
    ),
    Step(
        "evidence currency",
        "recorded behavioural evidence against the prose it measured",
        ("scripts/evidence_currency.py", "--check"),
    ),
    Step(
        "gate steps",
        "this list, derived from the gate rather than transcribed",
        ("scripts/gate_steps.py", "--check"),
    ),
    Step(
        "text hygiene",
        "tracked text hygiene and repository-local Markdown links",
        ("scripts/check_text.py",),
    ),
    Step("python style", "Python style, at the pinned Ruff", ("-m", "ruff", "check", ".")),
    Step(
        "non-Python sources",
        "every non-Python source the repository ships, through its own parser",
        ("scripts/check_sources.py",),
    ),
    Step(
        "validation tests",
        "the validation test suite",
        ("-m", "unittest", "discover", "-s", "scripts/tests", "-v"),
    ),
)


def main() -> int:
    failed: list[str] = []
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "scripts")
    for step in STEPS:
        print(f"==> {step.label}", flush=True)
        result = subprocess.run(
            [sys.executable, *step.argv], cwd=ROOT, env=environment, check=False
        )
        if result.returncode:
            failed.append(step.label)
    if failed:
        print(f"Workspace checks failed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print("Workspace checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
