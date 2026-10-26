"""Read-only fail-closed GitHub release validation; never provisions or deploys."""

import json
import os
import re
import subprocess
import sys

ENVIRONMENT = "staging"


def github(path):
    return json.loads(subprocess.check_output(["gh", "api", path], text=True))


def validate_environment(environment, branches):
    protection = environment.get("protection_rules", [])
    if not any(
        rule.get("type") == "required_reviewers"
        and rule.get("prevent_self_review") is True
        and rule.get("reviewers")
        for rule in protection
    ):
        raise ValueError(
            "Staging requires independent reviewers and prevent-self-review"
        )
    if (environment.get("deployment_branch_policy") or {}).get(
        "custom_branch_policies"
    ) is not True:
        raise ValueError("Selected deployment branches required")
    policies = branches.get("branch_policies", [])
    if (
        branches.get("total_count") != 1
        or len(policies) != 1
        or policies[0].get("name") != "main"
        or policies[0].get("type") != "branch"
    ):
        raise ValueError("Only main may deploy")


def validate_ci(runs, sha):
    if not any(
        r.get("head_sha") == sha
        and r.get("head_branch") == "main"
        and r.get("event") == "push"
        and r.get("status") == "completed"
        and r.get("conclusion") == "success"
        for r in runs.get("workflow_runs", [])
    ):
        raise ValueError(
            "Exact source SHA requires successful Verify RevenueOps main push run"
        )


def validate_approval(reviews, actor):
    if not any(
        r.get("state") == "approved"
        and r.get("user", {}).get("login", "").lower() not in ("", actor.lower())
        and any(e.get("name") == ENVIRONMENT for e in r.get("environments", []))
        for r in reviews
    ):
        raise ValueError(
            "Recorded independent staging approval required; bypass is insufficient"
        )


def main():
    if (
        os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
    ):
        raise ValueError("Manual main dispatch only")
    sha = os.environ["RELEASE_SHA"]
    if not re.fullmatch("[0-9a-f]{40}", sha):
        raise ValueError("Full lowercase release SHA required")
    if (
        os.environ.get("CONFIRMATION") != "DEPLOY STAGING"
        or os.environ.get("SCHEMA_COMPATIBLE") != "true"
    ):
        raise ValueError(
            "Explicit staging and schema compatibility confirmations required"
        )
    subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"], check=True)
    repo = os.environ["GITHUB_REPOSITORY"]
    validate_environment(
        github(f"repos/{repo}/environments/{ENVIRONMENT}"),
        github(
            f"repos/{repo}/environments/{ENVIRONMENT}/deployment-branch-policies?per_page=100"
        ),
    )
    validate_ci(
        github(
            f"repos/{repo}/actions/workflows/verify.yml/runs?head_sha={sha}&event=push&status=completed&per_page=100"
        ),
        sha,
    )
    if len(sys.argv) > 1 and sys.argv[1] == "approved":
        validate_approval(
            github(
                f"repos/{repo}/actions/runs/{os.environ['GITHUB_RUN_ID']}/approvals"
            ),
            os.environ["GITHUB_ACTOR"],
        )
    print("Source, CI and independent release gates verified")


if __name__ == "__main__":
    main()
