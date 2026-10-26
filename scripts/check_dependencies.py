"""Fail on new advisories; show precise reviewed, expiring exceptions without hiding them."""

import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
policy = json.loads((ROOT / "docs/security/dependency-exceptions.json").read_text())
if date.today() > date.fromisoformat(policy["expires"]):
    raise SystemExit("Dependency exception review expired")
with tempfile.TemporaryDirectory() as temp:
    output = Path(temp) / "audit.json"
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip_audit",
            "--disable-pip",
            "--no-deps",
            "-r",
            str(ROOT / "backend/requirements-lock.txt"),
            "-f",
            "json",
            "-o",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if process.returncode not in (0, 1) or not output.exists():
        raise SystemExit("Dependency audit could not execute; no clean-security claim")
    report = json.loads(output.read_text())
allowed = {(e["package"], e["version"], e["id"]) for e in policy["exceptions"]}
unknown = []
for dependency in report["dependencies"]:
    for issue in dependency["vulns"]:
        key = (dependency["name"], dependency["version"], issue["id"])
        if key in allowed:
            print("Reviewed residual finding: " + ":".join(key))
        else:
            unknown.append(key)
if unknown:
    raise SystemExit("Unreviewed dependency advisories: " + str(unknown))
print(
    "No unreviewed advisories. Documented residual findings remain; not a zero-vulnerability result."
)
