#!/usr/bin/env python3
"""Run the external Agent Skills baseline with Fornax's declarative profile."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

#: What a reader has to do when the pinned baseline is absent from the interpreter
#: running the gate. The import sits inside `main` for this: at module scope its failure
#: is a traceback from the gate's second step, which names the module but not the
#: environment that should hold it. A clone whose `.venv` predates the builder pin fails
#: exactly there, and the traceback sends the reader after the missing package rather
#: than after the sync that installs it.
MISSING_BASELINE = (
    "FAIL Agent Skills baseline - the pinned agent-skill-builder is not installed in "
    "this interpreter.\n"
    "Sync the maintenance environment, as README.md describes:\n"
    "  uv pip sync --python .venv/bin/python requirements-maintenance.txt"
)


def main(root: Path = ROOT) -> int:
    """Delegate the workspace check without reimplementing builder policy."""
    try:
        from agent_skill_builder.cli import main as builder_main
    except ImportError:
        print(MISSING_BASELINE, file=sys.stderr)
        return 1
    return builder_main(["check", str(root), "--format", "text"])


if __name__ == "__main__":
    raise SystemExit(main())
