---
name: code-intelligence
description: Use when navigating or refactoring code with a language server - choosing between semantic (LSP), exact-text (rg), and fuzzy/semantic search; anchoring LSP calls by position; gating degraded results; and disclosing tool substitutions, in any language.
license: Apache-2.0
metadata:
  author: Anton Babenko
  version: 0.1.0
---

# Code Intelligence

Pick the search tool by task, not by habit. Use the language server for symbol
meaning, exact-text search for literals, semantic search for fuzzy discovery.
Language-agnostic. Language-specific skills extend this with server capability
matrices and ecosystem prerequisites.

## Tool Precedence

| Goal | Use | Tradeoff |
|------|-----|----------|
| Symbol relationships: definition, references, call sites, rename safety | Language server (LSP) at a position | Needs a running server + indexed workspace |
| Exact text, known name, exhaustive enumeration, config/value files | `rg` then Read | No semantic scope; matches strings in comments too |
| Conceptual / fuzzy / "where might this live" / cross-repo discovery | A semantic/neural search tool, if the host provides one | Not exact; never use for counts or completeness claims |

Detail: [Tool Precedence](references/tool-precedence.md#precedence-table),
[When LSP Is Wrong](references/tool-precedence.md#when-lsp-is-wrong).

## Calling the LSP

- DO call at a position (`file:line:character`). Anchor the position with a
  text search for a known occurrence first.
- DON'T pass a bare symbol name and expect resolution. A name-only call that
  returns empty is a usage defect, not server failure.
- DO Read the returned locations to see source text; LSP returns locations and
  symbols, not the lines themselves.
- DO retry once on a cold start: the first call after launch may return empty
  while the server indexes.
- DON'T report an unsupported operation as a finding. Not every server
  implements implementation, call hierarchy, or rename. Redirect intent (use
  references instead of call hierarchy).

Detail: [LSP Calls](references/lsp-calls.md#position-anchoring),
[Unsupported Operations](references/lsp-calls.md#unsupported-operations).

## Degradation Gate

Pass ALL three before claiming "LSP unavailable, using text search instead":

1. `documentSymbol` on an in-scope file returns symbols -> server is
   responsive (responsiveness only, NOT proof of complete reference coverage).
2. The failing call was position-anchored (not symbol-name-only).
3. That anchored call still returned empty.

Only then is a disclosed text fallback warranted.

Detail: [Degradation Gate](references/degradation-and-disclosure.md#degradation-gate).

## Disclose Substitutions

Any tool substitution OR omission is stated on the FIRST line of the response,
not in a later summary:

`Intended: <tool>. Actual: <tool>. Reason: <why>. Impact: <completeness/confidence>.`

Post-hoc accounting in a closing summary is a rule violation.

Detail: [Disclosure Format](references/degradation-and-disclosure.md#disclosure-format).

## Do Not Invent a Missing Tool

Before claiming a tool (e.g. `rg`) is shimmed, aliased, or absent, prove it:
`type -a <tool>`, `ls -l` the resolved path, `<tool> --version` shows the
expected banner. An unproven "tool is missing" claim followed by a fallback is
a verification failure, not a sanctioned substitution.

If the tool is genuinely absent or aliased: prefer the LSP for semantic tasks;
for exact text use the host-approved text search; `git grep` / `grep` only as
an explicitly disclosed last resort - never as the default substitute.

Detail: [Anti-Phantom-Shim Proof](references/degradation-and-disclosure.md#anti-phantom-shim-proof).

## Scope

This is the generic discipline. Packaging it as a skill improves reuse and
discoverability; it does NOT enforce the behavior - skills are
model-triggered. A PreToolUse hook or a dedicated subagent gate is the
enforcement mechanism and is out of scope here.

## References

- [Tool Precedence](references/tool-precedence.md) - precedence table, when LSP is the wrong tool, semantic-search scope
- [LSP Calls](references/lsp-calls.md) - position anchoring, cold start, unsupported operations, reading results
- [Degradation and Disclosure](references/degradation-and-disclosure.md) - the gate, disclosure format, anti-phantom-shim proof
