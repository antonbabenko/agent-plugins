# LSP Calls

Generic mechanics for driving a language server. Operation names follow LSP:
`goToDefinition`, `findReferences`, `hover`, `documentSymbol`,
`workspaceSymbol`, `goToImplementation`, call hierarchy. Availability is
host-gated - the host decides whether an LSP tool is exposed at all.

## Position Anchoring

The server resolves by source position, not by symbol name.

- Call with `file:line:character` pointing at an occurrence of the symbol.
- Find that occurrence first with a text search (a known use or the
  declaration), then issue the LSP call at that location.
- A bare-name call is unsupported; an empty result from one is a usage defect,
  not degradation.

Example: to find callers of `parseConfig`, `rg -n 'parseConfig'` to get a
line, then `findReferences` at that line/column. Works the same whether the
language is Go, Python, or TypeScript.

## Cold Start And Retry

The first call after the server launches may return empty or partial while it
indexes the workspace.

- Retry the same call once after a short pause before drawing any conclusion.
- A still-empty result after retry feeds the degradation gate; it is not
  immediate proof the server is broken.

## Unsupported Operations

Not every server implements every operation. `goToImplementation`, call
hierarchy (`prepareCallHierarchy` / `incomingCalls` / `outgoingCalls`), and
rename are commonly absent.

- DO check advertised capabilities first. When the server supports `rename` /
  `prepareRename` or call hierarchy, use it - it carries language semantics a
  manual pass misses.
- DON'T call an unsupported operation and report its absence as a finding.
- DO redirect only when the operation is genuinely unsupported: `findReferences`
  (filtered to call sites) instead of call hierarchy; enumerate references then
  edit by hand instead of a rename provider.
- DON'T guess support - confirm via advertised capabilities or a language skill
  that documents them.

## Reading Results

LSP returns locations and symbols, not source lines.

- After `goToDefinition` / `findReferences`, Read each returned location to see
  and act on the actual code.
- For multi-edit changes in one file, Read that file again immediately before
  each edit - earlier edits shift line/character offsets and a stale view
  produces corrupted edits.
- `documentSymbol` returns a structural outline; use it as a liveness probe
  and to navigate, not as a reference set.
