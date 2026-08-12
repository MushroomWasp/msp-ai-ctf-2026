from __future__ import annotations

from pathlib import Path

import pytest

from shared.common.testing import load_module_from_path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _challenge_dirs() -> list[Path]:
    return sorted(
        path
        for path in (REPO_ROOT / "challenges").iterdir()
        if path.is_dir() and (path / "tests" / "config.py").exists()
    )


def load_cases():
    cases = []
    for root in _challenge_dirs():
        config = load_module_from_path(root / "tests" / "config.py")
        cases.append(
            pytest.param(
                {
                    "slug": root.name,
                    "root": root,
                    "expected_flag": config.EXPECTED_FLAG,
                    "solution": config.SOLUTION,
                },
                id=root.name,
            )
        )
    return cases


CASES = load_cases()
