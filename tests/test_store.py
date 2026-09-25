#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

from pathlib import Path

import pytest

from claude_mv_session.errors import MoveError
from claude_mv_session.store import Session, find_session, validate_session_id

from .conftest import SESSION_ID, make_session


def test_session_paths() -> None:
    session = Session(SESSION_ID, Path("/p/-proj"))
    assert session.transcript == Path(f"/p/-proj/{SESSION_ID}.jsonl")
    assert session.artifacts == Path(f"/p/-proj/{SESSION_ID}")


def test_validate_session_id_accepts_uuid() -> None:
    assert validate_session_id(SESSION_ID) == SESSION_ID


@pytest.mark.parametrize("session_id", ["nope", "*", "../../etc/passwd"])
def test_validate_session_id_rejects_non_uuid(session_id: str) -> None:
    with pytest.raises(MoveError, match="not a session id"):
        validate_session_id(session_id)


def test_find_session_rejects_bad_id_before_globbing(config: Path) -> None:
    with pytest.raises(MoveError, match="not a session id"):
        find_session(config / "projects", "*")


def test_find_session_locates_project(config: Path) -> None:
    project_dir = make_session(config)
    assert find_session(config / "projects", SESSION_ID) == Session(SESSION_ID, project_dir)


def test_find_session_reports_missing(config: Path) -> None:
    with pytest.raises(MoveError, match="no session"):
        find_session(config / "projects", SESSION_ID)


def test_find_session_tolerates_missing_projects_dir(tmp_path: Path) -> None:
    with pytest.raises(MoveError, match="no session"):
        find_session(tmp_path / "absent", SESSION_ID)


def test_find_session_refuses_ambiguous_match(config: Path) -> None:
    make_session(config, project="-a")
    make_session(config, project="-b")
    with pytest.raises(MoveError, match="several projects") as caught:
        find_session(config / "projects", SESSION_ID)
    assert "-a" in str(caught.value) and "-b" in str(caught.value)
