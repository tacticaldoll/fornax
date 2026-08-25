#!/usr/bin/env python3
"""Run every fast, deterministic workspace invariant through one entry point."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
STEPS = (
    ("runtime contract", "scripts/runtime_contract.py"),
    ("production skills", "scripts/validate_skills.py"),
    (
        "skill template",
        "scripts/validate_skills.py",
        "--skills-path",
        "templates",
        "--allow-template-placeholders",
    ),
    ("skill maps", "scripts/skill_graph.py", "--check"),
    ("record seams", "scripts/seam_contract.py", "--check"),
    ("development knowns", "scripts/development_knowns.py", "--check"),
    ("evidence currency", "scripts/evidence_currency.py", "--check"),
    ("text hygiene", "scripts/check_text.py"),
    ("python style", "-m", "ruff", "check", "."),
    (
        "validation tests",
        "-m",
        "unittest",
        "discover",
        "-s",
        "scripts/tests",
        "-v",
    ),
)


def main() -> int:
    failed: list[str] = []
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "scripts")
    for step in STEPS:
        label, *arguments = step
        print(f"==> {label}", flush=True)
        result = subprocess.run(
            [sys.executable, *arguments], cwd=ROOT, env=environment, check=False
        )
        if result.returncode:
            failed.append(label)
    if failed:
        print(f"Workspace checks failed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print("Workspace checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
