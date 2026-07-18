# Host Packaging

Skills are host-neutral: a skill is `skill.yaml` (portable manifest) + `SKILL.md` (portable workflow)
plus optional `references/`. The `SKILL.md` format — YAML frontmatter with `name` and `description`,
then a Markdown body — is the open **[Agent Skills](https://agentskills.io) standard**, so the same
skill runs across Claude Code, GitHub Copilot, Cline, Cursor, Codex, OpenCode, and Antigravity. There
are **no per-skill, per-host adapter files**; host-specifics live once at the packaging layer.
The vendor-neutral `distribution.json` owns distribution identity and release version, while host
manifests are projections of that canonical metadata.

## Marketplace / plugin hosts

Each ships **one manifest for the whole collection**, pointing at `./skills/`:

| Host | File | Notes |
|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` | its `name` drives the `/fornax:<skill>` prefix |
| Codex | `.codex-plugin/plugin.json` | |
| Cursor | `.cursor-plugin/plugin.json` | |
| Gemini CLI / Antigravity | `gemini-extension.json` | install from the Git repository URL; `agy` layers on the same `~/.gemini/extensions/` store |
| agents marketplace | `.agents/plugins/marketplace.json` | marketplace descriptor also read by Codex |
| OpenCode | `.opencode/plugins/fornax.js` (+ `.opencode/INSTALL.md`) | registers the skills path; add to the `opencode.json` `plugin` array |

## Directory-discovery hosts

GitHub Copilot CLI and Cline read the open Agent Skills format **directly from standard skill
directories** — no bespoke manifest. Install by placing (copy or symlink) the `skills/<name>/`
folders where the host looks:

- **Copilot CLI**: `.github/skills`, `.claude/skills`, or `.agents/skills` (project); `~/.copilot/skills`
  or `~/.agents/skills` (personal).
- **Cline**: `.cline/skills` (recommended), `.clinerules/skills`, or `.agents/skills` (project);
  `~/.cline/skills` (personal).

Because every `SKILL.md` already conforms to the open standard, these hosts need only discovery, not a
Fornax-specific file.

## Declaration

Each `skill.yaml` `compatibility` list declares the hosts a skill supports (`claude`, `openai-codex`,
`cursor`, `antigravity`, `opencode`, `github-copilot`, `cline`, `generic-llm-agent`) — a portable
declaration, not a file requirement.
