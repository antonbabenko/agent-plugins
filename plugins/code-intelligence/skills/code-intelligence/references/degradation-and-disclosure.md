# Degradation and Disclosure

What to prove before falling back, how to announce a fallback, and how to
prove a tool is really missing.

## Degradation Gate

First separate two cases:

- **No LSP at all**: the host exposes no language-server tool, or the server
  will not start. This is genuine unavailability - the gate does not apply.
  Disclose on the first line (see Disclosure Format) and use text search.
- **LSP callable, position-anchored call returns empty**: a degraded or
  unindexed workspace can legitimately do this. Do not conclude "unavailable" -
  run the gate.

Gate (second case only). Pass ALL three before claiming "LSP degraded, using
text search":

1. `documentSymbol` on an in-scope file returns symbols. The server is
   responsive. This proves responsiveness ONLY, not complete reference
   coverage.
2. The failing call was position-anchored, not symbol-name-only.
3. That anchored call still returned empty after a cold-start retry.

All three pass -> a disclosed text fallback is warranted. Any fails -> fix the
call or the setup; do not fall back yet.

Distinguish: a name-only call returning empty is a usage defect (gate fails at
2). A position-anchored call on a responsive server returning empty is genuine
degradation (gate passes).

## Disclosure Format

State any tool substitution OR omission on the FIRST line of the response:

`Intended: <tool>. Actual: <tool>. Reason: <why>. Impact: <completeness/confidence>.`

- Covers substitution (used a different tool) AND omission (skipped a step or
  scope).
- First line, same response. A later closing summary is a rule violation - the
  reader must see the caveat before the conclusion.
- One line, factual, no hedging. The impact clause states what confidence is
  lost (e.g. "text matches only, may include comments/strings").

## Anti-Phantom-Shim Proof

Do not claim a tool is shimmed, aliased, replaced, or missing without proof.
Verify before asserting:

1. `type -a <tool>` - resolve what actually runs.
2. `ls -l <resolved-path>` - confirm the binary exists and is executable.
3. `<tool> --version` - confirm it prints the expected banner.

If it prints the expected version, the tool is real - investigate the
execution context (sandbox, PATH, shell) before any fallback. An unproven
"tool is missing" claim followed by a fallback is a verification failure, not
a sanctioned substitution.

If genuinely absent or aliased: prefer the LSP for semantic tasks; for exact
text use the host-approved text search; `git grep` / `grep` only as an
explicitly disclosed last resort, never the default substitute.
