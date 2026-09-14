#!/usr/bin/env python3
"""Run the external Agent Skills baseline with Fornax's declarative profile."""

from __future__ import annotations

from pathlib import Path

from agent_skill_builder.cli import main as builder_main


ROOT = Path(__file__).resolve().parent.parent


def main(root: Path = ROOT) -> int:
    """Delegate the workspace check without reimplementing builder policy."""
    return builder_main(["check", str(root), "--format", "text"])


if __name__ == "__main__":
    raise SystemExit(main())

