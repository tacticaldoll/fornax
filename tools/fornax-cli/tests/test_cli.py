from __future__ import annotations

import json
import unittest
from contextlib import redirect_stderr
from io import StringIO
from unittest.mock import patch

from fornax_cli import cli


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
