# Tracing Reference

Load this when mapping an unfamiliar area (Phases 1-4). These are techniques for tracing flow and,
just as important, for knowing when to stop.

## Set the horizon from the purpose

Comprehension has no natural bottom — you can always trace one layer deeper. The change or decision
the map serves is the stopping rule:

- **A localized fix** → trace the one path that reaches the defect, plus its immediate callers and
  the state it touches. Ignore sibling features.
- **A refactor / split** → map the target unit's full surface and every inbound reference, but not
  the internals of unrelated modules it calls.
- **A design or adoption decision** → map boundaries, contracts, and external effects; skip
  line-level logic.

If you cannot say which of these the map is for, you cannot size it — ask before tracing.

## Find the entry points first

You understand a system faster from its edges inward than from a random file outward. Look for:

- Public API surface, route/request handlers, RPC/GraphQL resolvers.
- CLI commands, `main`/bootstrap/init, dependency-injection wiring.
- Event/message/queue handlers, scheduled jobs, lifecycle hooks.
- The **tests** that exercise the area — they name the real entry points and expected behaviour.

## Trace one path at a time

Follow a single realistic scenario end to end before branching out. For that path:

- **Control** — the call chain, the branches actually taken, where errors are caught or propagated,
  where it returns early.
- **Data** — what each step reads and writes, where that state lives (local, field, global, store),
  what transforms it, and which side effects fire (I/O, network, DB, mutation of shared state).

Resist breadth-first wandering; a fully understood single path beats five half-traced ones.

## Read for invariants, not just flow

Flow tells you what happens; invariants tell you what a change must not break. Watch for:

- Ordering and sequencing assumptions ("this runs before that").
- Nullability / presence assumptions, and what guarantees them upstream.
- Object lifecycle and ownership (who creates, mutates, disposes).
- Concurrency assumptions (single-threaded expectations, locks, reentrancy).
- Transactional or atomicity boundaries.

These are the landmines that make a "small" change break something far away.

## Mark inference vs fact

State what the code *shows* separately from what you *infer*. "The handler retries on 5xx
(`client.ts:88`)" is fact; "so duplicate requests are probably deduped upstream" is inference —
label it. Unmarked inference is how a confident-sounding map misleads the next change.

## When you have mapped enough

Stop when the map answers the purpose's question, not when the system is fully understood. Concrete
signals:

- You can name every path the intended change will touch and the state each moves.
- You can name the invariants the change must preserve.
- The remaining unknowns are outside the change's blast radius (record them under **Not traced**).

More tracing past that point is cost without return — hand off to the skill that acts on the map.
