#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from .errors import MoveError


@dataclass(frozen=True)
class Session:
    id: str
    project_dir: Path

    @property
    def transcript(self) -> Path:
        return self.project_dir / f"{self.id}.jsonl"

    @property
    def artifacts(self) -> Path:
        return self.project_dir / self.id


def find_session(projects_dir: Path, session_id: str) -> Session:
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise MoveError(f"not a session id: {session_id}") from None
    matches = sorted(projects_dir.glob(f"*/{session_id}.jsonl"))
    if not matches:
        raise MoveError(f"no session {session_id} under {projects_dir}")
    if len(matches) > 1:
        found = ", ".join(str(match) for match in matches)
        raise MoveError(f"session {session_id} found in several projects: {found}")
    return Session(session_id, matches[0].parent)
