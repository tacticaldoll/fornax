# fornax CLI

The `fornax` command is the thin Fornax policy adapter over
[`agent-skill-deployer`](https://github.com/tacticaldoll/agent-skill-deployer).
The engine owns host discovery, inventory, deployment channels, provenance,
reconciliation, and verification. This package owns only the Fornax command name,
namespace, provenance identity, validators, release source, and workspace version.

The CLI has no independent version. Build metadata is read from the release's
vendor-neutral `distribution.json`, and runtime deployment is fixed to the matching
`v<version>` tag at `https://github.com/tacticaldoll/fornax`.

## Install the command

Install the tagged CLI persistently with `pipx`:

```sh
pipx install \
  "git+https://github.com/tacticaldoll/fornax.git@v0.1.0#subdirectory=tools/fornax-cli"

fornax deploy --dry-run
fornax deploy --all
```

## Run without installing

Use the exact same CLI and deployment pipeline without leaving a persistent command:

```sh
pipx run \
  --spec "git+https://github.com/tacticaldoll/fornax.git@v0.1.0#subdirectory=tools/fornax-cli" \
  fornax deploy --all
```

Or with `uv`:

```sh
uvx \
  --from "git+https://github.com/tacticaldoll/fornax.git@v0.1.0#subdirectory=tools/fornax-cli" \
  fornax deploy --all
```

`pipx run` and `uvx` may cache their temporary environment, but they do not install a
permanent `fornax` command. They execute the same tagged package as the persistent
installation; there is no second deployment implementation.

## Commands

```sh
fornax hosts
fornax status
fornax doctor
fornax deploy --dry-run
fornax deploy --all
```

The Fornax CLI deliberately has no `config` command and accepts no `--source` path.
Local checkouts are development inputs and cannot become formal deployment sources.

## Formal release contract

Before inventory or deployment, the CLI:

1. Resolves its matching `v<version>` tag from the formal Fornax remote.
2. Requires the tag and remote default HEAD to identify the same commit, because native
   plugin hosts install from that remote.
3. Materializes a detached snapshot under
   `~/.cache/agent-skill-deployer/releases/fornax/<commit>`.
4. Requires the snapshot to be clean and its manifest version to equal the CLI version.
5. Uses that exact snapshot for validation and every directory-discovery host.

If any check fails, deployment stops before mutating a host. Native plugin hosts and
directory-copy hosts therefore cannot silently deploy different revisions. Installed
skills are managed copies with `.fornax-install.json`; none link to a workspace.

## Development

Development may use the engine and wrapper directly, but it is intentionally outside
the formal `fornax` command contract:

```sh
PYTHONPATH=/path/to/agent-skill-deployer:tools/fornax-cli \
  python3 -m unittest discover -s tools/fornax-cli/tests -v
```
