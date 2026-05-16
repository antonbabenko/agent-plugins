# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **For End Users:** See [README.md](README.md) for installation and usage.
>
> **This file** is for contributors, maintainers, and skill developers.

## What This Is

A **hybrid multi-plugin marketplace** for AI coding agents. Each plugin is
executable documentation (a Claude Code / Agent Skills compatible skill) loaded
on demand. Plugins are unrelated and versioned independently.

The manifest at `.claude-plugin/marketplace.json` lists every plugin. A plugin
is either:

- **External** — referenced via a GitHub `source` object. Content, tests, and
  releases live in that plugin's own repo. This repo only pins a ref.
- **Inline** — content lives here under `plugins/<name>/` and uses this repo's
  per-plugin release pipeline.

## Repository Structure

```
agent-plugins/
├── .claude-plugin/marketplace.json   # Marketplace + plugin entries
├── plugins/                          # Inline plugins only (empty until added)
│   └── .gitkeep
│   └── <inline-plugin>/              # (when added) source dir for the manifest
│       ├── skills/<plugin>/          # Autodiscovered: skills/<name>/SKILL.md
│       │   ├── SKILL.md              # Core skill file
│       │   └── references/           # Reference files loaded on demand
│       ├── tests/                    # Baseline scenarios, rationalization table
│       └── CHANGELOG.md              # Per-plugin changelog (CI-managed)
└── .github/workflows/
    ├── validate.yml                  # PR validation (hybrid source-aware)
    └── automated-release.yml         # Per-plugin release (inline plugins only)
```

Claude Code autodiscovers `<source>/skills/<name>/SKILL.md` and, for external
sources, auto-clones + caches the referenced repo (see
[plugins reference](https://code.claude.com/docs/en/plugins-reference)).

## Plugin Source Types

| | External | Inline |
|--|----------|--------|
| `source` | `{ "source": "github", "repo": "owner/repo", "ref": "vX.Y.Z" }` | `"./plugins/<plugin>"` |
| Content | Upstream repo | `plugins/<plugin>/` here |
| Releases | Upstream repo's own pipeline | This repo's per-plugin pipeline |
| Update here | Bump `source.ref` + mirrored `version` | Push a scoped conventional commit |
| `version` field | Optional, manual mirror of `source.ref` (NOT CI-managed) | Required, CI-managed, must equal SKILL.md `metadata.version` |

`terraform-skill` is external: `antonbabenko/terraform-skill`, pinned by
`source.ref`. Its content and tags (`vX.Y.Z`) live in that repo; to ship a
newer version, bump `source.ref` and the mirrored `version` in the manifest.

## Adding a Plugin

**External plugin** — manifest entry only:

1. Add to `.claude-plugin/marketplace.json` `plugins[]`: `name`,
   `source: { "source": "github", "repo": "owner/repo", "ref": "vX.Y.Z" }`,
   `description`, optional `category` / `keywords`, optional `version`
   (mirror of the ref, manual).
2. No local content, CHANGELOG, or tests here. No scoped-commit release.

**Inline plugin** — content lives here:

1. Create `plugins/<plugin>/skills/<plugin>/SKILL.md` with valid frontmatter
   (`name`, `description`; optional `metadata.version`).
2. Add a `plugins[]` entry: `name`, `source: ./plugins/<plugin>`,
   `description`, `version` (start at `0.1.0`), optional `category` /
   `keywords`.
3. Add `plugins/<plugin>/CHANGELOG.md` (can be empty; CI prepends to it).
4. The manifest `version` must equal the SKILL.md `metadata.version`. CI
   enforces this.
5. Add `plugins/<plugin>/tests/baseline-scenarios.md` - **required**, CI
   enforces it: at least one `## Scenario`, a `## Running These Tests`
   protocol, and a `### Success Criteria` list. Copy the shape of
   `plugins/code-intelligence/tests/baseline-scenarios.md`.

## Development Workflow

**This is documentation, not code.** No build, no compiled tests.

### Validation

CI runs on PRs touching `plugins/**` or `.claude-plugin/**`. It validates every
`plugins/*/skills/*/SKILL.md`. To check locally:

```bash
# Frontmatter + size, all skills
for f in plugins/*/skills/*/SKILL.md; do
  echo "$f: $(wc -l < "$f") lines"
done

# Manifest <-> SKILL.md version sync
python3 -c "
import json, yaml, os
m = json.load(open('.claude-plugin/marketplace.json'))
for p in m['plugins']:
    src = p['source'].lstrip('./')
    sp = os.path.join(src, 'skills', p['name'], 'SKILL.md')
    fm = yaml.safe_load(open(sp).read().split('---', 2)[1])
    sv = (fm.get('metadata') or {}).get('version')
    print(p['name'], p['version'], '==', sv, 'OK' if sv == p['version'] else 'MISMATCH')
"

# Broken internal links for a skill
cd plugins/<plugin>/skills/<plugin>
grep -oP '\[.*?\]\(references/.*?\.md.*?\)' SKILL.md references/*.md | \
  sed 's/.*(//' | sed 's/).*//' | sed 's/#.*//' | \
  while read -r link; do [ ! -f "$link" ] && echo "Broken: $link"; done
```

### Testing Changes

No automated suite. Manual flow:

1. Edit a `SKILL.md` or `references/*.md` file.
2. Run that plugin's `tests/baseline-scenarios.md` per its
   `## Running These Tests`: each prompt with the plugin OFF (baseline) then
   ON (target).
3. Every scenario must meet its `### Success Criteria` with no new
   rationalizations; one failure blocks the change.
4. Add or update a scenario whenever a PR adds or changes a behavior.
5. Attach baseline + target transcripts to the PR (or `/tmp`), never under
   `plugins/`. Tests are required, not optional - CI fails an inline plugin
   with no scenario file.

## Commit Conventions & Releases

Releases are **fully automated and per-plugin, for inline plugins only**.
External plugins release in their own repos; you ship a newer one here by
bumping its `source.ref`. The release pipeline analyzes each push to `master`
and bumps each inline plugin independently from **plugin-scoped** conventional
commits.

| Commit | Effect |
|--------|--------|
| `feat(<plugin>)!:` or body `BREAKING CHANGE:` | Major bump for `<plugin>` |
| `feat(<plugin>): ...` | Minor bump for `<plugin>` |
| `fix(<plugin>): ...`, `perf(<plugin>):`, `refactor(<plugin>):` | Patch bump |
| Commit with no plugin scope (or unknown scope) | No release |

**The commit scope must equal the plugin name.** A commit scoped to
`terraform-skill` never moves any other plugin. Per release the workflow:

- bumps `plugins[].version` in `marketplace.json`,
- syncs that plugin's `SKILL.md` `metadata.version`,
- prepends an entry to `plugins/<plugin>/CHANGELOG.md`,
- tags `<plugin>-vX.Y.Z` and creates a GitHub Release.

The marketplace root `version` is the manifest schema version and is bumped
manually, not by CI.

**Never manually edit plugin version numbers** in the manifest or SKILL.md. CI
owns them. To force a release without a code change, push a scoped commit or run
the workflow via `workflow_dispatch`.

> Note: inline-plugin tags are `<plugin>-vX.Y.Z` (scoped to this repo).
> External plugins like `terraform-skill` keep their own `vX.Y.Z` tags in
> their upstream repo; this repo never tags or changelogs them.

## SKILL.md Architecture

### YAML Frontmatter

```yaml
---
name: <plugin>                 # letters, numbers, hyphens only
description: Use when...        # < 1024 chars, starts with "Use when"
license: Apache-2.0             # optional
metadata:
  author: Anton Babenko         # optional
  version: X.Y.Z                # optional; auto-synced by CI if present
---
```

### Progressive Disclosure Pattern

`SKILL.md` is the entry point. Reference files load on demand. Cross-links use
relative paths: `[Guide](references/some-guide.md)`. When adding content, ask:
**decision framework or key pattern -> SKILL.md; detailed example or template
-> reference file.**

### Content Standards

- **Imperative voice:** "Use X" not "You should consider X"
- **Scannable format:** tables > bullets > prose
- **DO / DON'T** side-by-side for non-obvious patterns
- **Version-specific features** clearly marked
- **Token budget:** keep `SKILL.md` lean (target <500 lines; <300 ideal)

### LLM Consumption Rules (enforce in every PR review)

These tune content for the **primary reader: an LLM retrieving facts to answer
a query**, not a human reading end to end. Mandatory for every addition to
`SKILL.md` and `references/*.md`. Reject PRs that violate them.

1. **Shape: decision table before playbook.** When a topic has multiple viable
   approaches, open with a decision table (`Goal | Use | Tradeoff`) before any
   phase steps. Never bury branching in prose.
2. **Cut human scaffolding.** Before/after diffs and "Why this matters"
   paragraphs are human-only signal. If the steps already name the action, a
   diff is redundant; drop it.
3. **Compress prose to DON'T/DO rules.** Any "You should...", "Note that...",
   "Keep in mind..." sentence becomes a terse imperative bullet. One fact per
   bullet.
4. **Every artifact earns its tokens.** Each code block, table, or example must
   add a fact not in the prose. If it only restates, cut it.
5. **Anchor stability.** SKILL.md routes to specific `#anchor` headings in
   reference files. Rewrites may restructure subsections but must preserve the
   top-level `### Heading` the SKILL.md table points to.
6. **Retrieval-first ordering.** Within a section: (a) decision table,
   (b) default procedure, (c) alternatives, (d) rules as DON'T/DO. Rationale is
   one opening sentence, never a closing "Why this matters" block.

**Token target per reference subsection:** under 400 tokens (~1,600 chars).

## What Belongs Where

| Content type | Location |
|--------------|----------|
| Decision frameworks, core patterns | `plugins/<plugin>/skills/<plugin>/SKILL.md` |
| Detailed guides, templates, examples | `.../references/*.md` |
| Baseline test scenarios | `plugins/<plugin>/tests/*.md` |
| Per-plugin changelog | `plugins/<plugin>/CHANGELOG.md` (CI-managed) |
| Installation/usage docs | `README.md` |
| Contributor process | `CONTRIBUTING.md` |
| Marketplace + versions | `.claude-plugin/marketplace.json` (CI-managed versions) |
