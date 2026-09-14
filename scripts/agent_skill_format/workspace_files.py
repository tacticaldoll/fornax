#!/usr/bin/env python3
"""List the files a workspace actually carries, as git sees them.

More than one check needs the same answer to "what is in this workspace": text hygiene
reads every file, and the distribution check looks for install pins in the
Markdown among them. Asking git rather than walking the tree is what keeps
.venv, caches, and build output out without a skip list that would go stale
beside .gitignore.

A root that is not a git worktree raises, rather than reporting an empty
workspace. A check that silently found nothing to inspect would report the
same clean result as one that inspected everything.

Standard library only.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def workspace_files(root: Path) -> list[Path]:
    """Return cached and non-ignored untracked files in the workspace."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    )
    return [root / os.fsdecode(path) for path in result.stdout.split(b"\0") if path]


def listed(root: Path) -> tuple[list[Path] | None, str | None]:
    """Return the workspace files, or a diagnostic naming why they could not be read.

    The raise is the right default — a check must not read an unlistable workspace as
    an empty one — but every caller then has to turn it into its own diagnostic, and
    the second caller did not. This is that turn, written once: a release tarball or a
    `git archive` export is a directory a check can legitimately be pointed at, and it
    should report rather than traceback.
    """
    try:
        return workspace_files(root), None
    except (OSError, subprocess.CalledProcessError) as error:
        return None, f"workspace could not be listed: {error}"
