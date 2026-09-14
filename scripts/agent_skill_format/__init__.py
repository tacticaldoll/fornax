"""The portable skill format's reading machinery, on its way out of this repository.

A package boundary inside the workspace, ahead of the repository boundary it is
meant to become. Everything here answers a question about a *published* artifact —
a manifest, a Markdown body, a declared path, a token read whole — and nothing here
knows what Fornax decides those answers should be. That split is the carve-out's
whole premise, and putting it behind an import is what makes a back-edge visible
before a repository boundary makes it expensive.

Nothing here reaches outside the standard library except where a grammar's owner is
declared: CommonMark is `markdown-it-py`'s and YAML is `PyYAML`'s, both pinned
alongside the workspace. The per-module claims are the ones a check holds.
"""
