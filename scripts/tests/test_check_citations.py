#!/usr/bin/env python3
"""What the citation check must refuse, and what it must leave alone."""

from __future__ import annotations

import unittest
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import check_citations


def workspace(tmp: str, **files: str) -> Path:
    """A root holding a `scripts/` module and whatever documents a case needs."""
    root = Path(tmp)
    (root / "scripts").mkdir()
    (root / "scripts" / "sample_module.py").write_text(
        "CONSTANT = 1\n\n\n"
        "def reads_whole() -> None:\n    pass\n\n\n"
        "class Reader:\n    depth: int\n\n    def read(self) -> None:\n        pass\n",
        encoding="utf-8",
    )
    (root / "docs" / "dispositions").mkdir(parents=True)
    for name, content in files.items():
        path = root / name.replace("__", "/")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def messages(root: Path) -> list[str]:
    return [problem.message for problem in check_citations.check(root)]


class LineCitations(unittest.TestCase):
    def test_a_line_citation_is_refused_in_every_subject(self) -> None:
        for name in ("AGENTS.md", "PROJECT.md", "README.md", "development-knowns.yaml"):
            with self.subTest(name=name), TemporaryDirectory() as tmp:
                root = workspace(tmp, **{name: "See `scripts/sample_module.py:4` for it.\n"})

                found = messages(root)

                self.assertEqual(len(found), 1, found)
                self.assertIn("cites a line", found[0])

    def test_a_line_range_is_refused_too(self) -> None:
        with TemporaryDirectory() as tmp:
            root = workspace(tmp, **{"AGENTS.md": "See `PROJECT.md:5-8`.\n"})

            self.assertIn("cites a line", messages(root)[0])

    def test_a_disposition_record_is_a_subject(self) -> None:
        with TemporaryDirectory() as tmp:
            root = workspace(
                tmp,
                **{"docs__dispositions__v1..v2.md": "Reach `scripts/sample_module.py:4`.\n"},
            )

            self.assertIn("cites a line", messages(root)[0])

    def test_a_citation_inside_a_fence_is_a_quotation(self) -> None:
        """The archive of a producer's record holds line citations on purpose.

        Without this the check would refuse `docs/reviews/` archives if they were ever
        made subjects, and it would refuse a record that quotes the input it reconciles.
        """
        with TemporaryDirectory() as tmp:
            root = workspace(
                tmp,
                **{
                    "docs__dispositions__v1..v2.md": (
                        "The input said:\n\n"
                        "````text\n"
                        "Evidence: scripts/sample_module.py:4\n"
                        "`scripts/sample_module.py:4`\n"
                        "````\n\n"
                        "and this record does not repeat it.\n"
                    )
                },
            )

            self.assertEqual(messages(root), [])

    def test_a_yaml_subject_has_no_fences_and_is_read_whole(self) -> None:
        # The fence rule is CommonMark's, so it applies to Markdown. A registry holding
        # a line citation inside a quoted scalar is still a line citation.
        with TemporaryDirectory() as tmp:
            root = workspace(
                tmp,
                **{"development-knowns.yaml": '    evidence: "see `PROJECT.md:5`"\n'},
            )

            self.assertIn("cites a line", messages(root)[0])


class SymbolCitations(unittest.TestCase):
    def test_a_symbol_the_module_defines_passes(self) -> None:
        for symbol in ("reads_whole", "Reader", "CONSTANT"):
            with self.subTest(symbol=symbol), TemporaryDirectory() as tmp:
                root = workspace(tmp, **{"AGENTS.md": f"Asked through `sample_module.{symbol}`.\n"})

                self.assertEqual(messages(root), [])

    def test_a_symbol_the_module_does_not_define_is_reported(self) -> None:
        with TemporaryDirectory() as tmp:
            root = workspace(tmp, **{"AGENTS.md": "Asked through `sample_module.section`.\n"})

            found = messages(root)

            self.assertEqual(len(found), 1, found)
            self.assertIn("names no top-level symbol", found[0])

    def test_a_filename_is_not_a_symbol_citation(self) -> None:
        # `evidence_currency.py` reads as module.symbol to any pattern that does not
        # know the suffixes, and every record cites files that way.
        with TemporaryDirectory() as tmp:
            root = workspace(tmp, **{"AGENTS.md": "In `sample_module.py` and `PROJECT.md`.\n"})

            self.assertEqual(messages(root), [])

    def test_a_dotted_name_from_outside_this_tree_is_not_judged(self) -> None:
        # A standard-library or third-party call is not a claim about this repository,
        # and answering about it would make the check refuse ordinary prose.
        with TemporaryDirectory() as tmp:
            root = workspace(
                tmp,
                **{"AGENTS.md": "Owned by `shlex.shlex`, read by `yaml.safe_load`.\n"},
            )

            self.assertEqual(messages(root), [])

    def test_a_member_the_class_defines_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = workspace(tmp, **{"AGENTS.md": "Reached by `sample_module.Reader.read`.\n"})

            self.assertEqual(messages(root), [])

    def test_a_member_the_class_does_not_define_is_reported(self) -> None:
        # The shape of the defect that prompted the rule was a wrong function name in a
        # cell asserting a closure had been verified. A three-part citation went
        # unmatched by the first pattern, so this whole class was unchecked.
        with TemporaryDirectory() as tmp:
            root = workspace(tmp, **{"AGENTS.md": "Reached by `sample_module.Reader.require`.\n"})

            found = messages(root)

            self.assertEqual(len(found), 1, found)
            self.assertIn("names no member of Reader", found[0])


class EntryPoint(unittest.TestCase):
    def run_main(self, root: Path) -> tuple[int, str, str]:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = check_citations.main(["--root", str(root)])
        return code, out.getvalue(), err.getvalue()

    def test_a_clean_workspace_passes_and_says_what_it_read(self) -> None:
        with TemporaryDirectory() as tmp:
            root = workspace(tmp, **{"AGENTS.md": "Asked through `sample_module.reads_whole`.\n"})

            code, out, _ = self.run_main(root)

        self.assertEqual(code, 0, out)
        self.assertIn("citations in", out)

    def test_a_defect_fails_the_entry_point_and_names_the_place(self) -> None:
        with TemporaryDirectory() as tmp:
            root = workspace(tmp, **{"AGENTS.md": "\n\nSee `PROJECT.md:5`.\n"})

            code, _, err = self.run_main(root)

        self.assertEqual(code, 1)
        self.assertIn("AGENTS.md:3", err)

    def test_this_repository_passes_its_own_check(self) -> None:
        self.assertEqual(check_citations.check(check_citations.ROOT), [])


if __name__ == "__main__":
    unittest.main()
