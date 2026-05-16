# Contributing to agent-plugins

Thanks for helping improve these agent plugins. This repo is a multi-plugin
marketplace; read [CLAUDE.md](CLAUDE.md) for the architecture, content
standards, and the per-plugin release model before contributing.

## Quick Start

1. Fork the repository.
2. Create a feature branch.
3. Make changes following the guidelines below.
4. Test your changes (see Testing).
5. Open a pull request (the template is enforced).

## When to Contribute

**Good contributions:**

- ✅ New plugins that are useful, self-contained skills
- ✅ New best practices with community consensus
- ✅ Corrections to outdated or incorrect information
- ✅ Sharper organization, better examples, clearer structure
- ✅ Version-specific updates for tools a plugin targets

**Not suitable:**

- ❌ Personal preferences without community consensus
- ❌ Untested content changes (show baseline -> improved evidence)
- ❌ Content that merely duplicates existing agent knowledge
- ❌ Hand-edited version numbers (CI owns them)

## Adding a Plugin

**External** (content + releases in its own repo) — manifest entry only:

1. Add a `plugins[]` entry to `.claude-plugin/marketplace.json`: `name`,
   `source: { "source": "github", "repo": "owner/repo", "ref": "vX.Y.Z" }`,
   `description`, optional `category` / `keywords`, optional `version`
   (manual mirror of the ref).
2. No local content, CHANGELOG, tests, or scoped-commit release. Update by
   bumping `source.ref` (and the mirrored `version`).

**Inline** (content lives here):

1. `plugins/<plugin>/skills/<plugin>/SKILL.md` with valid frontmatter
   (`name`, `description`; optional `metadata.version`).
2. Add a `plugins[]` entry: `name`, `source: ./plugins/<plugin>`,
   `description`, `version` (`0.1.0`), optional `category` / `keywords`.
3. `plugins/<plugin>/CHANGELOG.md` (may be empty; CI prepends to it).
4. The manifest `version` must equal the SKILL.md `metadata.version`. CI
   enforces this.

See CLAUDE.md "SKILL.md Architecture" and the "LLM Consumption Rules" for
content shape and token discipline.

## Commits & Releases

Releases are automated and **per-plugin, for inline plugins only**, driven by
the commit scope on `master`. The scope must equal the plugin name. External
plugins release upstream; update them here by bumping `source.ref`.

| Commit subject | Result |
|----------------|--------|
| `feat(<plugin>): ...` | minor bump for `<plugin>` |
| `fix(<plugin>): ...` / `perf` / `refactor` | patch bump |
| `feat(<plugin>)!: ...` or `BREAKING CHANGE:` in body | major bump |
| no plugin scope | no release |

A commit scoped to one plugin never affects another. PRs are squash-merged, so
the squash commit subject is what drives the release; set it deliberately.

## Testing

This is documentation, not code. There is no build. Validate locally with the
commands in [CLAUDE.md](CLAUDE.md#validation), then verify behavior:

1. Reload the plugin in your agent host.
2. Run real queries the skill targets.
3. Confirm the agent applies the new patterns and introduces no new
   rationalizations.

Content PRs must include baseline (without change) and improved (with change)
agent transcripts in the PR template.

## CI

`validate.yml` runs on every PR touching `plugins/**` or `.claude-plugin/**`:
frontmatter, size, manifest validity, manifest <-> SKILL.md version sync,
broken links, and markdown lint. Fix failures before requesting review.

## Reporting Issues

Use [GitHub Issues](https://github.com/antonbabenko/agent-plugins/issues).
Include the plugin name, your agent host, and a reproducible prompt.
