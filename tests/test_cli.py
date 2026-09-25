#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

from claude_mv_session import __version__
from claude_mv_session.cli import main, report
from claude_mv_session.mover import MovePlan
from claude_mv_session.store import Session

from .conftest import OLD_CWD, SESSION_ID, make_session


@pytest.fixture(autouse=True)
def isolated_config(config: Path, monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(config))


def test_main_moves_session(config: Path, target: Path, capsys) -> None:
    make_session(config)
    assert main([SESSION_ID, str(target)]) == 0
    out = capsys.readouterr().out
    assert f"from {OLD_CWD}" in out
    assert f"claude --resume {SESSION_ID}" in out


def test_main_reports_errors(capsys, target: Path) -> None:
    assert main([SESSION_ID, str(target)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("claude-mv-session: no session")


def test_main_requires_both_arguments(capsys) -> None:
    with pytest.raises(SystemExit) as caught:
        main([SESSION_ID])
    assert caught.value.code == 2
    assert "target" in capsys.readouterr().err


def test_version(capsys) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["--version"])
    assert caught.value.code == 0
    assert capsys.readouterr().out.strip() == f"claude-mv-session {__version__}"


def test_report_quotes_target_and_falls_back_to_project_dir() -> None:
    plan = MovePlan(
        source=Session(SESSION_ID, Path("/p/-old")),
        destination=Session(SESSION_ID, Path("/p/-new-dir")),
        target=Path("/new dir"),
        old_cwd=None,
    )
    assert report(plan) == (
        f"moved {SESSION_ID}\n"
        "  from /p/-old\n"
        "  to   /new dir\n"
        f"resume with: cd '/new dir' && claude --resume {SESSION_ID}"
    )


def test_module_entry_point(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["claude-mv-session", "--version"])
    with pytest.raises(SystemExit) as caught:
        runpy.run_module("claude_mv_session", run_name="__main__")
    assert caught.value.code == 0
    assert __version__ in capsys.readouterr().out
