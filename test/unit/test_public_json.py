import json
import os
from pathlib import Path

import pytest

PUBLIC_DIR = Path(os.environ.get("PUBLIC_DIR", "public"))

if not (PUBLIC_DIR / "show").is_dir():
    pytest.skip(f"{PUBLIC_DIR}/show not found; build the site first", allow_module_level=True)

JSON_FILES = sorted((PUBLIC_DIR / "show").glob("**/*.json"))


def test_every_emitted_json_parses():
    failures = []
    for path in JSON_FILES:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError) as e:
            failures.append(f"{path}: {e}")
    assert not failures, f"{len(failures)} invalid JSON file(s):\n" + "\n".join(failures[:20])


def test_every_json_has_schema_version_and_type():
    problems = []
    shows = episodes = lists = 0
    for path in JSON_FILES:
        expected = {"show.json": "show", "episodes.json": "episodes"}.get(path.name, "episode")
        if expected == "show":
            shows += 1
        elif expected == "episodes":
            lists += 1
        else:
            episodes += 1
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError) as e:
            problems.append(f"{path}: unparseable: {e}")
            continue
        if not isinstance(data, dict):
            problems.append(f"{path}: top level is {type(data).__name__}, not an object")
        elif data.get("schema_version") != 1 or data.get("type") != expected:
            problems.append(
                f"{path}: schema_version={data.get('schema_version')!r} "
                f"type={data.get('type')!r} (expected 1, {expected!r})"
            )
    assert shows, "no show.json files found"
    assert episodes, "no episode json files found"
    assert not problems, f"{len(problems)} bad file(s):\n" + "\n".join(problems[:20])
