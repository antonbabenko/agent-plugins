#!/usr/bin/env python3
"""Regression tests for three-manifest external plugin sync."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT_PATH = Path(__file__).with_name("validate_external_manifests.py")


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_external_manifests", SCRIPT_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def claude_manifest(ref: str = "v1.2.3") -> dict:
    return {
        "plugins": [
            {
                "name": "example",
                "source": {
                    "source": "github",
                    "repo": "example/plugin",
                    "ref": ref,
                },
                "version": ref.removeprefix("v"),
            }
        ]
    }


def mirror_manifest(ref: str = "v1.2.3", *, extra: bool = False) -> dict:
    plugins = [
        {
            "name": "example",
            "source": {
                "source": "url",
                "url": "git@github.com:example/plugin.git",
                "ref": ref,
            },
        }
    ]
    if extra:
        plugins.append(
            {
                "name": "stale",
                "source": {
                    "source": "url",
                    "url": "git@github.com:example/stale.git",
                    "ref": "v9.9.9",
                },
            }
        )
    return {"plugins": plugins}


class ExternalManifestSyncTests(unittest.TestCase):
    def test_accepts_matching_external_entries(self):
        validator = load_validator()
        self.assertEqual(
            validator.validate_manifests(
                claude_manifest(), mirror_manifest(), mirror_manifest()
            ),
            [],
        )

    def test_rejects_stale_agents_external_entry(self):
        validator = load_validator()
        errors = validator.validate_manifests(
            claude_manifest(), mirror_manifest(extra=True), mirror_manifest()
        )
        self.assertTrue(any("stale" in error and ".agents" in error for error in errors))

    def test_rejects_stale_kiro_external_entry(self):
        validator = load_validator()
        errors = validator.validate_manifests(
            claude_manifest(), mirror_manifest(), mirror_manifest(extra=True)
        )
        self.assertTrue(any("stale" in error and ".kiro" in error for error in errors))

    def test_rejects_ref_mismatch(self):
        validator = load_validator()
        errors = validator.validate_manifests(
            claude_manifest(), mirror_manifest(ref="v1.2.2"), mirror_manifest()
        )
        self.assertTrue(any("ref mismatch" in error for error in errors))

    def test_rejects_ref_version_mismatch(self):
        validator = load_validator()
        claude = claude_manifest()
        claude["plugins"][0]["version"] = "1.2.2"
        errors = validator.validate_manifests(
            claude, mirror_manifest(), mirror_manifest()
        )
        self.assertTrue(any("v+version" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
