import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.main import app

schema = app.openapi()
assert schema["components"]["schemas"]["Decision"]["additionalProperties"] is False
assert "/api/investigations/{case_id}/review" in schema["paths"]
assert all(
    "/send" not in path and "/payment/execute" not in path for path in schema["paths"]
)
assert all(
    "security" in operation
    for path, operations in schema["paths"].items()
    if path.startswith("/api/") and not path.startswith("/api/auth/")
    for operation in operations.values()
)
patterns = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b(?:sk-proj-|ghp_)[A-Za-z0-9_-]{30,}"),
]
files = (
    subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
)
for name in filter(None, files):
    path = ROOT / name
    if path.is_file() and path.suffix not in (".png", ".zip"):
        text = path.read_text(errors="replace")
        assert not any(pattern.search(text) for pattern in patterns), (
            f"Potential secret in {name}"
        )
print(
    f"API contracts and limited tracked-file secret scan passed ({len(files) - 1} files)."
)
