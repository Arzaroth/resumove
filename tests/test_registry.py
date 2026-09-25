#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

import os
from pathlib import Path

import pytest

from claude_mv_session.registry import process_matches, session_is_live

from .conftest import SESSION_ID, fake_process, register


def test_no_sessions_dir(tmp_path: Path, proc_root: Path) -> None:
    assert not session_is_live(tmp_path / "absent", SESSION_ID, proc_root)


def test_live_session(config: Path, proc_root: Path) -> None:
    fake_process(proc_root, 42, 1000)
    register(config, 42, procStart="1000")
    assert session_is_live(config / "sessions", SESSION_ID, proc_root)


def test_other_session_is_ignored(config: Path, proc_root: Path) -> None:
    fake_process(proc_root, 42, 1000)
    register(config, 42, session_id="99999999-2222-3333-4444-555555555555", procStart="1000")
    assert not session_is_live(config / "sessions", SESSION_ID, proc_root)


def test_dead_process_is_ignored(config: Path, proc_root: Path) -> None:
    register(config, 42, procStart="1000")
    assert not session_is_live(config / "sessions", SESSION_ID, proc_root)


def test_unusable_records_are_skipped(config: Path, proc_root: Path) -> None:
    sessions = config / "sessions"
    (sessions / "garbage.json").write_text("{not json")
    (sessions / "list.json").write_text("[1, 2]")
    (sessions / "dir.json").mkdir()
    assert not session_is_live(sessions, SESSION_ID, proc_root)


def test_default_proc_root_sees_this_process(config: Path) -> None:
    register(config, os.getpid())
    assert session_is_live(config / "sessions", SESSION_ID)


@pytest.mark.parametrize("pid", ["42", None, True, 4.2])
def test_process_matches_needs_integer_pid(proc_root: Path, pid: object) -> None:
    fake_process(proc_root, 42, 1000)
    assert not process_matches(proc_root, pid, "1000")


def test_process_matches_without_start_time(proc_root: Path) -> None:
    fake_process(proc_root, 42, 1000)
    assert process_matches(proc_root, 42, None)


@pytest.mark.parametrize("start", ["1000", 1000])
def test_process_matches_start_time(proc_root: Path, start: object) -> None:
    fake_process(proc_root, 42, 1000)
    assert process_matches(proc_root, 42, start)


def test_process_matches_rejects_reused_pid(proc_root: Path) -> None:
    fake_process(proc_root, 42, 1000)
    assert not process_matches(proc_root, 42, "999")


def test_process_matches_rejects_truncated_stat(proc_root: Path) -> None:
    (proc_root / "42").mkdir()
    (proc_root / "42" / "stat").write_text("42 (claude) S 1 2\n")
    assert not process_matches(proc_root, 42, "1000")
