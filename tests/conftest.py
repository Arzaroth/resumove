#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

import json
from pathlib import Path

import pytest

SESSION_ID = "11111111-2222-3333-4444-555555555555"
OLD_CWD = "/old/place"
OLD_PROJECT = "-old-place"


@pytest.fixture
def config(tmp_path: Path) -> Path:
    path = tmp_path / "claude"
    (path / "projects").mkdir(parents=True)
    (path / "sessions").mkdir()
    return path


@pytest.fixture
def proc_root(tmp_path: Path) -> Path:
    path = tmp_path / "proc"
    path.mkdir()
    return path


@pytest.fixture
def target(tmp_path: Path) -> Path:
    path = tmp_path / "new.dir" / "x"
    path.mkdir(parents=True)
    return path


def make_session(
    config: Path,
    project: str = OLD_PROJECT,
    session_id: str = SESSION_ID,
    cwd: str | None = OLD_CWD,
    with_artifacts: bool = True,
) -> Path:
    project_dir = config / "projects" / project
    project_dir.mkdir(parents=True, exist_ok=True)
    artifact = project_dir / session_id / "tool-results" / "a.txt"
    entries: list[dict[str, object]] = [{"type": "user", "cwd": cwd} if cwd else {"type": "user"}]
    entries.append({"type": "tool", "path": str(artifact)})
    (project_dir / f"{session_id}.jsonl").write_text(
        "".join(json.dumps(entry, separators=(",", ":")) + "\n" for entry in entries)
    )
    if with_artifacts:
        artifact.parent.mkdir(parents=True)
        artifact.write_text("hi")
    return project_dir


def register(config: Path, pid: object, session_id: str = SESSION_ID, **extra: object) -> None:
    record = {"pid": pid, "sessionId": session_id, **extra}
    (config / "sessions" / f"{pid}.json").write_text(json.dumps(record))


def fake_process(proc_root: Path, pid: int, start: int) -> None:
    fields = ["S", *["0"] * 18, str(start), *["0"] * 5]
    process = proc_root / str(pid)
    process.mkdir()
    (process / "stat").write_text(f"{pid} (claude (x)) {' '.join(fields)}\n")
