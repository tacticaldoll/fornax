# Deployment Channels

Fornax assigns one **authoritative deployment channel** to each host and scope. A host may discover
skills through several surfaces, but the CLI must install Fornax through only the authoritative
channel and report other visible copies as conflicts. It must never delete an installation whose
ownership it cannot prove.

Prefer an official plugin or extension when it carries the complete skill package and has a stable
install, update, uninstall, and verification flow. Otherwise use the host's official personal
skills directory. "Plugin preferred" is not "plugin only": some hosts expose Agent Skills primarily
through directory discovery.

The CLI supports formal deployment only and exposes no local source option. Its workspace version
selects the matching tag from the canonical Fornax remote. Deployment proceeds only when the tag,
remote default HEAD, and manifest version agree on one commit. Plugin marketplaces and extensions
install from that verified remote; directory channels receive independent copies from a detached,
engine-managed snapshot of the same commit, never from a working checkout and never through
symlinks. Local host development is deliberately outside the `fornax` CLI.

## Capability matrix

| Host | Authoritative channel | Other discovery surfaces to inspect | Support | Basis |
|---|---|---|---|---|
| Claude Code | plugin | not found | stable | locally verified plugin workflow |
| Codex | plugin | `~/.codex/skills`, `~/.agents/skills` | stable | locally verified plugin; personal and shared Agent Skills observed |
| Gemini CLI | extension | `~/.gemini/skills`, `~/.agents/skills` | beta | [extension](https://geminicli.com/docs/extensions/reference/) and [Agent Skills](https://geminicli.com/docs/cli/using-agent-skills/) docs |
| Antigravity | `~/.gemini/config/skills` | plugin/extension behavior unverified | experimental | locally verified only |
| GitHub Copilot CLI | `~/.copilot/skills` | `~/.agents/skills`, plugin directories | beta | [official Copilot CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference) |
| Cline | `~/.cline/skills` | project `.cline/skills` and compatibility locations | beta | [official Cline Skills docs](https://docs.cline.bot/customization/skills) |
| Cursor | `~/.cursor/skills` | plugin behavior unverified | experimental | locally simulated only |
| OpenCode | config `skills/` directory | legacy `~/.opencode/skills` | experimental | locally simulated only |

The executable host profiles live in the independent
[`agent-skill-deployer`](https://github.com/tacticaldoll/agent-skill-deployer) engine. This document
records Fornax's selected policy; compatibility mechanics and their tests are released by the engine.

## Conflict states

- **duplicate-source** — more than one Fornax source is visible to the same host and scope.
- **non-authoritative-source** — Fornax is visible, but only through a channel that policy does not
  designate as authoritative for that host.
- **shadowed** — a lower-precedence copy exists but another source wins name resolution. Detection
  is deferred until each host's precedence can be verified.
- **stale** — the authoritative installation is at a different source commit.
- **foreign-source** — a matching installation has provenance for another source or target, so the
  CLI must never mutate it.
- **unverified-ownership** — a legacy path has no valid Fornax provenance; mutation requires an
  explicit one-time adoption decision.

Pre-provenance directory copies are reported as `legacy-unverified`. They fail closed by default and
may be replaced only through explicit `--adopt-legacy`; foreign provenance is never adopted.
Schema 2 provenance binds ownership to the resolved source and physical target. The initiating host
is retained as audit metadata but is not an ownership key, because a directory may have several
legitimate consumer hosts.
Schema 1 is upgraded automatically only when its source and host match and the capability matrix
proves the target has exactly one consumer. Shared or ambiguous schema-1 installs remain
`legacy-unverified` and require explicit adoption.

## Ownership boundary

Fornax owns its distribution identity, namespace, provenance name, validators, and choice of one
authoritative channel per host. `agent-skill-deployer` owns host discovery, native lifecycle
commands, inventory, conflict classification, staged directory swaps, reconciliation, verification,
and deployment state. The `fornax` command is only the adapter between those boundaries.
