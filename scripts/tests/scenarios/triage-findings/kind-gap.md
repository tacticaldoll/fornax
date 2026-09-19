# Kind-gap fixture

Triage this single finding against the included code excerpt. The premise is established by the
excerpt; do not decline it for missing evidence.

## Finding F-repeat-query

`Catalog::label` repeats an expensive, deterministic registry query for the same key on every call.
The accepted repair is to memoize labels by key after the first query. The cache is local process
state; no persistence, invalidation, concurrency, or API change is involved.

```text
class Catalog:
    def label(self, key):
        return expensive_registry_query(key).label
```

Produce one Causes and candidate repairs row for this finding.
