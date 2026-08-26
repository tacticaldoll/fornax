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
        # Two forms of this matcher shipped and both were wrong in the same direction.
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


class WorkflowPinTests(unittest.TestCase):
    def workspace(self, root: Path, workflow: str | None) -> None:
        (root / ".python-version").write_text("3.10\n", encoding="utf-8")
        (root / "ruff.toml").write_text('target-version = "py310"\n', encoding="utf-8")
        (root / "requirements-maintenance.txt").write_text("tool==1.2.3\n", encoding="utf-8")
        if workflow is not None:
            path = root / ".github" / "workflows" / "validate.yml"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(workflow, encoding="utf-8")

    def check(self, root: Path) -> list[str]:
        return runtime_contract.check(root, running=(3, 10), installed=lambda name: "1.2.3")

    def test_an_absent_workflow_fails_rather_than_reading_as_clean(self) -> None:
        # Zero seams is legitimate; zero CI is not, in a repository PROJECT.md calls
        # enforced by CI. Borrowing the clean-on-absence answer here would let deleting
        # the workflow pass every gate.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root, None)

            errors = self.check(root)

            self.assertEqual(len(errors), 1, errors)
            self.assertIn("validate.yml", errors[0])

    def test_a_workflow_pin_matching_the_requirements_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root, "        run: pip install tool==1.2.3\n")

            self.assertEqual(self.check(root), [])

    def test_a_workflow_pinning_another_release_fails(self) -> None:
        # The gate would otherwise check the workspace with a linter CI does not run.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root, "        run: pip install tool==9.9.9\n")

            errors = self.check(root)

            self.assertEqual(len(errors), 1, errors)
            self.assertIn("installs tool==9.9.9", errors[0])
            self.assertIn("pins 1.2.3", errors[0])

    def test_every_spelling_of_an_inline_pin_is_compared(self) -> None:
        # Anchoring on "pip install " missed --upgrade, a quoted spec, and every package
        # after the first on one line — three ways a disagreeing pin passed unread.
        spellings = (
            "        run: python -m pip install tool==9.9.9\n",
            "        run: pip install --upgrade tool==9.9.9\n",
            '        run: pip install "tool==9.9.9"\n',
            "        run: pip install other==2.0.0 tool==9.9.9\n",
            "        run: pip3 install tool==9.9.9\n",
            "        run: |\n          pip install \\\\\n            tool==9.9.9\n",
            "        run: >\n          pip install\n          tool==9.9.9\n",
            "        run: |\n          pip install \\\\\n"
            "            --upgrade \\\\\n            tool==9.9.9\n",
        )
        for workflow in spellings:
            with self.subTest(workflow=workflow.strip()), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.workspace(root, workflow)

                errors = self.check(root)

                self.assertTrue(any("tool==9.9.9" in error for error in errors), errors)

    def test_text_that_is_not_an_install_is_not_a_pin(self) -> None:
        # The control the prefix-free rewrite lacked. Dropping the command anchor read
        # raw YAML, so a comment and an echo became installs.
        for line in (
            "        # example: tool==9.9.9\n",
            "        run: echo tool==9.9.9\n",
            "        run: pip download tool==9.9.9\n",
            "        run: echo \\\\\n          tool==9.9.9\n",
            "        run: >\n          echo\n          tool==9.9.9\n",
            # Nothing runs an environment variable, in either scalar form. Reading
            # every scalar in the file made installation text under `env:` a pin.
            "      - env:\n          HELP: pip install tool==9.9.9\n",
            "      - env:\n          HELP: >\n            pip install tool==9.9.9\n",
            "      - name: pip install tool==9.9.9\n",
            "      - with:\n          args: pip install tool==9.9.9\n",
        ):
            with self.subTest(line=line.strip()), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.workspace(root, line)

                self.assertEqual(self.check(root), [])

    def test_a_pin_after_a_vcs_url_fragment_is_still_compared(self) -> None:
        # `#` starts a shell comment only at the start of a word. Cutting at the first
        # one anywhere threw away the rest of the command, so this pin went unread and
        # a workflow installing 9.9.9 against a requirements file pinning 1.2.3 was
        # reported clean — the exact miss this check exists to catch.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(
                root,
                '        run: pip install "a @ git+https://h/r.git@v1'
                '#subdirectory=t" tool==9.9.9\n',
            )

            errors = self.check(root)

            self.assertEqual(len(errors), 1, errors)
            self.assertIn("9.9.9", errors[0])

    def test_a_workflow_spec_that_cannot_be_read_whole_is_reported(self) -> None:
        # The terminator list this replaced ended the version at `"` and `;`, so a
        # quoted `tool==1.2.3|x` reached the comparison as `1.2.3` and matched. There
        # is no shorter answer available now: it is read whole or reported unread.
        for command, unreadable in (
            ('        run: pip install "tool==1.2.3|x"\n', "tool==1.2.3|x"),
            ("        run: pip install tool==1.2.3#x\n", "tool==1.2.3#x"),
            ("        run: pip install 'unbalanced\n", "unbalanced"),
        ):
            with self.subTest(command=command.strip()), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.workspace(root, command)

                errors = self.check(root)

                self.assertEqual(len(errors), 1, errors)
                self.assertIn(unreadable, errors[0])
                self.assertIn("cannot be read", errors[0])

    def test_every_order_of_a_block_header_is_read(self) -> None:
        # YAML puts the indentation and chomping indicators in either order, so `>2-`
        # and `>-2` are the same header. Matching one order sent the other down the
        # plain-scalar path, where the invocation and its pin became two commands and
        # the pin disappeared with no error at all.
        for header in (">", ">-", ">+", ">2", ">2-", ">-2"):
            with self.subTest(header=header), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.workspace(
                    root, f"        run: {header}\n          pip install\n          tool==9.9.9\n"
                )

                errors = self.check(root)

                self.assertEqual(len(errors), 1, errors)
                self.assertIn("9.9.9", errors[0])

    def test_every_scalar_category_a_workflow_may_use(self) -> None:
        # The category the previous round left untested. A plain scalar folds onto its
        # more-indented lines, which the docstring said and the code did not: the body
        # went through the shell's backslash rule, so `pip install` and `tool==9.9.9`
        # became two commands and the pin was lost with no error.
        for label, workflow in (
            ("plain inline", "        run: pip install tool==9.9.9\n"),
            ("plain multiline", "        run: pip install\n          tool==9.9.9\n"),
            ("plain over three", "        run: pip\n          install\n          tool==9.9.9\n"),
            ("folded", "        run: >\n          pip install\n          tool==9.9.9\n"),
            ("folded indented", "        run: >2-\n          pip install\n          tool==9.9.9\n"),
            ("literal", "        run: |\n          pip install tool==9.9.9\n"),
            (
                "literal continued",
                "        run: |\n          pip install \\\n            tool==9.9.9\n",
            ),
            ("double quoted", '        run: "pip install tool==9.9.9"\n'),
            ("single quoted", "        run: 'pip install tool==9.9.9'\n"),
        ):
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.workspace(root, workflow)

                errors = self.check(root)

                self.assertEqual(len(errors), 1, f"{label}: {errors}")
                self.assertIn("9.9.9", errors[0])

    def test_quoting_this_is_not_sure_of_is_reported_not_guessed(self) -> None:
        # Total, not complete: a quoted scalar carrying an escape or spanning lines is
        # YAML this reader does not resolve, and saying so beats stripping the quotes
        # and hoping. Handing the quotes through made the whole command one shell word.
        for value in ('"echo \\"hi\\""', '"pip install'):
            with self.subTest(value=value), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.workspace(root, f"        run: {value}\n          tool==9.9.9\n")

                errors = self.check(root)

                self.assertEqual(len(errors), 1, errors)
                self.assertIn("cannot be read", errors[0])

    def test_a_blank_line_in_a_folded_scalar_is_a_paragraph_break(self) -> None:
        # YAML folds a blank line into a newline, not a space, and keeps the breaks
        # around a line indented past the block. Joining everything with spaces read
        #     run: >
        #       pip install
        #
        #       tool==9.9.9
        # as one invocation and reported a pin, when the workflow runs `pip install`
        # with no package and then a command named `tool==9.9.9`. A workflow that
        # installs nothing was read as one that installs the right thing.
        for label, body in (
            ("blank line", "          pip install\n\n          tool==9.9.9\n"),
            ("more indented", "          pip install\n            tool==9.9.9\n"),
        ):
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.workspace(root, f"        run: >\n{body}")

                self.assertEqual(self.check(root), [])

    def test_a_plain_scalar_breaks_at_a_blank_line_too(self) -> None:
        # The value on the key's line is the scalar's first line, so it folds with the
        # rest. Pasting it onto the front of the folded result instead let a blank line
        # after it be swallowed.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root, "        run: pip install\n\n          tool==9.9.9\n")

            self.assertEqual(self.check(root), [])

    def test_pip_is_an_install_only_in_command_position(self) -> None:
        # Searching the words for `pip install` made echoed text an install and its
        # argument a pin the workflow was said to carry.
        for label, command in (
            ("echoed", "echo pip install tool==9.9.9"),
            ("another program", "pip-audit install tool==9.9.9"),
            ("not the install verb", "pip download tool==9.9.9"),
        ):
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.workspace(root, f"        run: {command}\n")

                self.assertEqual(self.check(root), [])

    def test_an_install_in_any_command_position_is_read(self) -> None:
        for label, command in (
            ("after an operator", "echo hi && pip install tool==9.9.9"),
            ("after assignments", "PIP_NO_CACHE=1 pip install tool==9.9.9"),
            ("through the module", "python3 -m pip install tool==9.9.9"),
            ("by path", ".venv/bin/pip install tool==9.9.9"),
        ):
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.workspace(root, f"        run: {command}\n")

                errors = self.check(root)

                self.assertEqual(len(errors), 1, f"{label}: {errors}")
                self.assertIn("9.9.9", errors[0])

    def test_a_run_value_this_cannot_resolve_is_reported(self) -> None:
        # The same hole the token readers had, one layer up: a `run:` value read as
        # something smaller and plausible rather than reported as unread. An alias has
        # no resolution here and a malformed header is not a header.
        for value in (">x", "*deploy", "&setup"):
            with self.subTest(value=value), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.workspace(root, f"        run: {value}\n          pip install tool==9.9.9\n")

                errors = self.check(root)

                self.assertEqual(len(errors), 1, errors)
                self.assertIn(value, errors[0])
                self.assertIn("cannot be read", errors[0])

    def test_a_requirements_file_reference_is_not_a_pin(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root, "        run: pip install -r requirements-maintenance.txt\n")

            self.assertEqual(self.check(root), [])

    def test_a_workflow_pin_the_requirements_never_declared_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.workspace(root, "        run: pip install other==2.0.0\n")

            errors = self.check(root)

            self.assertEqual(len(errors), 1, errors)
            self.assertIn("does not declare", errors[0])

    def test_this_repository_agrees_with_its_own_workflow(self) -> None:
        errors = [
            error
            for error in runtime_contract.check(runtime_contract.ROOT)
            if "validate.yml" in error
        ]

        self.assertEqual(errors, [])


class SharedPinTests(unittest.TestCase):
    """The CLI declares the libraries the workspace validator imports, because
    snapshot validation shells out to it. Where both files name a package they must
    name the same version, or one pinned tag validates differently between runs.

    This lives here rather than beside the CLI because it reads two files and needs
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
