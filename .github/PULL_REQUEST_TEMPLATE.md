# Pull Request

## Description

**Plugin(s) affected:** <!-- e.g. terraform-skill, or "new plugin: foo" -->

**Type of change:**
- [ ] New plugin
- [ ] New content (best practices, patterns, guidance)
- [ ] Fix (correcting outdated or incorrect information)
- [ ] Refactor (reorganizing or improving clarity)
- [ ] Documentation (README, CONTRIBUTING, CLAUDE.md)
- [ ] CI / tooling

**Summary:**
<!-- What does this change do and why? -->

## Conventional Commit

Releases are per-plugin. A typed squash/merge commit qualifies for an inline
plugin when it changes release-worthy content under `plugins/<plugin>/`, or
when its subject is explicitly scoped to that plugin. Scope is useful for
clarity but is not required when the changed paths identify the plugin.

- `feat: ...` (or `feat(<plugin>): ...`) -> minor bump for affected plugin(s)
- `fix: ...`, `perf: ...`, or `refactor: ...` (scoped or unscoped) -> patch bump
- `feat!:` / `feat(<plugin>)!:` or a valid `BREAKING CHANGE:` footer -> major bump
- `chore` / `docs` / `ci` / `test`, or changes limited to tests/CHANGELOG -> no release

**Planned commit subject:** `type(scope): description`

## Testing Evidence (REQUIRED for content changes)

### Baseline Behavior (WITHOUT changes)

```
Prompt: [test prompt]
Agent response: [verbatim or screenshot]
Issues: [what was missing or incorrect]
```

### Behavior (WITH changes)

```
Prompt: [same test prompt]
Agent response: [verbatim or screenshot]
Improvements: [what improved / patterns now followed]
```

- [ ] Ran the plugin's `tests/baseline-scenarios.md` per its
      `## Running These Tests` (plugin OFF then ON)
- [ ] Every scenario meets its `### Success Criteria`; no scenario fails
- [ ] Added/updated a scenario for any new or changed behavior
- [ ] Agent references new content
- [ ] Agent applies new patterns proactively
- [ ] No new rationalizations introduced

## Standards Compliance Checklist

### Frontmatter (if SKILL.md changed)

- [ ] `name` and `description` present; `name` is letters/numbers/hyphens only
- [ ] Description starts with "Use when..." and is < 1024 chars
- [ ] `metadata.version` (if present) matches the manifest plugin version
      (or left for CI; do not hand-bump)

### Token Efficiency & Content Quality

- [ ] SKILL.md remains lean (target <500 lines)
- [ ] Detailed content lives in `references/*.md`
- [ ] Tables over prose; imperative voice; DO vs DON'T where useful
- [ ] Code examples complete and runnable
- [ ] LLM Consumption Rules in CLAUDE.md followed

### Marketplace / Structure

External plugin (referenced repo):
- [ ] `plugins[]` entry with `source: { source: github, repo: owner/repo, ref: vX.Y.Z }`
- [ ] No local content / CHANGELOG / scoped-commit release
- [ ] `version` (if set) mirrors `source.ref`; the external updater keeps it in sync

Inline plugin (content here):
- [ ] `plugins[]` entry with `source: ./plugins/<plugin>`
- [ ] `plugins/<plugin>/skills/<plugin>/SKILL.md` exists
- [ ] `plugins/<plugin>/CHANGELOG.md` exists
- [ ] No version numbers hand-edited (CI owns them)

## Validation

<!-- Runs in CI; check locally too (see CLAUDE.md) -->

- [ ] Tooling unit tests pass (when `.github/scripts/**` changes)
- [ ] Frontmatter validation passes
- [ ] Manifest <-> SKILL.md version sync passes
- [ ] No broken internal links
- [ ] Markdown lint clean

## Related Issues

Closes #
Relates to #

---

## For Maintainers

- [ ] Testing evidence convincing (baseline -> improved)
- [ ] Standards compliance verified
- [ ] Squash with a correctly typed conventional commit subject
- [ ] Confirm the resulting per-plugin version bump is intended
