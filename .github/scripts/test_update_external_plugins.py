#!/usr/bin/env python3
"""Regression tests for update_external_plugins.py."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT_PATH = Path(__file__).with_name("update_external_plugins.py")
SPEC = importlib.util.spec_from_file_location("update_external_plugins", SCRIPT_PATH)
UPDATER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(UPDATER)


class ExternalPluginUpdaterTests(unittest.TestCase):
    def _write_fixture(self, root: Path, ref: str, version: str) -> None:
        claude = {
            "name": "test",
            "owner": {"name": "Test"},
            "version": "1.0.0",
            "plugins": [
                {
                    "name": "example",
                    "source": {
                        "source": "github",
                        "repo": "example/plugin",
                        "ref": ref,
                    },
                    "description": "fixture",
                    "version": version,
                }
            ],
        }
        mirror = {
            "plugins": [
                {
                    "name": "example",
                    "source": {
                        "source": "url",
                        "url": "git@github.com:example/plugin.git",
                        "ref": ref,
                    },
                }
            ]
        }

        for path, data in (
            (root / ".claude-plugin" / "marketplace.json", claude),
            (root / ".agents" / "plugins" / "marketplace.json", mirror),
            (root / ".kiro" / "plugins" / "marketplace.json", mirror),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def _run_main(self, root: Path, latest_version: str, latest_tag: str):
        old_cwd = Path.cwd()
        try:
            os.chdir(root)
            with mock.patch.object(
                UPDATER,
                "latest_version",
                return_value=(latest_version, latest_tag),
            ), mock.patch.object(sys, "argv", ["update_external_plugins.py"]):
                return UPDATER.main()
        finally:
            os.chdir(old_cwd)

    def _manifest_state(self, root: Path) -> tuple[str, str, str, str]:
        claude = json.loads(
            (root / ".claude-plugin" / "marketplace.json").read_text()
        )
        agents = json.loads(
            (root / ".agents" / "plugins" / "marketplace.json").read_text()
        )
        kiro = json.loads(
            (root / ".kiro" / "plugins" / "marketplace.json").read_text()
        )
        return (
            claude["plugins"][0]["source"]["ref"],
            claude["plugins"][0]["version"],
            agents["plugins"][0]["source"]["ref"],
            kiro["plugins"][0]["source"]["ref"],
        )

    def test_refuses_automatic_downgrade(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root, ref="v2.0.0", version="2.0.0")

            with self.assertRaises(SystemExit) as exc:
                self._run_main(root, latest_version="1.9.0", latest_tag="v1.9.0")

            self.assertEqual(exc.exception.code, 1)
            self.assertEqual(
                self._manifest_state(root),
                ("v2.0.0", "2.0.0", "v2.0.0", "v2.0.0"),
            )

    def test_allows_upgrade(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root, ref="v1.9.0", version="1.9.0")

            result = self._run_main(
                root, latest_version="2.0.0", latest_tag="v2.0.0"
            )

            self.assertEqual(result, 0)
            self.assertEqual(
                self._manifest_state(root),
                ("v2.0.0", "2.0.0", "v2.0.0", "v2.0.0"),
            )


if __name__ == "__main__":
    unittest.main()
