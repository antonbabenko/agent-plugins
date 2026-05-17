---
name: setup-code-intelligence
description: Check code-intelligence prerequisites (ripgrep + a language server) and print install hints
allowed-tools: Bash, AskUserQuestion
---

# code-intelligence: setup & readiness check

Run a one-shot readiness check for the `code-intelligence` skill, then offer an
optional star. The skill picks LSP vs exact-text vs fuzzy search by task; it
needs `rg` for the exact-text tier and a language server for the semantic tier.
Without them it runs degraded (text/fuzzy only).

Do the steps in order. Report results as a compact table. Do not install
anything. Do not write any state file. Keep output ASCII.

## 1. Detect OS

Run `uname -s`. Use it to pick the install hint column:

- `Darwin` -> Homebrew (`brew install ...`)
- `Linux` -> distro package manager (`apt`, `dnf`, `pacman`) or the
  language-native installer below

## 2. Check ripgrep

```bash
command -v rg >/dev/null 2>&1 && rg --version | head -1 || echo "rg MISSING"
```

If missing, print the matching install line and mark the exact-text tier
unavailable:

- macOS: `brew install ripgrep`
- Debian/Ubuntu: `sudo apt install ripgrep`
- Fedora: `sudo dnf install ripgrep`
- Arch: `sudo pacman -S ripgrep`
- Any (Rust): `cargo install ripgrep`

## 3. Probe language servers

For each server below, run `command -v <bin>` and report `present` or
`missing` on one line, with the install hint when missing. The user only needs
the server for the languages they work in - missing ones are not failures by
themselves.

| Language | Binary | Install hint |
|----------|--------|--------------|
| TypeScript/JS | `typescript-language-server` | `npm i -g typescript-language-server typescript` |
| Python | `pyright` or `pylsp` | `npm i -g pyright` or `pipx install python-lsp-server` |
| Go | `gopls` | `go install golang.org/x/tools/gopls@latest` |
| Rust | `rust-analyzer` | `rustup component add rust-analyzer` |
| C/C++ | `clangd` | `brew install llvm` or `apt install clangd` |
| Bash | `bash-language-server` | `npm i -g bash-language-server` |
| Terraform | `terraform-ls` | `brew install hashicorp/tap/terraform-ls` |
| Lua | `lua-language-server` | `brew install lua-language-server` |

**Claude Code users:** several language servers are also installable as LSP
plugins from the `claude-code-lsps` marketplace, no manual binary needed -
`/plugin marketplace add boostvolt/claude-code-lsps` then
`/plugin install <server>@claude-code-lsps` (e.g.
`terraform-ls@claude-code-lsps`). Prefer this on Claude Code; fall back to the
binary install hints above otherwise.

## 4. Verdict

- `rg` present AND at least one language server present -> print `READY`.
- Otherwise -> print `DEGRADED` and list, in priority order, what to install
  first: `rg` before any language server (text tier is the common fallback).

Tie the explanation to the skill: with no language server the agent cannot do
position-anchored semantic navigation and must disclose the text/fuzzy
fallback on the first line of its answer.

## 5. Optional star (after the checks, never before)

Use `AskUserQuestion`: "Star antonbabenko/agent-plugins on GitHub?" with
options `Yes` and `No thanks`.

- `Yes`: if `command -v gh` and `gh auth status` both succeed, run
  `gh api -X PUT /user/starred/antonbabenko/agent-plugins` and confirm.
  Otherwise print the link: `https://github.com/antonbabenko/agent-plugins`.
- `No thanks`: print one line - `Thanks for using code-intelligence:
  https://github.com/antonbabenko/agent-plugins` - and stop.

DON'T call `gh api` without an explicit `Yes`. DON'T write a marker or any
state file. DON'T ask more than once per invocation.
