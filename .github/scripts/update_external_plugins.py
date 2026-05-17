#!/usr/bin/env python3
"""Auto-update external-plugin pins in agent-plugins.

Source of truth: .claude-plugin/marketplace.json (external entries where
`source` is an object with source == "github"). The matching entry in
.agents/plugins/marketplace.json (keyed by `name`) is kept in sync.

For each external plugin, resolve the latest eligible upstream release tag and,
if newer than the pinned ref, rewrite atomically:
  - .claude-plugin: entry.source.ref = vX.Y.Z   AND  entry.version = X.Y.Z
  - .agents:        entry.source.ref = vX.Y.Z   (no version field)

No third-party deps (stdlib only). Real errors exit non-zero; "nothing to do"
exits 0. `--dry-run` prints intended changes without writing.

Optional policy overlay: .github/external-plugin-updates.json
  {
    "defaults": {"includePrereleases": false,
                 "tagPattern": "^v?(\\\\d+\\\\.\\\\d+\\\\.\\\\d+)$",
                 "source": "github-releases"},
    "plugins": {"<name>": {"source": "github-tags", ...}}
  }
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

CLAUDE_MANIFEST = ".claude-plugin/marketplace.json"
AGENTS_MANIFEST = ".agents/plugins/marketplace.json"
POLICY_FILE = ".github/external-plugin-updates.json"

DEFAULTS = {
    "includePrereleases": False,
    "tagPattern": r"^v?(\d+\.\d+\.\d+)$",
    "source": "github-releases",  # or "github-tags"
}
API = "https://api.github.com"


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_json(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        fail(f"{path} not found")
    except json.JSONDecodeError as e:
        fail(f"{path}: invalid JSON: {e}")


def write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def gh_get(url: str):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "agent-plugins-external-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.headers
    except urllib.error.HTTPError as e:
        fail(f"GitHub API {url} -> HTTP {e.code} {e.reason}")
    except urllib.error.URLError as e:
        fail(f"GitHub API {url} unreachable: {e.reason}")


def paginate(url: str):
    items = []
    while url:
        page, headers = gh_get(url)
        if not isinstance(page, list):
            fail(f"expected a list from {url}")
        items.extend(page)
        url = ""
        link = headers.get("Link", "")
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part[part.find("<") + 1:part.find(">")]
    return items


def semver(t: str, pat: re.Pattern):
    m = pat.match(t)
    if not m:
        return None
    return tuple(int(x) for x in m.group(1).split("."))


def normalize_repo(agents_url: str) -> str:
    # git@github.com:owner/repo.git -> owner/repo
    m = re.match(r"^git@github\.com:(.+?)(?:\.git)?$", agents_url.strip())
    if m:
        return m.group(1)
    m = re.match(r"^https://github\.com/(.+?)(?:\.git)?$", agents_url.strip())
    if m:
        return m.group(1)
    return agents_url.strip()


def latest_version(repo: str, cfg: dict):
    pat = re.compile(cfg["tagPattern"])
    # rename / existence guard
    meta, _ = gh_get(f"{API}/repos/{repo}")
    if meta.get("full_name", "").lower() != repo.lower():
        fail(f"{repo}: upstream full_name is "
             f"{meta.get('full_name')!r} (renamed?) - update the manifest")

    candidates = []
    if cfg["source"] == "github-tags":
        for t in paginate(f"{API}/repos/{repo}/tags?per_page=100"):
            v = semver(t.get("name", ""), pat)
            if v:
                candidates.append((v, t["name"]))
    else:
        for r in paginate(f"{API}/repos/{repo}/releases?per_page=100"):
            if r.get("draft"):
                continue
            if r.get("prerelease") and not cfg["includePrereleases"]:
                continue
            v = semver(r.get("tag_name", ""), pat)
            if v:
                candidates.append((v, r["tag_name"]))
    if not candidates:
        fail(f"{repo}: no eligible release/tag matching {cfg['tagPattern']}")
    candidates.sort(key=lambda x: x[0])
    ver, tag = candidates[-1]
    return ".".join(str(n) for n in ver), tag


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    policy = {}
    if os.path.exists(POLICY_FILE):
        policy = load_json(POLICY_FILE)
    pdefaults = {**DEFAULTS, **(policy.get("defaults") or {})}
    poverrides = policy.get("plugins") or {}

    claude = load_json(CLAUDE_MANIFEST)
    agents = load_json(AGENTS_MANIFEST)
    agents_by_name = {p.get("name"): p for p in agents.get("plugins", [])}

    changed = []
    for entry in claude.get("plugins", []):
        src = entry.get("source")
        if not isinstance(src, dict) or src.get("source") != "github":
            continue  # inline or non-github external
        name = entry.get("name")
        repo = src.get("repo", "")
        if not re.match(r"^[\w.-]+/[\w.-]+$", repo):
            fail(f"{name}: invalid source.repo {repo!r}")

        a = agents_by_name.get(name)
        if a is None:
            fail(f"{name}: no matching entry in {AGENTS_MANIFEST}")
        a_src = a.get("source", {})
        a_repo = normalize_repo(a_src.get("url", ""))
        if a_repo.lower() != repo.lower():
            fail(f"{name}: {AGENTS_MANIFEST} repo {a_repo!r} != "
                 f"{repo!r} ({CLAUDE_MANIFEST})")

        cfg = {**pdefaults, **(poverrides.get(name) or {})}
        ver, tag = latest_version(repo, cfg)
        cur_ref = src.get("ref", "")
        if cur_ref == tag:
            print(f"  {name}: up to date ({tag})")
            continue

        changed.append((name, repo, cur_ref, tag))
        if args.dry_run:
            continue
        src["ref"] = tag
        entry["version"] = ver           # mirrored, no leading v
        a_src["ref"] = tag               # .agents: ref only

    if not changed:
        print("Nothing to update.")
        return 0

    print("\nplugin | repo | old -> new")
    for n, r, o, t in changed:
        print(f"  {n} | {r} | {o or '(none)'} -> {t}")

    if args.dry_run:
        print("\n(dry-run: no files written)")
        return 0

    write_json(CLAUDE_MANIFEST, claude)
    write_json(AGENTS_MANIFEST, agents)
    print(f"\nUpdated {CLAUDE_MANIFEST} and {AGENTS_MANIFEST}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
