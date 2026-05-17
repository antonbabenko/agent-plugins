# Changelog

All notable changes to the `code-intelligence` plugin are documented here. This file is managed by the per-plugin release pipeline; entries are prepended on release.

## code-intelligence-v0.4.1 (2026-05-17) ([compare](https://github.com/antonbabenko/agent-plugins/compare/code-intelligence-v0.3.1...code-intelligence-v0.4.1))

### Bug Fixes

* rename doctor command to setup-code-intelligence (#14) (cba265b)

## code-intelligence-v0.4.0 (2026-05-17)

### BREAKING CHANGES

* The `doctor` command is renamed to `setup-code-intelligence`. Its bare name
  shadowed Claude Code's built-in `/doctor`; invoke the readiness check as
  `/code-intelligence:setup-code-intelligence`.

## code-intelligence-v0.3.1 (2026-05-17) ([compare](https://github.com/antonbabenko/agent-plugins/compare/code-intelligence-v0.3.0...code-intelligence-v0.3.1))

### Bug Fixes

* doctor prints claude-code-lsps install path (ff8c05a)

## code-intelligence-v0.3.0 (2026-05-16) ([compare](https://github.com/antonbabenko/agent-plugins/compare/code-intelligence-v0.2.0...code-intelligence-v0.3.0))

### Features

* Codex marketplace support, README rebuild, code-intelligence doctor (#2) (fc383cc)

## code-intelligence-v0.2.0 (2026-05-16)

### Features

* add generic LSP and search code-intelligence skill (#1) (3d6f897)
