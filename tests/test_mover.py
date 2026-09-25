#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

from claude_mv_session.errors import MoveError
from claude_mv_session.mover import MovePlan, execute, plan_move
from claude_mv_session.paths import project_name
from claude_mv_session.store import Session

from .conftest import OLD_CWD, SESSION_ID, fake_process, make_session, register


def entries(transcript: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in transcript.read_text().splitlines()]


def test_plan_move(config: Path, target: Path, proc_root: Path) -> None:
    source_dir = make_session(config)
    plan = plan_move(config, SESSION_ID, target, proc_root)
    assert plan == MovePlan(
        source=Session(SESSION_ID, source_dir),
        destination=Session(SESSION_ID, config / "projects" / project_name(target)),
        target=target,
        old_cwd=OLD_CWD,
    )


def test_plan_move_resolves_target(
    config: Path, target: Path, proc_root: Path, monkeypatch, tmp_path: Path
) -> None:
    make_session(config)
    (tmp_path / "link").symlink_to(target)
    monkeypatch.chdir(tmp_path)
    assert plan_move(config, SESSION_ID, Path("link"), proc_root).target == target


def test_plan_move_rejects_missing_target(config: Path, tmp_path: Path, proc_root: Path) -> None:
    make_session(config)
    with pytest.raises(MoveError, match="not a directory"):
        plan_move(config, SESSION_ID, tmp_path / "absent", proc_root)


def test_plan_move_rejects_file_target(config: Path, tmp_path: Path, proc_root: Path) -> None:
    make_session(config)
    file = tmp_path / "file"
    file.write_text("")
    with pytest.raises(MoveError, match="not a directory"):
        plan_move(config, SESSION_ID, file, proc_root)


def test_plan_move_rejects_same_project(config: Path, target: Path, proc_root: Path) -> None:
    make_session(config, project=project_name(target))
    with pytest.raises(MoveError, match="already belongs"):
        plan_move(config, SESSION_ID, target, proc_root)


def test_plan_move_never_overwrites_artifacts(config: Path, target: Path, proc_root: Path) -> None:
    make_session(config)
    (config / "projects" / project_name(target) / SESSION_ID).mkdir(parents=True)
    with pytest.raises(MoveError, match="destination already has"):
        plan_move(config, SESSION_ID, target, proc_root)


def test_plan_move_never_overwrites_transcript(config: Path, target: Path, proc_root: Path) -> None:
    make_session(config)
    make_session(config, project=project_name(target))
    with pytest.raises(MoveError, match="several projects"):
        plan_move(config, SESSION_ID, target, proc_root)


def test_plan_move_refuses_live_session(config: Path, target: Path, proc_root: Path) -> None:
    make_session(config)
    fake_process(proc_root, 42, 1000)
    register(config, 42, procStart="1000")
    with pytest.raises(MoveError, match="running claude"):
        plan_move(config, SESSION_ID, target, proc_root)


def test_execute_moves_and_rewrites(config: Path, target: Path, proc_root: Path) -> None:
    source_dir = make_session(config)
    os.utime(source_dir / f"{SESSION_ID}.jsonl", (1_000_000, 1_000_000))
    plan = plan_move(config, SESSION_ID, target, proc_root)

    execute(plan)

    moved = plan.destination
    assert not source_dir.exists()
    assert (moved.artifacts / "tool-results" / "a.txt").read_text() == "hi"
    first, second = entries(moved.transcript)
    assert first["cwd"] == str(target)
    assert second["path"] == str(moved.artifacts / "tool-results" / "a.txt")
    assert moved.transcript.stat().st_mtime == 1_000_000
    assert {p.name for p in moved.project_dir.iterdir()} == {SESSION_ID, f"{SESSION_ID}.jsonl"}


def test_execute_without_cwd_or_artifacts(config: Path, target: Path, proc_root: Path) -> None:
    make_session(config, cwd=None, with_artifacts=False)
    plan = plan_move(config, SESSION_ID, target, proc_root)
    assert plan.old_cwd is None

    execute(plan)

    assert not plan.destination.artifacts.exists()
    first, _ = entries(plan.destination.transcript)
    assert "cwd" not in first


def test_execute_keeps_non_empty_source_project(
    config: Path, target: Path, proc_root: Path
) -> None:
    source_dir = make_session(config)
    (source_dir / "memory").mkdir()
    execute(plan_move(config, SESSION_ID, target, proc_root))
    assert [p.name for p in source_dir.iterdir()] == ["memory"]


def test_execute_into_existing_project(config: Path, target: Path, proc_root: Path) -> None:
    make_session(config)
    make_session(
        config, project=project_name(target), session_id="99999999-2222-3333-4444-555555555555"
    )
    plan = plan_move(config, SESSION_ID, target, proc_root)
    execute(plan)
    assert plan.destination.transcript.exists()


def test_execute_cleans_up_on_failure(
    config: Path, target: Path, proc_root: Path, monkeypatch
) -> None:
    source_dir = make_session(config)
    original = (source_dir / f"{SESSION_ID}.jsonl").read_bytes()
    plan = plan_move(config, SESSION_ID, target, proc_root)

    def fail(*_: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(shutil, "copystat", fail)
    with pytest.raises(OSError, match="disk full"):
        execute(plan)

    assert list(plan.destination.project_dir.iterdir()) == []
    assert (source_dir / f"{SESSION_ID}.jsonl").read_bytes() == original
    assert plan.source.artifacts.is_dir()
