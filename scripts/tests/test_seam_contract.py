from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fixtures
import generated_block
import seam_contract

PUBLISHER = "9d0f3c1a-7b2e-4e61-8d45-2a6f90c3b817"
RECORD = f"{PUBLISHER}/review-record@1 text/markdown"

BEFORE = "# Fixture\n\nProse above the block.\n\n"
AFTER = "\nProse below the block.\n"

PRODUCER = """---
name: {name}
description: {description}
---

# {name}

**Input**: the code to look at — if none is given, ask for one.

## Report

<!-- OUTPUT-TEMPLATE: review-record@1 text/markdown -->
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


def write_pair(root: Path, input_line: str, declare_seam: bool = True) -> None:
    """A producer with an output template and optional matching interface declarations."""
    skills = root / "skills"
    fixtures.write_skill(
        skills,
        "alpha-skill",
        skill_md_text=PRODUCER.format(name="alpha-skill", description=fixtures.DESCRIPTION),
        interface_text=(
            f"publisher: {PUBLISHER}\nproduces:\n  - {RECORD}\n" if declare_seam else None
        ),
    )
    fixtures.write_skill(
        skills,
        "beta-skill",
        skill_md_text=CONSUMER.format(
            name="beta-skill", description=fixtures.DESCRIPTION, input_line=input_line
        ),
        interface_text=(
            f"publisher: {PUBLISHER}\nconsumes:\n  - {RECORD}\n" if declare_seam else None
        ),
    )


def write_contract(root: Path, body: str | None = None) -> Path:
    path = root / seam_contract.CONTRACT
    path.parent.mkdir(parents=True, exist_ok=True)

    if body is None:
        markers = seam_contract.MARKERS
        body = f"{BEFORE}{markers.start}\nstale\n{markers.end}{AFTER}"

    path.write_text(body, encoding="utf-8")
    return path


def run(root: Path, *argv: str) -> tuple[int, str]:
    output = StringIO()

    with patch.object(seam_contract, "ROOT", root), redirect_stdout(output):
        code = seam_contract.main(list(argv))

    return code, output.getvalue()


class SeamDiscovery(unittest.TestCase):
    def test_invalid_utf8_is_a_block_error(self):
        # Reading is the shared protocol's job now, so its error type is too. SeamError
        # stays a subclass for what is genuinely a fact about the corpus.
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_bytes(b"# invalid \xff\n")

            with self.assertRaisesRegex(generated_block.BlockError, "must use UTF-8"):
                seam_contract.read(path)

    def test_render_uses_one_blank_line_between_seams(self):
        shape = [("Source", "field")]
        block = seam_contract.render(
            [
                ("beta-skill", "alpha-skill", "Review Record v1 (text/markdown)", shape),
                ("gamma-skill", "alpha-skill", "Review Record v1 (text/markdown)", shape),
            ]
        ).text

        self.assertNotIn("\n\n\n", block)
        self.assertIn("| `Source` | field |\n\n### `alpha-skill` → `gamma-skill`", block)

    def test_matching_interface_records_are_a_seam(self):
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

    def test_prose_does_not_invent_a_seam(self):
        for line in (
            "the thing to do — if the code is unfamiliar, map it first with `alpha-skill`.",
            "the thing to do; if the target is an existing unit, hand off to `alpha-skill`.",
            "a `SKILL.md` (draft or existing), or a passage of it.",
        ):
            with self.subTest(line=line), TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_pair(root, line, declare_seam=False)
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
            write_pair(
                root,
                "the thing this fixture consumes — if none is given, ask for it.",
                declare_seam=False,
            )
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

    def test_an_unmarked_markdown_fence_is_not_the_output_template(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pair(root, "a record")
            write_contract(root)
            producer = root / "skills" / "alpha-skill" / "SKILL.md"
            producer.write_text(
                producer.read_text(encoding="utf-8").replace(
                    "<!-- OUTPUT-TEMPLATE: review-record@1 text/markdown -->\n", ""
                ),
                encoding="utf-8",
            )

            code, out = run(root, "--write")

            self.assertEqual(code, 1)
            self.assertIn("needs a marked output template", out)

    def test_duplicate_output_template_markers_fail(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pair(root, "a record")
            write_contract(root)
            producer = root / "skills" / "alpha-skill" / "SKILL.md"
            text = producer.read_text(encoding="utf-8")
            marked = text[text.index("<!-- OUTPUT-TEMPLATE:") :]
            producer.write_text(text + "\n" + marked, encoding="utf-8")

            code, out = run(root, "--write")

            self.assertEqual(code, 1)
            self.assertIn("duplicate marked output template", out)


if __name__ == "__main__":
    unittest.main()
