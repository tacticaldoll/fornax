# Installing Fornax for OpenCode

Add Fornax to the `plugin` array in your `opencode.json` (global or project-level):

```json
{
  "plugin": ["fornax@git+https://github.com/tacticaldoll/fornax.git"]
}
```

Restart OpenCode. The plugin registers the Fornax skills directory; list and load
skills with OpenCode's native `skill` tool:

```
use skill tool to list skills
use skill tool to load map-codebase
```

Pin a version with a git ref:

```json
{
  "plugin": ["fornax@git+https://github.com/tacticaldoll/fornax.git#v0.1.0"]
}
```

Fornax skills read, plan, and report — they produce plans, maps, and reviews and hand off execution
rather than editing behind your back.
