import sys
from copy import deepcopy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.release_guard import validate_approval, validate_ci, validate_environment
from scripts.staging_host import (
    API_PREFIX,
    WEB_PREFIX,
    validate_manifest,
    validate_pair,
)

SHA = "a" * 40
PAIR = {"api": API_PREFIX + "a" * 64, "web": WEB_PREFIX + "b" * 64}
ENV = {
    "protection_rules": [
        {
            "type": "required_reviewers",
            "prevent_self_review": True,
            "reviewers": [{"id": 1}],
        }
    ],
    "deployment_branch_policy": {"custom_branch_policies": True},
}
BRANCHES = {"total_count": 1, "branch_policies": [{"name": "main", "type": "branch"}]}


def test_protected_environment():
    validate_environment(ENV, BRANCHES)


@pytest.mark.parametrize(
    "case",
    ["no_review", "self_review", "wildcard", "tag", "no_policy", "empty_reviewers"],
)
def test_environment_rejects_unsafe(case):
    env, branches = deepcopy(ENV), deepcopy(BRANCHES)
    if case == "no_review":
        env["protection_rules"] = []
    if case == "self_review":
        env["protection_rules"][0]["prevent_self_review"] = False
    if case == "wildcard":
        branches["branch_policies"][0]["name"] = "*"
    if case == "tag":
        branches["branch_policies"][0]["type"] = "tag"
    if case == "no_policy":
        env["deployment_branch_policy"] = {}
    if case == "empty_reviewers":
        env["protection_rules"][0]["reviewers"] = []
    with pytest.raises(ValueError):
        validate_environment(env, branches)


def test_independent_approval():
    validate_approval(
        [
            {
                "state": "approved",
                "user": {"login": "reviewer"},
                "environments": [{"name": "staging"}],
            }
        ],
        "author",
    )


@pytest.mark.parametrize(
    "review",
    [
        [],
        [
            {
                "state": "approved",
                "user": {"login": "author"},
                "environments": [{"name": "staging"}],
            }
        ],
        [
            {
                "state": "rejected",
                "user": {"login": "reviewer"},
                "environments": [{"name": "staging"}],
            }
        ],
        [
            {
                "state": "approved",
                "user": {"login": "reviewer"},
                "environments": [{"name": "production"}],
            }
        ],
    ],
)
def test_approval_denies_bypass(review):
    with pytest.raises(ValueError):
        validate_approval(review, "author")


def test_exact_ci():
    run = {
        "head_sha": SHA,
        "head_branch": "main",
        "event": "push",
        "status": "completed",
        "conclusion": "success",
    }
    validate_ci({"workflow_runs": [run]}, SHA)
    for field, value in [
        ("head_sha", "b" * 40),
        ("head_branch", "feature"),
        ("event", "pull_request"),
        ("status", "in_progress"),
        ("conclusion", "failure"),
    ]:
        with pytest.raises(ValueError):
            validate_ci({"workflow_runs": [{**run, field: value}]}, SHA)


@pytest.mark.parametrize(
    "value",
    [
        "latest",
        "sha256:" + "a" * 64,
        "ghcr.io/other/api@sha256:" + "a" * 64,
        API_PREFIX + "x" * 64,
        API_PREFIX + "a" * 63,
    ],
)
def test_digest_allowlist(value):
    with pytest.raises(ValueError):
        validate_pair({**PAIR, "api": value})


def test_manifest_and_baseline_drift():
    manifest = {"sha": SHA, "operation": "deploy", "baseline": PAIR, "target": PAIR}
    validate_manifest(manifest, PAIR)
    with pytest.raises(ValueError):
        validate_manifest(manifest, {**PAIR, "api": API_PREFIX + "c" * 64})
    with pytest.raises(ValueError):
        validate_manifest({**manifest, "extra": "untrusted"}, PAIR)
    with pytest.raises(ValueError):
        validate_manifest({**manifest, "sha": "main"}, PAIR)


def test_production_runtime_gate():
    from scripts.staging_host import validate_runtime

    runtime = {
        "APP_ENV": "production",
        "DEMO_ENABLED": "false",
        "JWT_SECRET": "synthetic-random-secret-value-0123456789",
        "DATABASE_URL": "postgresql://service:synthetic-strong-password@private-db/revenueops",
        "CORS_ORIGINS": '["https://staging.example.com"]',
    }
    validate_runtime(runtime)
    for key, value in [
        ("APP_ENV", "development"),
        ("DEMO_ENABLED", "true"),
        ("JWT_SECRET", "replace-with-at-least-32-random-characters"),
        ("DATABASE_URL", "postgresql://user:local-only@db/demo"),
        ("CORS_ORIGINS", '["http://example.com"]'),
    ]:
        with pytest.raises(ValueError):
            validate_runtime({**runtime, key: value})
