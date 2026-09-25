#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

import json
from pathlib import Path

PROC_ROOT = Path("/proc")

_START_TIME_INDEX = 19


def session_is_live(sessions_dir: Path, session_id: str, proc_root: Path = PROC_ROOT) -> bool:
    for entry in sessions_dir.glob("*.json"):
        try:
            record = json.loads(entry.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(record, dict) or record.get("sessionId") != session_id:
            continue
        if process_matches(proc_root, record.get("pid"), record.get("procStart")):
            return True
    return False


def process_matches(proc_root: Path, pid: object, proc_start: object) -> bool:
    if not isinstance(pid, int) or isinstance(pid, bool):
        return False
    try:
        stat = (proc_root / str(pid) / "stat").read_text(encoding="utf-8")
    except OSError:
        return False
    if proc_start is None:
        return True
    fields = stat.rpartition(")")[2].split()
    return len(fields) > _START_TIME_INDEX and fields[_START_TIME_INDEX] == str(proc_start)
