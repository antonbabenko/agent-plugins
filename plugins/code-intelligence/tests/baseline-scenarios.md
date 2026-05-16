# Baseline Scenarios

Compare agent behavior WITHOUT vs WITH the code-intelligence skill. Run each
prompt without the skill (baseline), then with it (target). Capture transcripts
in the PR body or /tmp - never inside the plugin.

> markdownlint note: repeated `Test Prompt` / `Pressure Variations` /
> `Success Criteria` sub-headings are inherent to the multi-scenario format;
> `.markdownlint.jsonc` sets `MD024: siblings_only` and disables `MD013`, so
> this format lints clean.

## Running These Tests

Required for every content PR that touches this plugin. No build; this is a
behavioral A/B against a real agent host.

1. **Baseline (WITHOUT the change).** Use an agent host where this plugin is
   NOT loaded - uninstall it, disable it, or use a separate profile. For each
   scenario below, paste the **Test Prompt** verbatim and save the agent's full
   response.
2. **Target (WITH the change).** Load the plugin (your branch). Re-run the
   exact same prompts.
3. **Compare.** For each scenario, the WITH run must satisfy every box under
   **Success Criteria** and introduce no new rationalizations. Also run the
   listed **Pressure Variations** - the behavior must hold under pressure.
4. **Gate.** ALL scenarios must pass. A single failing scenario blocks the PR.
5. **Evidence.** Put the baseline and target transcripts in the PR body (or
   `/tmp`) - never inside `plugins/`. Fill the PR template's testing section.

New scenarios: when a PR adds or changes a behavior, add or update a scenario
here so the behavior stays covered. CI fails an inline plugin that has no
`tests/baseline-scenarios.md` with scenarios, this run protocol, and success
criteria.

## Scenario 1: Find Callers and Rename Safely

**Objective:** Verify the agent uses semantic navigation and a safe rename pass
instead of blind text replacement.

### Test Prompt

```text
Rename the function `parseConfig` to `loadConfig` everywhere it is used in this project.
```

### Expected Baseline Behavior (WITHOUT skill)

- Single `grep`/`rg` for `parseConfig`, then in-place replace across matches
- Replaces occurrences in comments/strings/unrelated same-named symbols
- Rationalization: "search found all of them"

### Target Behavior (WITH skill)

- Anchors a position via text search, then LSP `findReferences`
- Reads each file immediately before editing it (offsets shift)
- Distinguishes the target symbol from unrelated same-named tokens
- Discloses on line 1 if it falls back to text search after the gate

### Pressure Variations

- Time: "just do a find-and-replace, it's quick"
- Authority: "I already know every call site, just rename"
- Sunk cost: after a blind replace, "did that catch all of them?"

### Success Criteria

- [ ] Uses LSP `findReferences` at a position (or discloses fallback on line 1 after passing the degradation gate)
- [ ] Fresh-reads each file before editing
- [ ] Does not claim an unsupported operation as a finding
- [ ] No edits to comments/strings/unrelated symbols

---

## Scenario 2: Tool Claimed Missing

**Objective:** Verify the agent proves a tool is absent before substituting and
discloses any substitution.

### Test Prompt

```text
rg seems broken in this environment, just use the other search tool to find every call to `chargeCard`.
```

### Expected Baseline Behavior (WITHOUT skill)

- Accepts the claim, silently switches to another tool
- No verification that rg is actually unavailable
- No first-line disclosure of the substitution

### Target Behavior (WITH skill)

- Runs the anti-phantom-shim proof (`type -a rg`, `ls -l` resolved path, `rg --version`)
- If rg is real: uses it and says so; if genuinely absent: prefers LSP for the semantic part
- Discloses any substitution on the first line in the standard format

### Pressure Variations

- Authority: "trust me, rg is broken, don't waste time checking"
- Time: "we don't have time to verify, just switch"

### Success Criteria

- [ ] Verifies tool reality before substituting
- [ ] First-line disclosure when substituting or omitting
- [ ] Does not present `grep` as the default substitute

---

## Scenario 3: Fuzzy Discovery

**Objective:** Verify the agent uses the semantic tier for conceptual questions
and does not over-claim completeness.

### Test Prompt

```text
Where in this codebase is user authentication handled?
```

### Expected Baseline Behavior (WITHOUT skill)

- Single grep for "auth", presents partial hits as the full answer
- Or claims an exact count of "all" auth code from a fuzzy search

### Target Behavior (WITH skill)

- Uses semantic/neural search (if host provides) to locate the area
- Switches to LSP/`rg` to confirm specifics
- Frames semantic results as leads, makes no exact-count or completeness claim from them

### Pressure Variations

- "just give me the one file that does auth"
- "how many places exactly - give me the number"

### Success Criteria

- [ ] Uses the semantic tier if the host provides one; otherwise discloses the fallback to text search on the first line - does not default to LSP for this conceptual question
- [ ] No exact-count or "this is all of it" claim from semantic search
- [ ] Narrows with LSP/`rg` before asserting specifics

---

## Scenario 4: Doctor Command Readiness Check

**Objective:** Verify the `/code-intelligence:doctor` command reports
prerequisites accurately and the optional star step is consent-gated and
stateless.

### Test Prompt

```text
/code-intelligence:doctor
```

### Expected Baseline Behavior (WITHOUT skill)

- Command does not exist; the host reports an unknown command

### Target Behavior (WITH skill)

- Checks `rg` and probes language servers, one status line each with an
  install hint for missing ones
- Prints `READY` or `DEGRADED` with what to install first (`rg` before any
  language server)
- Asks the star question once, only after the checks
- Calls `gh api` only on an explicit Yes; otherwise prints the manual link
- Writes no state or marker file

### Pressure Variations

- "skip the checks and just star it" - must still run checks first and not
  star without an explicit Yes
- Run the command twice - second run behaves identically (no memory, no marker)

### Success Criteria

- [ ] Reports `rg` status and per-language-server status with install hints
- [ ] Prints a `READY`/`DEGRADED` verdict with install priority
- [ ] Star step runs after checks and only on explicit consent
- [ ] No `gh api` call without an explicit Yes
- [ ] No state or marker file is created
