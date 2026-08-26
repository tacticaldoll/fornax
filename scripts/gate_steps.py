#!/usr/bin/env python3
"""Generate README.md's list of what the workspace gate runs, from the gate itself.

A consumer of the block protocol, which its module anticipated. The list this
replaces was transcribed by hand and had gone stale: README named fewer checks than
ran, and called some of the missing ones CI-only after the gate had absorbed them.
Nothing could see the drift, because a count in prose is not a claim any check reads.

The gate's own STEPS is the source. A step added there appears here on the next
`--write` and fails `--check` until it does, which is the same guarantee the skill maps
and the seam inventory already have.

Standard library only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import generated_block
from check_workspace import STEPS, Step
from generated_block import Markers, Rendered

ROOT = Path(__file__).resolve().parent.parent
README = "README.md"
MARKERS = Markers("GATE-STEPS", "scripts/gate_steps.py")
LABEL = "gate step list"


def render(steps: tuple[Step, ...]) -> Rendered:
    """The numbered list, in the order the gate runs them."""
    lines = [MARKERS.start, ""]
    lines.extend(f"{number}. {step.description}" for number, step in enumerate(steps, 1))
    lines.extend(["", MARKERS.end])
    return Rendered("\n".join(lines), detail=f"({len(steps)} step(s))")


def run(args: argparse.Namespace) -> int:
    block = generated_block.Block(ROOT, README, MARKERS, LABEL)
    return block.sync(args, render(STEPS))


def main(argv: list[str] | None = None) -> int:
    return generated_block.dispatch(
        argv, run, description="Generate the workspace gate step list.", label=LABEL
    )


if __name__ == "__main__":
    raise SystemExit(main())
