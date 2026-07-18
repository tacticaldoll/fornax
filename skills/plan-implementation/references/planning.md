# Planning Reference

Load this in Phases 1-2 to slice and sequence work. These are heuristics for cutting increments that
each produce a signal, and for ordering them — plus when to stop planning.

## Slice vertically, not horizontally

A **vertical slice** touches a little of each layer to deliver one observable behaviour end to end
(request → logic → store → response, thinnest possible). A **horizontal slice** builds one whole
layer first (all the models, then all the services). Prefer vertical:

- A vertical slice can be run and verified — it proves the whole path works.
- A horizontal layer proves nothing until the layers above and below exist; the signal comes late,
  and integration risk piles up at the end.
- The first vertical slice is a **walking skeleton**: the thinnest thing that runs end to end. Build
  it first; it retires the most architectural risk per unit of work.

## Make every increment produce a signal

The endpoint of each increment is an observable change, not "code written". Good acceptance checks:

- A test that fails now and passes after (name it).
- A behaviour you can trigger and see (an endpoint returns X, a command prints Y).
- A check that flips: type-checks, a lint rule, a metric.

If you cannot name the signal, the increment is too vague or too big — split it until you can.

## Sequence: dependency first, then risk and unblocking

1. **Dependency order is mandatory** — a task cannot precede what it needs.
2. Among what is free to reorder, pull earlier the work that is **riskiest / most uncertain**
   (a spike or a tracer bullet that proves the hard part is possible) and **most unblocking** (clears
   the widest set of downstream tasks). Finding out the risky approach fails on task 2 is cheap;
   finding out on task 9 is not.
3. Keep the system shippable between steps — never commit a sequence that leaves it half-broken.

A **tracer bullet** is a thin end-to-end path built early to validate the whole approach before
fleshing out any part; reach for one when the integration, not any single piece, is the real risk.

## Keep tasks independent where you can

Two tasks that must land together are one task split prematurely — either merge them or record the
**interlock** explicitly so the implementer does not ship one without the other. Genuinely
independent tasks can be reordered, parallelized, and verified alone; maximize that.

## When NOT to over-plan

Plan to the first fork where a result will reshape the rest — not past it.

- If the walking skeleton might invalidate the later tasks, plan the skeleton in detail and the rest
  as coarse placeholders; re-plan once it lands.
- Do not specify tasks whose shape depends on an unknown you will only resolve by doing an earlier
  task. Detailed planning past that point is speculation that will be rewritten.
- The plan is a tool for sequencing and verification, not a contract to predict every step; stop when
  it is detailed enough to start and to know when each step is done.
