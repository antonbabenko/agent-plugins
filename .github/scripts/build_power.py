#!/usr/bin/env python3
"""POWER.md generator for inline plugins (Kiro Power).

Single source of truth is the plugin's skills/<name>/SKILL.md. This emits
<plugin_dir>/POWER.md so the inline skill installs as a Kiro Power. Pure,
deterministic, idempotent. POWER.md is a GENERATED, CI-owned artifact - same
contract as .codex-plugin/plugin.json: never hand-edit. The release pipeline
regenerates it; validate.yml runs --check to block drift.

displayName + keywords are reused from the plugin's .codex-plugin/plugin.json
(one curated source). references/ files are NOT moved; only relative links are
rewritten so they resolve from the plugin (power) root. If <plugin_dir>/mcp.json
exists, an "## MCP Tools (Kiro)" trailer naming its servers is appended.

Stdlib only (no PyYAML): the SKILL.md frontmatter is a fixed, simple shape
parsed line by line - same approach as .github/scripts/update_external_plugins.py.

Usage:
  python3 .github/scripts/build_power.py plugins/<plugin>            # write
  python3 .github/scripts/build_power.py plugins/<plugin> --check     # verify
"""

import json
import os
import re
import sys


def parse_frontmatter(skill_path):
    src = open(skill_path, encoding="utf-8").read()
    if not src.startswith("---"):
        raise SystemExit(f"build_power: {skill_path} has no leading --- "
                         f"frontmatter")
    parts = src.split("---")
    fm, body = parts[1], "---".join(parts[2:])
    out = {}
    for raw in fm.splitlines():
        line = raw.rstrip("\r")
        m = re.match(r"^name:\s*(.+?)\s*$", line)
        if m:
            out["name"] = m.group(1)
            continue
        m = re.match(r"^description:\s*(.+?)\s*$", line)
        if m:
            out["description"] = m.group(1)
            continue
        m = re.match(r"^\s+author:\s*(.+?)\s*$", line)
        if m:
            out["author"] = m.group(1)
            continue
        m = re.match(r"^\s+version:\s*(.+?)\s*$", line)
        if m:
            out["version"] = m.group(1)
            continue
    for k in ("name", "description", "author", "version"):
        if not out.get(k):
            raise SystemExit(f"build_power: {skill_path} frontmatter "
                             f"missing {k}")
    return out, body


def yaml_dq(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_power(plugin_dir):
    plugin_dir = plugin_dir.rstrip("/")
    name = os.path.basename(plugin_dir)
    skill_path = os.path.join(plugin_dir, "skills", name, "SKILL.md")
    codex_path = os.path.join(plugin_dir, ".codex-plugin", "plugin.json")
    mcp_path = os.path.join(plugin_dir, "mcp.json")

    meta, body = parse_frontmatter(skill_path)

    if not os.path.isfile(codex_path):
        raise SystemExit(f"build_power: {codex_path} not found (needed for "
                         f"displayName/keywords)")
    codex = json.load(open(codex_path, encoding="utf-8"))
    display_name = (codex.get("interface") or {}).get("displayName") \
        or meta["name"]
    keywords = codex.get("keywords") or []
    if not keywords:
        raise SystemExit(f"build_power: {codex_path} has no keywords")

    rewritten = re.sub(r"\]\(references/",
                       f"](skills/{name}/references/", body)
    rewritten = re.sub(r"^\n+", "", rewritten)
    rewritten = re.sub(r"\s*$", "", rewritten)

    # Quote free-text scalars + every keyword so a future value containing a
    # YAML-sensitive char (:, #, [, etc.) cannot break frontmatter parsing.
    # version stays unquoted: a CI-controlled multi-dot semver is always a
    # YAML string and validate.yml reads it directly.
    front = "\n".join([
        "---",
        f"name: {yaml_dq(meta['name'])}",
        f"displayName: {yaml_dq(display_name)}",
        f"description: {yaml_dq(meta['description'])}",
        f"keywords: [{', '.join(yaml_dq(k) for k in keywords)}]",
        f"author: {yaml_dq(meta['author'])}",
        f"version: {meta['version']}",
        "---",
    ])

    banner = (
        "<!-- GENERATED FILE - DO NOT EDIT. Source: "
        f"{skill_path}. Regenerate: python3 .github/scripts/build_power.py "
        f"{plugin_dir}. CI-owned (version sync), like "
        ".codex-plugin/plugin.json. -->"
    )

    doc = f"{front}\n\n{banner}\n\n{rewritten}\n"

    if os.path.isfile(mcp_path):
        mcp = json.load(open(mcp_path, encoding="utf-8"))
        servers = list((mcp.get("mcpServers") or {}).keys())
        if servers:
            names = ", ".join(f"`{s}`" for s in servers)
            doc += (
                "\n## MCP Tools (Kiro)\n\n"
                f"This Power bundles {names} (see `mcp.json`). Kiro registers "
                "it under the Powers section of `~/.kiro/settings/mcp.json` "
                "on install. The guidance above works without it.\n"
            )
    return doc


def main(argv):
    args = [a for a in argv if a != "--check"]
    check = "--check" in argv
    if len(args) != 1:
        raise SystemExit("usage: build_power.py <plugin_dir> [--check]")
    plugin_dir = args[0]
    generated = build_power(plugin_dir)
    dest = os.path.join(plugin_dir.rstrip("/"), "POWER.md")
    current = open(dest, encoding="utf-8").read() \
        if os.path.isfile(dest) else None

    if check:
        if current != generated:
            print(f"build_power: {dest} is out of sync with SKILL.md. "
                  f"Run: python3 .github/scripts/build_power.py {plugin_dir}")
            sys.exit(1)
        print(f"build_power: {dest} in sync")
        return
    if current == generated:
        print(f"build_power: {dest} already up to date")
        return
    with open(dest, "w", encoding="utf-8") as f:
        f.write(generated)
    print(f"build_power: wrote {dest}")


if __name__ == "__main__":
    main(sys.argv[1:])
