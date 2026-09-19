from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import runtime_contract


PINNED = {"markdown-it-py": "4.2.0"}


def satisfied(name: str) -> str | None:
    return PINNED.get(name)


class RuntimeContractTests(unittest.TestCase):
    def write_contract(self, root: Path, python_version: str, ruff_version: str) -> None:
        workflow = root / ".github" / "workflows" / "validate.yml"
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text("        run: echo build\n", encoding="utf-8")
        (root / ".python-version").write_text(python_version + "\n", encoding="utf-8")
        (root / "ruff.toml").write_text(
            f'target-version = "{ruff_version}"\n', encoding="utf-8"
        )
        (root / "requirements-maintenance.txt").write_text(
            "markdown-it-py==4.2.0\n", encoding="utf-8"
        )

    def check(self, root: Path, **kwargs) -> list[str]:
        kwargs.setdefault("installed", satisfied)
        return runtime_contract.check(root, **kwargs)

    def test_matching_runtime_and_ruff_target_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")

            errors = self.check(root)

        self.assertEqual(errors, [])

    def test_mismatched_ruff_target_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py38")

            errors = self.check(root)

        self.assertEqual(
            errors,
            ["ruff.toml target-version must be py310 to match .python-version"],
        )

    def test_an_interpreter_below_the_declared_floor_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")

            errors = self.check(root, running=(3, 8))

        self.assertEqual(len(errors), 1)
        self.assertIn("requires Python 3.10 or newer", errors[0])
        self.assertIn("this interpreter is 3.8", errors[0])
        self.assertIn("README.md", errors[0])

    def test_an_interpreter_at_or_above_the_floor_passes(self) -> None:
        for running in ((3, 10), (3, 12), (4, 0)):
            with self.subTest(running=running), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write_contract(root, "3.10", "py310")

                self.assertEqual(self.check(root, running=running), [])

    def test_invalid_or_missing_declarations_fail_cleanly(self) -> None:
        cases = (
            ("3.10.1", 'target-version = "py310"\n', ".python-version must contain major.minor"),
            ("3.10", "line-length = 100\n", "ruff.toml must declare one target-version"),
        )
        for python_version, ruff_text, message in cases:
            with self.subTest(message=message), TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / ".python-version").write_text(
                    python_version + "\n", encoding="utf-8"
                )
                (root / "ruff.toml").write_text(ruff_text, encoding="utf-8")

                errors = self.check(root)

            self.assertIn(message, errors)

    def test_a_pinned_library_at_another_version_fails(self) -> None:
        # An environment holding a different version satisfies the floor and then
        # validates the workspace with a parser the pins do not name.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")

            errors = self.check(root, installed=lambda name: "3.0.0")

        self.assertEqual(len(errors), 1)
        self.assertIn("pinned at 4.2.0 but 3.0.0 is installed", errors[0])
        self.assertIn("README.md", errors[0])

    def test_a_pinned_library_that_is_absent_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")

            errors = self.check(root, installed=lambda name: None)

        self.assertEqual(len(errors), 1)
        self.assertIn("is not installed", errors[0])

    def test_a_requirements_file_pinning_nothing_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_contract(root, "3.10", "py310")
            (root / "requirements-maintenance.txt").write_text(
                "# only a comment\n", encoding="utf-8"
            )

            errors = self.check(root)

        self.assertEqual(
            errors, ["requirements-maintenance.txt must pin at least one name==version"]
        )


class DeclaredPinTests(unittest.TestCase):
    def test_a_declaration_is_read_whole_or_reported(self) -> None:
        # Form after form of this matcher shipped, each wrong in the same direction.
        # `[^\\s;#]+` ran past `|`, and the version alphabet that replaced it stopped
        # there and kept the prefix — turning `0.16.1|x`, which failed its comparison
        # loudly, into `0.16.1`, which passes it. Neither is a wider alphabet away: a
        # prefix match cannot tell a version from the start of something else.
        for line, expected, malformed in (
            ("ruff==0.16.1", {"ruff": "0.16.1"}, []),
            ("ruff==0.16.1  # comment", {"ruff": "0.16.1"}, []),
            ('ruff==0.16.1; python_version>"3.9"', {"ruff": "0.16.1"}, []),
            ('  "markdown-it-py==4.2.0",', {"markdown-it-py": "4.2.0"}, []),
            # Near-miss sharing the accepted prefix: it must not become the prefix.
            ("ruff==0.16.1|x", {}, ["ruff==0.16.1|x"]),
            ("ruff==0.16.1>y", {}, ["ruff==0.16.1>y"]),
            ("ruff==x.y.z", {}, ["ruff==x.y.z"]),
            # pip starts a comment at a `#` beginning a word. Cutting at the first one
            # anywhere reintroduced the truncation this test exists to stop.
            ("ruff==0.16.1#x", {}, ["ruff==0.16.1#x"]),
            # Valid alternate spelling: PEP 440 admits `_` in a local version, which
            # the alphabet omitted and therefore truncated to a version that installs.
            ("tool==1.0+ubuntu_1", {"tool": "1.0+ubuntu_1"}, []),
            ("tool==1.0.*", {"tool": "1.0.*"}, []),
            # Spellings PEP 508 admits that the hand-written matcher rejected: an
            # extras list, and whitespace around the operator.
            ("tool [extra] ==1.0", {"tool": "1.0"}, []),
            ("tool == 1.0", {"tool": "1.0"}, []),
            # Not a pin declaration at all, so not this function's to report.
            ("-r base.txt", {}, []),
            ("ruff>=0.16", {}, []),
            ("# ruff==nonsense", {}, []),
        ):
            with self.subTest(line=line):
                self.assertEqual(runtime_contract.pins(line), (expected, malformed))

    def test_a_malformed_declaration_fails_the_check(self) -> None:
        # The prefix form let this reach the comparison as `1.2.3`, match the installed
        # release and answer clean. It has to surface as an error, not as a silent pass.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".python-version").write_text("3.10\n", encoding="utf-8")
            (root / "ruff.toml").write_text('target-version = "py310"\n', encoding="utf-8")
            (root / "requirements-maintenance.txt").write_text(
                "tool==1.2.3|x\n", encoding="utf-8"
            )
            workflow = root / ".github" / "workflows" / "validate.yml"
            workflow.parent.mkdir(parents=True, exist_ok=True)
            workflow.write_text("        run: pip install tool==1.2.3\n", encoding="utf-8")

            errors = runtime_contract.check(
                root, running=(3, 10), installed=lambda name: "1.2.3"
            )

            self.assertTrue(any("which is not a pin" in error for error in errors), errors)


class DirectPinTests(unittest.TestCase):
    """A pin counts where the workflow installs, and nowhere else it merely appears.

    The first form read the file's text, so a version in a comment, a step `name` or an
    `env` value was reported as a pin the workflow installs. All three were measured, and
    none of them is an install: where a pin sits is YAML's question, and PyYAML answers
    it. These four cases are the accepted side and its three near misses.
    """

    def _workflow(self, step: str) -> str:
        return "jobs:\n  a:\n    steps:\n" + step

    def test_a_pin_in_a_run_is_stated(self) -> None:
        stated, unreadable = runtime_contract.direct_pins(
            self._workflow("      - run: pip install tool==9.9.9\n")
        )

        self.assertEqual(stated, [("tool", "9.9.9")])
        self.assertEqual(unreadable, [])

    def test_a_pin_in_a_comment_is_not_stated(self) -> None:
        stated, _ = runtime_contract.direct_pins(
            self._workflow("      # tool==9.9.9\n      - run: echo ok\n")
        )

        self.assertEqual(stated, [])

    def test_a_pin_in_a_step_name_is_not_stated(self) -> None:
        stated, _ = runtime_contract.direct_pins(
            self._workflow("      - name: tool==9.9.9\n        run: echo ok\n")
        )

        self.assertEqual(stated, [])

    def test_a_pin_in_an_env_value_is_not_stated(self) -> None:
        stated, _ = runtime_contract.direct_pins(
            self._workflow("      - env:\n          N: tool==9.9.9\n        run: echo ok\n")
        )

        self.assertEqual(stated, [])

    def test_a_quoted_pin_is_stated(self) -> None:
        # Quoting holds this pin together and splitting on whitespace lost it entirely —
        # three tokens, each no requirement at all, while pip installs the one it spells.
        # That is the direction this must not fail in, and `shlex` owns the question.
        stated, unreadable = runtime_contract.direct_pins(
            self._workflow('      - run: pip install "tool == 1.0"\n')
        )

        self.assertEqual(stated, [("tool", "1.0")])
        self.assertEqual(unreadable, [])

    def test_a_token_packaging_refuses_is_reported(self) -> None:
        # The channel the return type and the caller already promised. Dropping it left
        # a pin-shaped token passing in silence.
        stated, unreadable = runtime_contract.direct_pins(
            self._workflow("      - run: pip install tool==\n")
        )

        self.assertEqual(stated, [])
        self.assertTrue(unreadable)

    def test_a_command_the_lexer_cannot_finish_is_reported(self) -> None:
        stated, unreadable = runtime_contract.direct_pins(
            self._workflow('      - run: echo "unbalanced\n')
        )

        self.assertEqual(stated, [])
        self.assertTrue(unreadable)

    def test_a_run_that_is_not_a_string_is_reported(self) -> None:
        # The third answer: absent, stated, and a value this cannot read.
        stated, unreadable = runtime_contract.direct_pins(
            self._workflow("      - run:\n          a: b\n")
        )

        self.assertEqual(stated, [])
        self.assertTrue(unreadable)


class SharedPinTests(unittest.TestCase):
    """The CLI declares the libraries the workspace validator imports, because
    snapshot validation shells out to it. Where both files name a package they must
    name the same version, or one pinned tag validates differently between runs.

    This lives here rather than beside the CLI because it reads both declarations and needs
    nothing the deployment engine provides — and beside the CLI it ran only after
    that engine installed, so the invariant went unchecked whenever it did not.
    """

    def test_shared_dependencies_name_the_same_version(self) -> None:
        root = Path(__file__).resolve().parents[2]
        maintenance, loose = runtime_contract.pins(
            (root / "requirements-maintenance.txt").read_text(encoding="utf-8")
        )
        cli, unread = runtime_contract.pins(
            (root / "tools/fornax-cli/pyproject.toml").read_text(encoding="utf-8")
        )
        self.assertEqual((loose, unread), ([], []))
        shared = maintenance.keys() & cli.keys()

        self.assertTrue(shared, "no dependency is shared, so this asserts nothing")
        for name in sorted(shared):
            with self.subTest(name=name):
                self.assertEqual(cli[name], maintenance[name])


if __name__ == "__main__":
    unittest.main()
