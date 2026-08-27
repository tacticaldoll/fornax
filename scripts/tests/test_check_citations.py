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
        "import yaml\n\n\nCONSTANT = 1\n\n\n"
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

    def test_a_line_citation_is_refused_without_backticks_and_by_any_suffix(self) -> None:
        """The first form asked for backticks and a suffix from a short list.

        So a path-and-line written as plain prose passed, and so did a `.js` path, under
        a message saying the form is refused. Capped at six letters it then passed
        `.markdown`, so the extension has no length rule, only an alphabetic one.
        """
        for text in (
            "bare scripts/foo.py:12 in prose\n",
            "`.opencode/plugins/fornax.js:12`\n",
            "see docs/review-record-contract.md:44\n",
        ):
            with self.subTest(text=text), TemporaryDirectory() as tmp:
                root = workspace(tmp, **{"AGENTS.md": text})

                found = messages(root)

                self.assertEqual(len(found), 1, found)
                self.assertIn("cites a line", found[0])

    def test_a_long_extension_is_still_a_line_citation(self) -> None:
        for text in ("See docs/spec.markdown:12 for it.\n", "And schema.proto3:12 too.\n"):
            with self.subTest(text=text), TemporaryDirectory() as tmp:
                root = workspace(tmp, **{"AGENTS.md": text})

                self.assertIn("cites a line", messages(root)[0])

    def test_a_url_authority_is_not_a_line_citation(self) -> None:
        """A host and a port read as a path and a line to the pattern alone.

        `https://example.com:443/path` yields `//example.com:443`, so refusing it would
        make the check reject ordinary prose — worse than the miss it was closing.
        """
        for text in (
            "Served at https://example.com:443/path today.\n",
            "Or http://x.invalid:8080/a for it.\n",
            # A network-path reference carries an authority and no scheme, and
            # markdown_links.local_target already reads this form as not ours.
            "Or //example.com:443/path for it.\n",
        ):
            with self.subTest(text=text), TemporaryDirectory() as tmp:
                root = workspace(tmp, **{"AGENTS.md": text})

                self.assertEqual(messages(root), [])

    def test_a_citation_inside_a_url_path_is_still_one(self) -> None:
        # Exempting the whole whitespace-bounded word let this escape with the port. A
        # path inside a URL's path is as much a path as anywhere.
        for text in (
            "At https://host.example/docs/file.py:12 today.\n",
            "At //host.example/docs/file.py:12 today.\n",
        ):
            with self.subTest(text=text), TemporaryDirectory() as tmp:
                root = workspace(tmp, **{"AGENTS.md": text})

                self.assertIn("cites a line", messages(root)[0])

    def test_a_version_is_not_a_line_citation(self) -> None:
        # The widened pattern requires an alphabetic extension. Without that, "Python
        # 3.10:1" reads as a path with extension "10" and a line number.
        with TemporaryDirectory() as tmp:
            root = workspace(tmp, **{"AGENTS.md": "Pinned at Python 3.10:1 of the matrix.\n"})

            self.assertEqual(messages(root), [])

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

    def test_a_module_the_standard_library_or_this_tree_accounts_for_passes(self) -> None:
        """`shlex` comes with the interpreter; `yaml` is imported by the sample module.

        Both are derived rather than asked of the environment: the stdlib set is static
        for the pinned interpreter, and the third-party names come from the import
        statements under `scripts/`. Asking the environment made the answer depend on
        what a local interpreter happened to have installed.
        """
        with TemporaryDirectory() as tmp:
            root = workspace(
                tmp,
                **{"AGENTS.md": "Owned by `shlex.shlex`, read by `yaml.safe_load`.\n"},
            )

            self.assertEqual(messages(root), [])

    def test_a_third_party_module_nothing_here_imports_is_reported(self) -> None:
        with TemporaryDirectory() as tmp:
            root = workspace(tmp, **{"AGENTS.md": "Fetched with `requests.get`.\n"})

            found = messages(root)

            self.assertEqual(len(found), 1, found)
            self.assertIn("not imported anywhere here", found[0])

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

    def test_a_module_name_that_resolves_nowhere_is_reported(self) -> None:
        """An unknown module was read as an external one, so a misspelling passed.

        A similarity threshold stood here first and caught a near-miss while passing
        every misspelling unlike enough to a real name — the same silence in a smaller
        range. Importability answers it with no threshold and no list: a real external
        module resolves, a mistyped internal one resolves nowhere.
        """
        for name in ("sampl_module", "smpl_mdl", "totally_unlike_anything_here"):
            with self.subTest(name=name), TemporaryDirectory() as tmp:
                root = workspace(tmp, **{"AGENTS.md": f"Asked through `{name}.reads_whole`.\n"})

                found = messages(root)

                self.assertEqual(len(found), 1, found)
                self.assertIn("not in the standard library", found[0])

    def test_a_test_module_is_a_module_here(self) -> None:
        # Reading only scripts/ made every citation into a test module unknown, and the
        # near-miss rule then reported it against its production sibling.
        with TemporaryDirectory() as tmp:
            root = workspace(tmp)
            (root / "scripts" / "tests").mkdir()
            (root / "scripts" / "tests" / "test_sample_module.py").write_text(
                "class Cases:\n    def test_one(self) -> None:\n        pass\n",
                encoding="utf-8",
            )
            (root / "AGENTS.md").write_text(
                "Covered by `test_sample_module.Cases.test_one`.\n", encoding="utf-8"
            )

            self.assertEqual(messages(root), [])


class ModuleIdentity(unittest.TestCase):
    def test_a_stem_naming_more_than_one_module_is_reported_once(self) -> None:
        """A dict keyed by stem lost one file and checked citations against the other."""
        with TemporaryDirectory() as tmp:
            root = workspace(tmp)
            (root / "scripts" / "tests").mkdir()
            (root / "scripts" / "tests" / "sample_module.py").write_text(
                "x = 1\n", encoding="utf-8"
            )
            (root / "AGENTS.md").write_text("Nothing cites anything.\n", encoding="utf-8")

            found = messages(root)

            self.assertEqual(len(found), 1, found)
            self.assertIn("names more than one module", found[0])

    def test_a_module_that_cannot_be_parsed_is_reported_as_that(self) -> None:
        """Three states shared one None, so an unreadable module read as a missing one."""
        with TemporaryDirectory() as tmp:
            root = workspace(tmp)
            (root / "scripts" / "broken_module.py").write_text("def f(:\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("Asked through `broken_module.f`.\n", encoding="utf-8")

            found = messages(root)

            self.assertEqual(len(found), 1, found)
            self.assertIn("could not be parsed", found[0])
            self.assertNotIn("names no", found[0])

    def test_an_unparseable_module_is_named_where_it_actually_sits(self) -> None:
        """The diagnostic composed `scripts/<stem>.py`, which is a guess about a path.

        A module under `scripts/tests/` was reported at a path that does not exist, in
        the diagnostic whose whole job is to say which file could not be read.
        """
        with TemporaryDirectory() as tmp:
            root = workspace(tmp)
            (root / "scripts" / "tests").mkdir()
            (root / "scripts" / "tests" / "broken_nested.py").write_text(
                "def f(:\n", encoding="utf-8"
            )
            (root / "AGENTS.md").write_text(
                "Asked through `broken_nested.f`.\n", encoding="utf-8"
            )

            found = messages(root)

            self.assertEqual(len(found), 1, found)
            self.assertIn("scripts/tests/broken_nested.py", found[0])

    def test_symbols_cannot_hold_both_a_mapping_and_a_reason(self) -> None:
        for names, reason in (({}, "unreadable"), (None, None)):
            with self.subTest(names=names, reason=reason):
                with self.assertRaises(ValueError):
                    check_citations.Symbols(names, reason)


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
