# Tool Precedence

LSP for symbol meaning, text search for literals, semantic search for fuzzy
discovery. The three are not interchangeable.

### Precedence Table

| Task | Tool | Why |
|------|------|-----|
| Where is this symbol defined? | LSP `goToDefinition` at a use site | Resolves scope, imports, shadowing - text search cannot |
| Every reference / caller of a symbol | LSP `findReferences` at the symbol | Excludes same-named-but-unrelated tokens |
| Rename safety | LSP `findReferences` then per-file edits | Text replace hits comments, strings, unrelated scopes |
| Exact literal, error string, config key | `rg` then Read | Deterministic, fast, complete for text |
| Enumerate all matches / count occurrences | `rg` | Exact and exhaustive; semantic search drops matches |
| "Where is auth handled?", "which module owns X" | Semantic/neural search (if host provides) | Intent-level, no exact symbol to anchor on |

A directive that says one search tool replaces all search applies to broad
discovery only. It does not override LSP for symbol work or `rg` for exact
enumeration.

### When LSP Is Wrong

Skip the LSP and go straight to `rg` + Read for:

- Exact text or a known literal you can match directly.
- Known-name lookup where you already have the file and just need the line.
- Config / value files (data, not a symbol graph).
- Comments, generated docs, lockfiles, changelogs.
- Any file the language server does not index (non-source, vendored output).

LSP answers "what does this symbol mean and where is it used", not "where does
this string appear". Using it for the latter is slower and no more accurate.

### Semantic Search Scope

Semantic / neural search is for conceptual discovery when there is no exact
token to anchor on: "where is rate limiting", "which package handles billing".

- DO use it to locate a starting area, then switch to LSP or `rg` for precision.
- DON'T use it for exhaustive enumeration or any count - it drops exact
  matches and cannot prove completeness.
- DON'T cite its results as "all" of anything. Treat output as leads, not a
  closed set.

Example: "find everywhere we validate JWTs" - semantic search points at the
auth package; `rg 'jwt'` plus LSP `findReferences` on the verifier function
gives the complete set.
