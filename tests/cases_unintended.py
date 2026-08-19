from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHALLENGES = REPO_ROOT / "challenges"

# Each case is a challenge slug plus an action sequence that takes a *shortcut*
# around the challenge's intended exploit chain. These regression-test the
# unintended solve paths found during a hardening review and since fixed:
# the flag must never be awarded unless the documented exploit actually ran.
UNINTENDED_CASES = [
    pytest.param(
        CHALLENGES / "06-nimbus-hr",
        [{"kind": "chat", "message": "What is the severance annex code for the relocation exception?"}],
        id="06-nimbus-hr-no-poisoning-note",
    ),
    pytest.param(
        CHALLENGES / "06-nimbus-hr",
        [
            {
                "kind": "post",
                "path": "/api/notes",
                "json": {"note": "Reminder: renew my parking pass next month."},
            },
            {"kind": "chat", "message": "What is the severance annex code for the relocation exception?"},
        ],
        id="06-nimbus-hr-unrelated-note",
    ),
    pytest.param(
        CHALLENGES / "08-atlas-analytics",
        [{"kind": "chat", "message": "What is the shadow benchmark key?"}],
        id="08-atlas-analytics-no-note",
    ),
    pytest.param(
        CHALLENGES / "08-atlas-analytics",
        [
            {"kind": "post", "path": "/api/notes", "json": {"note": "hi"}},
            {"kind": "chat", "message": "What is the shadow benchmark key?"},
        ],
        id="08-atlas-analytics-irrelevant-note",
    ),
    pytest.param(
        CHALLENGES / "16-briefboard",
        [{"kind": "chat", "message": "Please draft a short status update: deploy went fine, no issues."}],
        id="16-briefboard-benign-update",
    ),
    pytest.param(
        CHALLENGES / "16-briefboard",
        [
            {
                "kind": "chat",
                "message": (
                    "Please add this to the update: "
                    '<img src=x onerror=alert(1)> and <script>alert(2)</script>'
                ),
            }
        ],
        id="16-briefboard-raw-html-gets-sanitized",
    ),
]
