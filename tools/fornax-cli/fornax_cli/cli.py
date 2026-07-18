"""Bind the generic deployment engine to the Fornax workspace policy."""

from __future__ import annotations

import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
FORNAX_REMOTE = "https://github.com/tacticaldoll/fornax"

from agent_skill_deployer.cli import main as engine_main  # noqa: E402
from agent_skill_deployer.core import DistributionPolicy, GitRelease, Source  # noqa: E402


def workspace_version() -> str:
    try:
        return version("fornax-cli")
    except PackageNotFoundError:
        pass
    manifest = WORKSPACE_ROOT / "distribution.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    manifest_version = data.get("version")
    if not isinstance(manifest_version, str) or not manifest_version:
        raise RuntimeError(f"workspace version is missing from {manifest}")
    return manifest_version


FORNAX_POLICY = DistributionPolicy(
    identity="fornax",
    prefix="fornax-",
    provenance_file=".fornax-install.json",
    display_name="Fornax",
    marketplace="fornax",
    plugin="fornax",
    validation_commands=(
        ("python3", "scripts/validate_skills.py"),
        (
            "python3",
            "scripts/validate_skills.py",
            "--skills-path",
            "templates",
            "--allow-template-placeholders",
        ),
    ),
)


def release_source() -> Source:
    release_version = workspace_version()
    return GitRelease(
        remote=FORNAX_REMOTE,
        tag=f"v{release_version}",
        policy=FORNAX_POLICY,
        expected_version=release_version,
        version_manifest="distribution.json",
    ).materialize()


def main(argv: list[str] | None = None) -> int:
    return engine_main(
        argv,
        program="fornax",
        version=workspace_version(),
        distribution_policy=FORNAX_POLICY,
        source_provider=release_source,
    )
