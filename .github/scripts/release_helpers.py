#!/usr/bin/env python3
"""Helpers shared by the per-plugin release workflow and regression tests."""

from __future__ import annotations

import re


_BREAKING_FOOTER_RE = re.compile(
    r"(?m)^BREAKING(?: CHANGE|-CHANGE):[ \t]+\S"
)


def has_breaking_change_footer(body: str) -> bool:
    """Return True only for a Conventional Commits breaking-change footer."""
    return _BREAKING_FOOTER_RE.search(body or "") is not None
