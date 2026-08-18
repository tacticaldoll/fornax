# Development knowns

`development-knowns.yaml` records non-obvious current conditions that affect future development
judgment. Entries are project knowledge, not a transcript of review feedback: a review, test, spike,
or experiment may supply evidence, but does not own the statement or authorize its treatment.

Git history records changes in understanding. Update the current entry instead of appending an event
log, and remove routine facts already stated clearly in `PROJECT.md` or `AGENTS.md`.

## Entry model

Every entry has a stable lowercase hyphen-case `id`, a project-centered `statement`, a `kind`
(`defect`, `risk`, `constraint`, or `debt`), a `treatment` (`remediate`, `monitor`, `accept`, or
`resolved`), a `rationale`, at least one `evidence` item, and an `updated` date. Optional
`declined-changes` preserve considered repairs that should not be proposed again without new
evidence.

Treatment-specific fields make the state meaningful:

- `remediate` requires `repair`.
- `monitor` requires `reconsider-when`.
- `accept` records why the current condition is intentional; `reconsider-when` is recommended.
- `resolved` requires `verification`.

Treatment is not work authorization. Only an explicit `work: backlog` or `work: in-progress` on a
`remediate` entry authorizes implementation; `work: done` may accompany a `resolved` entry. Review
and triage workflows may propose a registry update, but must not write one or start its repair until
the user authorizes that repository change.

## Constrained YAML and views

The registry uses a deliberately small YAML subset: top-level `schema` and `knowns`, flat known
mappings, single-line raw scalars, and block lists of single-line raw scalars. Quoted or multiline
scalars, flow collections, arbitrary nesting, anchors, aliases, and tags are rejected. This keeps
the local hook and CI standard-library-only; adopt a full YAML dependency only if the data model
genuinely needs richer structure or another full YAML consumer appears.

Validate the registry with:

```sh
python3 scripts/development_knowns.py --check
```

Read-only views are derived on demand and never committed:

```sh
python3 scripts/development_knowns.py --list backlog
python3 scripts/development_knowns.py --list watchlist
python3 scripts/development_knowns.py --list accepted
python3 scripts/development_knowns.py --list resolved
```

The backlog view contains only explicitly authorized `backlog` or `in-progress` work. The other
views project `monitor`, `accept`, and `resolved` treatments respectively.
