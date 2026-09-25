#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

import contextlib
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .errors import MoveError
from .paths import project_name
from .registry import PROC_ROOT, session_is_live
from .store import Session, find_session
from .transcript import recorded_cwd, relocate


@dataclass(frozen=True)
class MovePlan:
    source: Session
    destination: Session
    target: Path
    old_cwd: str | None


def plan_move(config: Path, session_id: str, target: Path, proc_root: Path = PROC_ROOT) -> MovePlan:
    if not target.is_dir():
        raise MoveError(f"target is not a directory: {target}")
    target = target.resolve()

    projects = config / "projects"
    source = find_session(projects, session_id)
    destination = Session(session_id, projects / project_name(target))

    if destination.project_dir == source.project_dir:
        raise MoveError(f"session already belongs to {target}")
    if destination.artifacts.exists():
        raise MoveError(f"destination already has {destination.artifacts}")
    if session_is_live(config / "sessions", session_id, proc_root):
        raise MoveError(f"session {session_id} is open in a running claude, quit it first")

    return MovePlan(source, destination, target, recorded_cwd(source.transcript))


def execute(plan: MovePlan) -> None:
    source, destination = plan.source, plan.destination
    destination.project_dir.mkdir(parents=True, exist_ok=True)

    data = relocate(
        source.transcript.read_bytes(),
        source.artifacts,
        destination.artifacts,
        plan.old_cwd,
        plan.target,
    )
    write_like(destination.transcript, data, source.transcript)
    if source.artifacts.is_dir():
        source.artifacts.rename(destination.artifacts)
    source.transcript.unlink()

    with contextlib.suppress(OSError):
        source.project_dir.rmdir()


def write_like(path: Path, data: bytes, template: Path) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(data)
        shutil.copystat(template, tmp)
        tmp.replace(path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
