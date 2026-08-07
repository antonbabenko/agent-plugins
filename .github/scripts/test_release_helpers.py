#!/usr/bin/env python3
"""Regression tests for release commit semantics."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


HELPER_PATH = Path(__file__).with_name("release_helpers.py")


def load_helpers():
    spec = importlib.util.spec_from_file_location("release_helpers", HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BreakingChangeTests(unittest.TestCase):
    def test_accepts_conventional_breaking_change_footer(self):
        helpers = load_helpers()
        self.assertTrue(
            helpers.has_breaking_change_footer(
                "Context first.\n\nBREAKING CHANGE: remove the v1 API"
            )
        )

    def test_accepts_hyphenated_breaking_change_footer(self):
        helpers = load_helpers()
        self.assertTrue(
            helpers.has_breaking_change_footer(
                "BREAKING-CHANGE: remove the legacy config key"
            )
        )

    def test_rejects_plain_mention(self):
        helpers = load_helpers()
        self.assertFalse(
            helpers.has_breaking_change_footer(
                "No BREAKING CHANGE is expected; this remains compatible."
            )
        )

    def test_rejects_inline_colon_mention(self):
        helpers = load_helpers()
        self.assertFalse(
            helpers.has_breaking_change_footer(
                "Note: BREAKING CHANGE: is documented here, not declared."
            )
        )

    def test_requires_description(self):
        helpers = load_helpers()
        self.assertFalse(helpers.has_breaking_change_footer("BREAKING CHANGE:   "))


if __name__ == "__main__":
    unittest.main()
