# Fornax — Project

What Fornax has **decided** and what it will **not** do, recorded so the calls are not re-litigated
by default (see the `audit-governance` skill). For what Fornax *is* — essence, naming, and voice — see
[docs/identity.md](docs/identity.md); for how to build and maintain skills, [AGENTS.md](AGENTS.md).

## Status

- Early stage. Every skill is `status: draft`, versioned `0.1.x`; nothing claims 1.0 maturity.
- Skills span four families: implementation, knowledge, decisions, meta.
- Public repo, enforced by CI and a pre-commit hook running `scripts/validate_skills.py`.

## Standing decisions

Settled; reopen only with a reason, not by default.

- **Skills read / plan / report; they do not edit or execute.** Output is refined context; execution
  is handed off. Skills work only with context that actually exists — they mark inference apart from
  fact, name what they did not check, and never fabricate.
- **Task-descriptive slugs.** Slugs are task-descriptive (`plan-implementation`, `map-codebase`, …)
  because manual `/fornax:<slug>` invocation is the load-bearing path — auto-triggering by
  `description` proved unreliable, and native per-skill aliases are unsupported across hosts, so the
  slug itself must carry the task name. The `/fornax:` prefix (from the plugin manifest, not the
  slug) namespaces against collisions.
- **Per-type output contract.** Workflow / artifact skills must produce a defined output; a
  stance / thinking-partner skill imposes none; reference is on-demand. A stance skill's "no artifact"
  is its declared contract, not an exception.
- **`family` is a flat field** (`implementation | knowledge | decisions | meta`), the single source
  for README grouping and the generated skill maps. The object-vs-meta and operation-kind
  distinctions are real but are *not* encoded as fields — nothing consumes them.
- **Enforcement is the structural floor only.** The validator checks structure (manifest fields,
  links, handoff targets, the `**Input**:` line, `family`); judgment (description shape, prose
  clarity) stays human. CI + the pre-commit hook run it.
- **forward ↔ reverse split.** `design-boundaries` designs boundaries forward; `map-codebase` / `plan-split` /
  `plan-repo-extract` read existing code; `plan-repo-extract` reconciles a forward blueprint against the recovered seam.
- **Rebranded `nlp-agent-skills` → Fornax** with fresh single-commit history; the old repo is kept as
  an archive.
- **No pull-request workflow**; commit and push directly. Commits and PRs omit AI attribution.
- **No per-skill host adapters.** Skills are host-neutral (the open Agent Skills standard); host
  specifics live once at the packaging layer (`.claude-plugin/`, `.codex-plugin/`, …), not in
  per-skill adapter files — those were ~90% boilerplate derivable from the manifest.
- **One authoritative deployment channel per host and scope.** Prefer an official plugin or
  extension when it carries the complete package; otherwise use the host's official skills
  directory. Inspect every discovery surface, report duplicates, and never infer ownership from a
  name prefix alone. "Plugin preferred" is deliberately not "plugin only."
- **The Fornax CLI performs formal deployment only.** It accepts no local source path. Its workspace
  version resolves the matching canonical Git tag, requires that tag, remote default HEAD, and
  manifest version to agree on one commit, then uses a managed detached snapshot for validation and
  directory hosts while native hosts use the verified remote. Local sources and host-development
  installs are outside the `fornax` CLI.
- **Host deployment mechanics live independently.** `agent-skill-deployer` owns host discovery,
  inventory, provenance-aware mutation, reconciliation, and verification. Fornax retains only a
  thin `fornax` policy adapter and takes its CLI version from the workspace release; the engine has
  its own release cadence.
- **Distribution structure is vendor-neutral.** `distribution.json` is the canonical collection
  identity and release version; host manifests are projections. New domain collections start from
  `agent-skills-distribution-template`, while the deployer keeps network-free neutral fixtures and
  no Fornax-specific test identity.

## Non-goals

- **Not an executor.** No editing code, running builds, or shipping — those are downstream of a
  skill's plan.
- **No blanket discipline machinery.** Hard-gates and rationalization tables are added per skill only
  on an observed failure, never corpus-wide by default (micro-testing showed the read/plan/report
  identity already binds).
- **No structural field for a distinction nothing consumes** (e.g. an object-vs-meta tier).
- **Not general ideation.** Skills stay grounded in a codebase, a conversation, governance, or the
  toolkit itself — not free-floating brainstorming.
