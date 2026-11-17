"""Persist a real test run, with code hashes and dependency versions."""
import hashlib
import importlib.metadata
import io
import json
import platform
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
stream = io.StringIO()
suite = unittest.defaultTestLoader.discover(str(root/"tests"))
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
record = {"run_at_utc":datetime.now(timezone.utc).isoformat(),
    "python":platform.python_version(), "passed":result.wasSuccessful(),
    "tests_run":result.testsRun, "failures":len(result.failures), "errors":len(result.errors),
    "dependencies":{name:importlib.metadata.version(name) for name in ("Pillow","pyproj","shapely")},
    "inputs_sha256":{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [*sorted((root/"tools").glob("*.py")), *sorted((root/"tests").glob("*.py"))]},
    "output":stream.getvalue(),
    "scope":"Software validation on synthetic fixtures only; does not validate a crowd estimate."}
target = root/"results/verification.json"
target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(record, indent=2)+"\n")
print(stream.getvalue())
sys.exit(0 if result.wasSuccessful() else 1)
