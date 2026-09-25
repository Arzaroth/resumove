#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

from pathlib import Path

import pytest

from claude_mv_session.errors import MoveError
from claude_mv_session.paths import MAX_PROJECT_NAME_LENGTH, config_dir, project_name


def test_config_dir_honours_env() -> None:
    assert config_dir({"CLAUDE_CONFIG_DIR": "/somewhere"}) == Path("/somewhere")


@pytest.mark.parametrize("env", [{}, {"CLAUDE_CONFIG_DIR": ""}])
def test_config_dir_defaults_to_home(env: dict[str, str], monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    assert config_dir(env) == tmp_path / ".claude"


def test_project_name_replaces_every_non_alphanumeric() -> None:
    assert (
        project_name(Path("/home/me/Repos/project.worktrees/feature/x_1"))
        == "-home-me-Repos-project-worktrees-feature-x-1"
    )


def test_project_name_accepts_the_limit() -> None:
    assert len(project_name(Path("/" + "a" * (MAX_PROJECT_NAME_LENGTH - 1)))) == 200


def test_project_name_rejects_longer_paths() -> None:
    with pytest.raises(MoveError, match="too long"):
        project_name(Path("/" + "a" * MAX_PROJECT_NAME_LENGTH))
