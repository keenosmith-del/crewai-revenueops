"""Install manually on an EXISTING staging VM. Fixed paths/services, digest-only updates."""

import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path("/opt/revenueops/staging")
API_PREFIX = "ghcr.io/keenosmith-del/crewai-revenueops-api@sha256:"
WEB_PREFIX = "ghcr.io/keenosmith-del/crewai-revenueops-web@sha256:"


def validate_pair(pair):
    if set(pair) != {"api", "web"}:
        raise ValueError("Exactly an API/web image pair required")
    for name, prefix in [("api", API_PREFIX), ("web", WEB_PREFIX)]:
        if not isinstance(pair[name], str) or not re.fullmatch(
            re.escape(prefix) + "[0-9a-f]{64}", pair[name]
        ):
            raise ValueError("Only approved registry digest images permitted")
    return pair


def read_current(root=ROOT):
    text = (root / ".release.env").read_text()
    values = dict(line.split("=", 1) for line in text.splitlines() if line)
    return validate_pair({"api": values["API_IMAGE"], "web": values["WEB_IMAGE"]})


def validate_manifest(manifest, current):
    if set(manifest) != {"sha", "operation", "baseline", "target"}:
        raise ValueError("Unexpected manifest fields")
    if not re.fullmatch("[0-9a-f]{40}", manifest["sha"]) or manifest[
        "operation"
    ] not in ("deploy", "rollback"):
        raise ValueError("Invalid source or operation")
    validate_pair(manifest["baseline"])
    validate_pair(manifest["target"])
    if manifest["baseline"] != current:
        raise ValueError("Staging drifted after snapshot; promotion refused")


def validate_runtime(values):
    if (
        values.get("APP_ENV") != "production"
        or values.get("DEMO_ENABLED", "").lower() != "false"
    ):
        raise ValueError(
            "Staging must enforce production authentication with demo disabled"
        )
    secret = values.get("JWT_SECRET", "")
    if len(secret) < 32 or secret.startswith(("local-", "replace-")):
        raise ValueError("Staging requires a non-placeholder secret")
    database = values.get("DATABASE_URL", "")
    if not database.startswith("postgresql") or any(
        value in database for value in ("local-only", "ci-only")
    ):
        raise ValueError("Staging requires explicit PostgreSQL credentials")
    origins = json.loads(values.get("CORS_ORIGINS", "[]"))
    if not origins or any(
        not isinstance(origin, str) or not origin.startswith("https://")
        for origin in origins
    ):
        raise ValueError("Explicit HTTPS origins required")


def inspect_running(expected):
    for service in ("api", "worker", "web"):
        container = compose("ps", "-q", service).stdout.strip()
        if not container:
            raise ValueError("Existing running staging services required")
        actual = subprocess.check_output(
            ["docker", "inspect", "--format", "{{.Config.Image}}", container], text=True
        ).strip()
        if actual != expected["web" if service == "web" else "api"]:
            raise ValueError(
                "Running container reference drifted from recorded baseline"
            )


def compose(*arguments):
    return subprocess.run(
        [
            "docker",
            "compose",
            "--project-name",
            "revenueops-staging",
            "--env-file",
            str(ROOT / ".release.env"),
            "-f",
            str(ROOT / "compose.yaml"),
            *arguments,
        ],
        check=True,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def main():
    if not (ROOT / "EXISTING_STAGING_ONLY").is_file():
        raise ValueError("Existing staging marker required; no provisioning supported")
    runtime = dict(
        line.split("=", 1)
        for line in (ROOT / "runtime.env").read_text().splitlines()
        if line and not line.startswith("#")
    )
    validate_runtime(runtime)
    current = read_current()
    inspect_running(current)
    if len(sys.argv) > 1 and sys.argv[1] == "snapshot":
        print(json.dumps(current))
        return
    manifest = json.load(sys.stdin)
    validate_manifest(manifest, current)
    import fcntl

    with (ROOT / ".promotion.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        validate_manifest(manifest, read_current())
        inspect_running(current)
        backup = ROOT / "recovery" / f"{datetime.now(UTC):%Y%m%dT%H%M%S%f}.json"
        backup.write_text(
            json.dumps({"previous": current, "requested": manifest}, indent=2) + "\n"
        )
        # Verify immutable image provenance before changing desired runtime state.
        for image in manifest["target"].values():
            subprocess.run(
                ["docker", "pull", image], check=True, capture_output=True, text=True
            )
            revision = subprocess.check_output(
                [
                    "docker",
                    "image",
                    "inspect",
                    "--format",
                    '{{index .Config.Labels "org.opencontainers.image.revision"}}',
                    image,
                ],
                text=True,
            ).strip()
            if revision != manifest["sha"]:
                raise ValueError(
                    "Image revision does not match the verified release SHA"
                )
        temporary = ROOT / ".release.env.next"
        temporary.write_text(
            "API_IMAGE="
            + manifest["target"]["api"]
            + "\nWEB_IMAGE="
            + manifest["target"]["web"]
            + "\n"
        )
        os.replace(temporary, ROOT / ".release.env")
        compose("pull", "api", "worker", "web")
        compose(
            "up",
            "-d",
            "--no-build",
            "--wait",
            "--wait-timeout",
            "120",
            "api",
            "worker",
            "web",
        )
        for service in ("api", "worker", "web"):
            container = compose("ps", "-q", service).stdout.strip()
            actual = subprocess.check_output(
                ["docker", "inspect", "--format", "{{.Config.Image}}", container],
                text=True,
            ).strip()
            if actual != manifest["target"]["web" if service == "web" else "api"]:
                raise RuntimeError(
                    "Running container revision mismatch; reviewed rollback required"
                )
        print(
            json.dumps(
                {
                    "status": "promoted",
                    "images": manifest["target"],
                    "source": manifest["sha"],
                }
            )
        )


if __name__ == "__main__":
    main()
