---
name: code-intelligence
description: Use when navigating or refactoring code with a language server - choosing between semantic (LSP), exact-text (rg), and fuzzy/semantic search; anchoring LSP calls by position; gating degraded results; and disclosing tool substitutions, in any language.
license: Apache-2.0
metadata:
  author: Anton Babenko
  version: 0.4.1
---

# Code Intelligence

Pick the search tool by task, not by habit. Generic and language-agnostic;
domain skills extend it with server capability matrices and ecosystem
prerequisites - for example the `terraform-skill` plugin (same marketplace)
owns the terraform-ls capability matrix and Terraform setup. It is
model-triggered guidance, not enforcement.

## Tool Precedence

| Goal | Use | Tradeoff |
|------|-----|----------|
| Symbol relationships: definition, references, call sites, rename safety | Language server (LSP) at a position | Needs a running server + indexed workspace |
| Exact text, known name, exhaustive enumeration, config/value files | `rg` then Read | No semantic scope; matches strings in comments too |
| Conceptual / fuzzy / "where might this live" / cross-repo discovery | A semantic/neural search tool, if the host provides one | Not exact; never use for counts or completeness claims |

Detail: [Precedence Table](references/tool-precedence.md#precedence-table),
[When LSP Is Wrong](references/tool-precedence.md#when-lsp-is-wrong).

## Calling the LSP

- DO call at a position (`file:line:character`). Anchor the position with a
  text search for a known occurrence first.
- DON'T pass a bare symbol name and expect resolution. A name-only call that
  returns empty is a usage defect, not server failure.
- DO Read the returned locations for source text; LSP returns locations and
  symbols, not the lines.
- DO retry once on a cold start: the first call after launch may return empty
  while the server indexes.
- DO prefer the server's own operation when it advertises it: use `rename` /
  `prepareRename` for renames and call hierarchy for callers - they carry
  language-specific semantics a manual pass misses.
- DON'T report an unsupported operation as a finding. When the server lacks
  one, redirect: `findReferences` (then filter to call sites) instead of call
  hierarchy; enumerate references then hand-edit instead of a rename provider.

Detail: [Position Anchoring](references/lsp-calls.md#position-anchoring),
[Unsupported Operations](references/lsp-calls.md#unsupported-operations).

## Degradation Gate

Two distinct cases:

- **No LSP at all** (host exposes no language-server tool, or the server fails
  to start): that IS unavailability. Disclose it on the first line (see below)
  and use text search. The gate does not apply - there is nothing to gate.
- **LSP callable but a position-anchored call returns empty:** do NOT conclude
  "unavailable" yet. Pass ALL three:
  1. `documentSymbol` on an in-scope file returns symbols -> server responsive
     (responsiveness only, NOT proof of complete reference coverage).
  2. The failing call was position-anchored (not symbol-name-only).
  3. That anchored call still returned empty after a cold-start retry.

Only after the three-part case passes is a disclosed text fallback warranted.

Detail: [Degradation Gate](references/degradation-and-disclosure.md#degradation-gate).

## Disclose Substitutions

State any tool substitution OR omission on the FIRST line of the response, not
in a later summary (post-hoc accounting is a rule violation):

`Intended: <tool>. Actual: <tool>. Reason: <why>. Impact: <completeness/confidence>.`

Detail: [Disclosure Format](references/degradation-and-disclosure.md#disclosure-format).

## Do Not Invent a Missing Tool

Before claiming a tool (e.g. `rg`) is shimmed, aliased, or absent, prove it:
`type -a <tool>`, `ls -l` the resolved path, `<tool> --version` shows the
expected banner. An unproven "tool is missing" claim followed by a fallback is
a verification failure, not a sanctioned substitution.

If genuinely absent or aliased: prefer the LSP for semantic tasks; for exact
text use the host-approved text search; `git grep` / `grep` only as an
explicitly disclosed last resort, never the default substitute.

Detail: [Anti-Phantom-Shim Proof](references/degradation-and-disclosure.md#anti-phantom-shim-proof).
