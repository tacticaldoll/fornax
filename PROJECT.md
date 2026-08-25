# Fornax — Project

What Fornax has **decided** and what it will **not** do, recorded so the calls are not re-litigated
by default (see the `audit-governance` skill). For what Fornax *is* — essence, naming, and voice — see
[docs/identity.md](docs/identity.md); for how to build and maintain skills, [AGENTS.md](AGENTS.md).

## Status

- Early stage. Every skill is `status: draft`; nothing claims 1.0 maturity.
- Skills span four families: implementation, knowledge, decisions, meta.
- Public repo, enforced by CI and a pre-commit hook running `scripts/check_workspace.py`.

## Standing decisions

Settled; reopen only with a reason, not by default.

- **Skills read / plan / report; they do not edit or execute.** Output is refined context; execution
  is handed off. Skills work only with context that actually exists — they mark inference apart from
  fact, name what they did not check, and never fabricate.
- **Self-contained skills; no coupling to a workflow or an installed tool.** A skill's instructions
  presuppose no development workflow, no change-tracking artifact, and no externally installed tool.
  An external source may be read when it happens to be there — a spec, a lint config, a host's
  sub-agents — but every such read names where to look and what the report says when it is absent;
  `static-review`'s Gate 6 is the reference shape, and `design-boundaries`, `plan-split`, and
  `audit-governance` fall back the same way when the host offers no separate passes or reviewers.
  Stated because its absence cost something: a review gate briefly carried a check needing a diff
  baseline — undefined for the inputs that carry none, a pasted snippet or a file path, and
  conditional for two more — and every workspace check passed it, because there was nothing to appeal
  to.
- **Judgments are language-neutral; a named language is example only.** A skill's criteria hold for
  any language the reviewed code is written in. A concrete language may appear as illustration
  (`unjustified unsafe code`, `cargo deny`) and that stays; what is excluded is a criterion that
  cannot be applied without one language's vocabulary. Feedback arriving in one language's terms is
  evidence about that codebase, not a statement about the criterion — the same separation the
  development knowns decision makes.
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
- **A record contract exists only where one skill's output is another skill's input.** Most skills
  define an output; exactly one of those outputs is read by another skill (`static-review` →
  `handle-feedback` and `static-review` → `triage-findings`, `docs/review-record-contract.md`). The
  rest have no contract because they have no consumer, not because one is missing — deliberate
  asymmetry, not a gap. "Exactly one" is derived from the `skill-interface.yaml` declarations and
  held true by `seam_contract.py --check`, rather than by the two counts this decision used to carry
  — those were kept by hand against a type distinction no field records, so nothing could say when
  they drifted. A real seam opts into matching `skill-interface.yaml` declarations, whose stable
  identity is publisher UUID, record type, major version, and media type. The sidecar
  supports local discovery and recommendation only; it carries no payload schema, eligibility rule,
  execution instruction, or authorization. The seam list is **derived from these declarations**
  rather than prose or a maintained list, so a second seam appears automatically and zero seams
  reports clean. Invocation always remains a separate, explicitly authorized host action. Do not add
  a repository-wide payload schema: the sidecar declares identity and the inventory extracts visible
  template headings, but two consumers of the same record identity are not evidence for a
  corpus-wide payload model. Reconsider a wider schema only when a second distinct record identity
  crosses a producer→consumer seam; that is the first evidence that can show which payload
  constraints actually generalize across records.
- **Skills carry no version of their own.** Release versioning is the collection's —
  `distribution.json` plus the host manifest projections — because a skill has no distribution path
  of its own: hosts read `SKILL.md`, whose frontmatter has no version field; the deployer only
  rewrites `name`; and the CLI pins one collection tag. The per-skill `skill.yaml` `version` was
  removed because nothing read it, every skill sat frozen at one value, and the patch/minor/major
  rules had accumulated on that inert field while the collection version — the one that actually
  gates whether installed users receive a change — had none.
- **Release bumps are separate.** Feature and fix commits keep the current collection version while
  they are implemented and reviewed. After the release contents are confirmed, one separate
  `build(deploy)` commit bumps `distribution.json` and every host projection together.
- **Development knowns are project state, not review authority.** Non-obvious defects, risks,
  constraints, and debt that affect future judgment live in `development-knowns.yaml`; reviews,
  tests, spikes, and experiments may supply evidence but do not dictate the statement or authorize
  work. Treatment and work authorization remain separate, while Git history records transitions.
  See `docs/development-knowns.md`.
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
  version resolves the matching canonical Git tag, requires that tag to be reachable from the remote
  default branch and the release manifest to declare that version, then **deploys that tag to every
  host** — native plugin, extension, and directory-copy alike — using a managed detached snapshot for
  validation and the directory channels. `main` may therefore move ahead of a release without putting
  two hosts on different revisions; the earlier requirement that the tag *equal* remote HEAD held
  only for the instant after tagging, and made the documented install command fail on the first
  commit after any release. Local sources and host-development installs are outside the `fornax` CLI.
- **Host deployment mechanics live independently.** `agent-skill-deployer` owns host discovery,
  inventory, provenance-aware mutation, reconciliation, and verification. Fornax retains only a
  thin `fornax` policy adapter and takes its CLI version from the workspace release; the engine has
  its own release cadence.
- **Distribution structure is vendor-neutral.** `distribution.json` is the canonical collection
  name, publisher UUID, and release version; host manifests are projections. New domain collections
  start from `agent-skills-distribution-template`, while the deployer keeps network-free neutral
  fixtures and no Fornax-specific test identity.

## Non-goals

- **Not an executor.** No editing code, running builds, or shipping — those are downstream of a
  skill's plan.
- **No blanket discipline machinery.** Hard-gates and rationalization tables are added per skill only
  on an observed failure, never corpus-wide by default (micro-testing showed the read/plan/report
  identity already binds).
- **No structural field for a distinction nothing consumes** (e.g. an object-vs-meta tier).
- **Not general ideation.** Skills stay grounded in a codebase, a conversation, governance, or the
  toolkit itself — not free-floating brainstorming.
