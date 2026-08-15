"""Shared test bootstrap: load .env and put api/ on the path.

Import for the side effect, before importing anything from api/:

    import _env  # noqa: F401
"""

import os
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))

for _line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in _line and not _line.lstrip().startswith("#"):
        _k, _v = _line.split("=", 1)
        os.environ.setdefault(_k.strip(), _v.strip().strip('"'))
