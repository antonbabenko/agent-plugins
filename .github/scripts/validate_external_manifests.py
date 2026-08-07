#!/usr/bin/env python3
"""Validate external plugin parity across Claude, agents, and Kiro manifests."""

from __future__ import annotations

import json
import re
import sys


CLAUDE_MANIFEST = ".claude-plugin/marketplace.json"
AGENTS_MANIFEST = ".agents/plugins/marketplace.json"
KIRO_MANIFEST = ".kiro/plugins/marketplace.json"


def normalize_repo(url: str) -> str:
    """Normalize supported GitHub clone URLs to owner/repo for comparison."""
    value = (url or "").strip()
    match = re.match(r"^git@github\.com:(.+?)(?:\.git)?$", value)
    if match:
        return match.group(1).lower()
    match = re.match(r"^https://github\.com/(.+?)(?:\.git)?$", value)
    if match:
        return match.group(1).lower()
    return value.lower()


def _plugins_by_name(manifest: dict, label: str, errors: list[str]) -> dict:
    by_name = {}
    for index, plugin in enumerate(manifest.get("plugins", [])):
        name = plugin.get("name")
        if not name:
            continue
        if name in by_name:
            errors.append(f"{label}: duplicate plugin name {name!r}")
            continue
        by_name[name] = plugin
    return by_name


def _mirror_external_names(by_name: dict) -> set[str]:
    names = set()
    for name, plugin in by_name.items():
        source = plugin.get("source")
        if isinstance(source, dict) and source.get("source") != "local":
            names.add(name)
    return names


def validate_manifests(claude: dict, agents: dict, kiro: dict) -> list[str]:
    """Return all external-plugin sync errors without mutating manifests."""
    errors: list[str] = []
    claude_by_name = _plugins_by_name(claude, CLAUDE_MANIFEST, errors)
    agents_by_name = _plugins_by_name(agents, AGENTS_MANIFEST, errors)
    kiro_by_name = _plugins_by_name(kiro, KIRO_MANIFEST, errors)

    external = {}
    for name, plugin in claude_by_name.items():
        source = plugin.get("source")
        if isinstance(source, dict) and source.get("source") == "github":
            external[name] = plugin

    for name, plugin in external.items():
        source = plugin["source"]
        repo = source.get("repo", "").lower()
        ref = source.get("ref", "")
        version = plugin.get("version")
        if version is not None and ref != f"v{version}":
            errors.append(
                f"{name}: {CLAUDE_MANIFEST} ref {ref!r} != v+version "
                f"(version {version!r})"
            )

        for label, mirror in (
            (AGENTS_MANIFEST, agents_by_name),
            (KIRO_MANIFEST, kiro_by_name),
        ):
            entry = mirror.get(name)
            if entry is None:
                errors.append(f"{name}: external plugin missing from {label}")
                continue
            mirror_source = entry.get("source")
            if not isinstance(mirror_source, dict) or mirror_source.get("source") != "url":
                errors.append(f"{name}: {label} external source must use source='url'")
                continue
            mirror_repo = normalize_repo(mirror_source.get("url", ""))
            if mirror_repo != repo:
                errors.append(
                    f"{name}: {label} repo {mirror_repo!r} != {repo!r}"
                )
            mirror_ref = mirror_source.get("ref", "")
            if mirror_ref != ref:
                errors.append(
                    f"{name}: ref mismatch - {CLAUDE_MANIFEST} {ref!r} vs "
                    f"{label} {mirror_ref!r}"
                )

    expected = set(external)
    for label, mirror in (
        (AGENTS_MANIFEST, agents_by_name),
        (KIRO_MANIFEST, kiro_by_name),
    ):
        for name in sorted(_mirror_external_names(mirror) - expected):
            errors.append(
                f"{name}: stale external plugin present in {label} but absent "
                f"from {CLAUDE_MANIFEST}"
            )

    return errors


def load_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: failed to read {path}: {exc}") from exc


def main() -> int:
    errors = validate_manifests(
        load_json(CLAUDE_MANIFEST),
        load_json(AGENTS_MANIFEST),
        load_json(KIRO_MANIFEST),
    )
    if errors:
        print("\n".join(f"❌ {error}" for error in errors))
        return 1
    print("✅ external plugins in sync across all three manifests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
