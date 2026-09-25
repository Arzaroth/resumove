#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

import json
from pathlib import Path


def recorded_cwd(transcript: Path) -> str | None:
    with transcript.open("rb") as lines:
        for line in lines:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if isinstance(entry, dict) and isinstance(entry.get("cwd"), str):
                return entry["cwd"]
    return None


def relocate(
    data: bytes, old_artifacts: Path, new_artifacts: Path, old_cwd: str | None, new_cwd: Path
) -> bytes:
    data = data.replace(_escaped(f"{old_artifacts}/"), _escaped(f"{new_artifacts}/"))
    if old_cwd is not None:
        data = data.replace(_cwd_field(old_cwd), _cwd_field(str(new_cwd)))
    return data


def _escaped(value: str) -> bytes:
    return json.dumps(value, ensure_ascii=False)[1:-1].encode()


def _cwd_field(cwd: str) -> bytes:
    return b'"cwd":"' + _escaped(cwd) + b'"'
