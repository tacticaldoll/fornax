# Working Brief Template

The compact, operational output of a warm-up. It is transient context for the current work, not a
repository summary and not durable knowledge (for durable capture, hand off to `save-knowledge`). Keep
it short; every field is either a declared fact with its source, or an explicit `not found`.

```markdown
## Working Brief — [project name]

**Sources read**: [AGENTS.md, CLAUDE.md, CONTRIBUTING, .github/workflows/, … | and: not found = …]

### Operational contract
- **Commit**: [message style / granularity / attribution policy | not found]
- **Branch / integration**: [branch model / default-branch protection / PR / merge (squash|merge) / subject rules | not found]
- **Review**: [required gates / approvals / review-before-merge | not found]
- **Style / language**: [formatter / linter / naming / doc rules / language policy | not found]

### Enforcement surface (what fails on violation)
| Check | Enforced by | Command | Enforced or documented-only |
|---|---|---|---|
| tests | [runner / CI job] | [invocation] | enforced |
| lint / format / type | … | … | … |
| git hooks | [pre-commit / husky] | … | … |
| build / self-check | … | … | … |

### Standing decisions and non-goals
- [Decision or "do not do X" + source] — so it is not re-litigated or violated.
- …

### Gaps and conflicts
- [Convention the project does not state → operating on assumption if needed.]
- [Two sources that disagree → the conflict, unresolved.]

### First-action guardrails
[The 2-4 rules that most shape the very next change: e.g. "branch before committing", "no AI
attribution in commits", "run <self-check> before reporting", "do not touch <owned path>".]
```

## Filling rules

- **Cite the source** for each declared fact (which file said it). A convention with no source is an
  assumption — put it under Gaps, not the contract.
- **Enforced vs documented** tells the agent what will catch a mistake automatically versus what it
  must self-police.
- **First-action guardrails** are the payoff — the few rules that would most embarrass the agent to
  violate on its first change. Keep them to the vital few.
- Prefer `not found` over silence, so the reader knows the difference between "the project forbids X"
  and "the project never addressed X".
