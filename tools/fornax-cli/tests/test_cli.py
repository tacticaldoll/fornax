from __future__ import annotations

import json
import re
import sys
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from fornax_cli import cli


DEPENDENCIES = re.compile(r"^dependencies\s*=\s*\[(.*?)^\]", re.MULTILINE | re.DOTALL)
REQUIREMENT = re.compile(r'"([^"]+)"')


def pins(lines: list[str]) -> dict[str, str]:
    """Map package name to exact version for every ``name==version`` line given."""
    found = {}
    for line in lines:
        name, separator, version = line.strip().strip('",').partition("==")
        if separator:
            found[name.strip()] = version.strip()
    return found


class FornaxCliTests(unittest.TestCase):
    def test_source_checkout_version_falls_back_to_workspace_manifest(self) -> None:
        manifest = json.loads(
            (cli.WORKSPACE_ROOT / "distribution.json").read_text(
                encoding="utf-8"
            )
        )

        with patch.object(cli, "version", side_effect=cli.PackageNotFoundError):
            self.assertEqual(cli.workspace_version(), manifest["version"])

    def test_installed_cli_uses_build_metadata_version(self) -> None:
        with patch.object(cli, "version", return_value="9.8.7"):
            self.assertEqual(cli.workspace_version(), "9.8.7")

    def test_policy_contains_only_fornax_distribution_choices(self) -> None:
        self.assertEqual(cli.FORNAX_POLICY.identity, "fornax")
        self.assertEqual(cli.FORNAX_POLICY.prefix, "fornax-")
        self.assertEqual(cli.FORNAX_POLICY.provenance_file, ".fornax-install.json")

    def test_validation_commands_run_under_this_interpreter(self) -> None:
        # A bare "python3" is whatever sits on PATH, which is neither guaranteed to
        # satisfy .python-version nor to import what the validator needs.
        self.assertTrue(cli.FORNAX_POLICY.validation_commands)

        for command in cli.FORNAX_POLICY.validation_commands:
            with self.subTest(command=command):
                self.assertEqual(command[0], sys.executable)

    def test_shared_dependencies_match_the_maintenance_pins(self) -> None:
        # Snapshot validation runs the workspace validator, so anything the validator
        # imports has to be declared here too. Where both files name a package they
        # must name the same version, or one pinned tag validates differently between
        # runs. Only the overlap is compared, so an unrelated maintenance dependency
        # does not become a CLI dependency by accident.
        declared = DEPENDENCIES.search(
            (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8")
        )

        if declared is None:
            self.fail("pyproject.toml must declare a dependencies array")

        cli = pins(REQUIREMENT.findall(declared.group(1)))
        maintenance = pins(
            (Path(__file__).resolve().parents[3] / "requirements-maintenance.txt")
            .read_text(encoding="utf-8")
            .splitlines()
        )
        shared = cli.keys() & maintenance.keys()

        self.assertTrue(shared, "no dependency is shared, so this asserts nothing")
        for name in sorted(shared):
            with self.subTest(name=name):
                self.assertEqual(cli[name], maintenance[name])

    def test_main_binds_workspace_version_and_policy(self) -> None:
        with patch.object(cli, "engine_main", return_value=0) as engine:
            self.assertEqual(cli.main(["hosts"]), 0)

        self.assertEqual(engine.call_args.args, (["hosts"],))
        self.assertEqual(engine.call_args.kwargs["program"], "fornax")
        self.assertEqual(
            engine.call_args.kwargs["version"], cli.workspace_version()
        )
        self.assertIs(engine.call_args.kwargs["distribution_policy"], cli.FORNAX_POLICY)
        self.assertIs(engine.call_args.kwargs["source_provider"], cli.release_source)

    def test_release_source_binds_remote_tag_and_manifest_version(self) -> None:
        materialized = object()
        with (
            patch.object(cli, "workspace_version", return_value="0.1.0"),
            patch.object(cli, "GitRelease") as release_type,
        ):
            release_type.return_value.materialize.return_value = materialized

            self.assertIs(cli.release_source(), materialized)

        release_type.assert_called_once_with(
            remote=cli.FORNAX_REMOTE,
            tag="v0.1.0",
            policy=cli.FORNAX_POLICY,
            expected_version="0.1.0",
            version_manifest="distribution.json",
        )

    def test_fornax_parser_rejects_config_and_local_source(self) -> None:
        for argv in (["config"], ["deploy", "--source", "/workspace"]):
            with self.subTest(argv=argv):
                with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
                    cli.main(argv)


if __name__ == "__main__":
    unittest.main()
