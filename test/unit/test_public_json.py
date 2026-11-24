import os
import re
from pathlib import Path

import pytest

PUBLIC_DIR = Path(os.environ.get("PUBLIC_DIR", "public"))

if not (PUBLIC_DIR / "show").is_dir():
    pytest.skip(f"{PUBLIC_DIR}/show not found; build the site first", allow_module_level=True)

JSON_FILES = sorted((PUBLIC_DIR / "show").glob("**/*.json"))


def test_bytes_are_written_as_plain_integers():
    """
    hugo --minify rewrites 50108000 as 50108e3, which JSON parsers read as a float
    """
    bad = []
    for path in JSON_FILES:
        for value in re.findall(r'"bytes":\s*([^,}\s]+)', path.read_text(encoding="utf-8")):
            if not value.isdigit():
                bad.append(f"{path}: bytes {value}")
    assert not bad, f"{len(bad)} non-integer bytes value(s):\n" + "\n".join(bad[:20])
