from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fixtures
import seam_contract

BEFORE = "# Fixture\n\nProse above the block.\n\n"
AFTER = "\nProse below the block.\n"

PRODUCER = """---
name: {name}
description: {description}
---

# {name}

**Input**: the code to look at — if none is given, ask for one.

## Report

```markdown
## Review Record

**Source**: [what was read]
**Verdict**: [pass | fail]

### Gate Index

### Findings
```
"""

CONSUMER = """---
name: {name}
description: {description}
---

# {name}

**Input**: {input_line}
"""


def write_pair(root: Path, input_line: str) -> None:
    """A producer with an output template, and a consumer whose Input line is under test."""
    skills = root / "skills"
    fixtures.write_skill(
        skills,
        "alpha-skill",
        skill_md_text=PRODUCER.format(name="alpha-skill", description=fixtures.DESCRIPTION),
    )
    fixtures.write_skill(
        skills,
        "beta-skill",
        skill_md_text=CONSUMER.format(
            name="beta-skill", description=fixtures.DESCRIPTION, input_line=input_line
        ),
    )


def write_contract(root: Path, body: str | None = None) -> Path:
    path = root / seam_contract.CONTRACT
    path.parent.mkdir(parents=True, exist_ok=True)

    if body is None:
        body = f"{BEFORE}{seam_contract.START}\nstale\n{seam_contract.END}{AFTER}"

    path.write_text(body, encoding="utf-8")
    return path


def run(root: Path, *argv: str) -> tuple[int, str]:
    output = StringIO()

    with patch.object(seam_contract, "ROOT", root), redirect_stdout(output):
        code = seam_contract.main(list(argv))

    return code, output.getvalue()


class SeamDiscovery(unittest.TestCase):
    def test_a_named_record_in_an_input_line_is_a_seam(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pair(root, "a `alpha-skill` Review Record, or the findings pasted inline.")
            write_contract(root)

            code, out = run(root, "--write")

            self.assertEqual(code, 0)
            body = (root / seam_contract.CONTRACT).read_text(encoding="utf-8")
            self.assertIn("`alpha-skill` → `beta-skill` — Review Record", body)
            self.assertIn("| `Source` | field |", body)
            self.assertIn("| `Gate Index` | section |", body)
            self.assertIn("rewrote", out)

    def test_a_prerequisite_is_not_a_seam(self):
        """`hand off to` and `map it first with` name a skill without consuming its record.

        This is the discriminating case: counting a prerequisite would invent a contract
        with nothing on either side of it.
        """
        for line in (
            "the thing to do — if the code is unfamiliar, map it first with `alpha-skill`.",
            "the thing to do; if the target is an existing unit, hand off to `alpha-skill`.",
            "a `SKILL.md` (draft or existing), or a passage of it.",
        ):
            with self.subTest(line=line), TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_pair(root, line)
                write_contract(root)

                code, _ = run(root, "--write")

                self.assertEqual(code, 0)
                body = (root / seam_contract.CONTRACT).read_text(encoding="utf-8")
                self.assertIn("Nothing to hold", body)

    def test_no_seams_reports_clean(self):
        """Zero is an answer, not a failure — a check that failed on none would be a
        reason to keep a seam alive."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pair(root, "the thing this fixture consumes — if none is given, ask for it.")
            write_contract(root)

            self.assertEqual(run(root, "--write")[0], 0)

            code, out = run(root, "--check")

            self.assertEqual(code, 0)
            self.assertIn("0 seam(s)", out)


class Staleness(unittest.TestCase):
    def test_check_fails_when_the_producer_moves(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pair(root, "a `alpha-skill` Review Record.")
            write_contract(root)
            self.assertEqual(run(root, "--write")[0], 0)

            producer = root / "skills" / "alpha-skill" / "SKILL.md"
            producer.write_text(
                producer.read_text(encoding="utf-8").replace("**Verdict**:", "**Outcome**:"),
                encoding="utf-8",
            )

            code, out = run(root, "--check")

            self.assertEqual(code, 1)
            self.assertIn("out of date", out)

    def test_check_passes_on_a_written_block(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pair(root, "a `alpha-skill` Review Record.")
            write_contract(root)
            self.assertEqual(run(root, "--write")[0], 0)

            code, out = run(root, "--check")

            self.assertEqual(code, 0)
            self.assertIn("1 seam(s)", out)

    def test_missing_markers_fail(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pair(root, "a `alpha-skill` Review Record.")
            write_contract(root, body="# Fixture\n\nNo markers here.\n")

            code, out = run(root, "--check")

            self.assertEqual(code, 1)
            self.assertIn("markers not found", out)


if __name__ == "__main__":
    unittest.main()
