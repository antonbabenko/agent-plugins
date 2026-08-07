#!/usr/bin/env python3
"""Regression tests for build_power.py frontmatter parsing."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT_PATH = Path(__file__).with_name("build_power.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("build_power", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BuildPowerFrontmatterTests(unittest.TestCase):
    def _plugin(self, root: Path, frontmatter: str) -> Path:
        plugin = root / "quoted-skill"
        skill_dir = plugin / "skills" / "quoted-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            frontmatter + "\n\n# Quoted Skill\n",
            encoding="utf-8",
        )
        codex = plugin / ".codex-plugin"
        codex.mkdir()
        (codex / "plugin.json").write_text(
            json.dumps(
                {
                    "interface": {"displayName": "Quoted Skill"},
                    "keywords": ["quoted", "yaml"],
                }
            ),
            encoding="utf-8",
        )
        return plugin

    def test_decodes_quoted_yaml_scalars_before_generating_power(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._plugin(
                Path(tmp),
                '''---
name: "quoted-skill"
description: "Use when: quoted YAML is required"
metadata:
  author: 'Example Author'
  version: "1.2.3"
---''',
            )

            generated = builder.build_power(str(plugin))

            self.assertIn('name: "quoted-skill"', generated)
            self.assertIn('description: "Use when: quoted YAML is required"', generated)
            self.assertIn('author: "Example Author"', generated)
            self.assertIn('version: 1.2.3', generated)
            self.assertNotIn('\\"quoted-skill\\"', generated)

    def test_keeps_existing_unquoted_frontmatter_behavior(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._plugin(
                Path(tmp),
                '''---
name: quoted-skill
description: Use when quoted YAML is not needed
metadata:
  author: Example Author
  version: 1.2.3
---''',
            )

            generated = builder.build_power(str(plugin))

            self.assertIn('name: "quoted-skill"', generated)
            self.assertIn('description: "Use when quoted YAML is not needed"', generated)
            self.assertIn('author: "Example Author"', generated)
            self.assertIn('version: 1.2.3', generated)


if __name__ == "__main__":
    unittest.main()
