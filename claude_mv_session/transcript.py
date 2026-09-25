#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

import json
from collections.abc import Iterable
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


def json_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def cwd_replacement(old_cwd: str, new_cwd: str) -> tuple[str, str]:
    return f'"cwd":{json_string(old_cwd)}', f'"cwd":{json_string(new_cwd)}'


def prefix_replacement(old_dir: Path, new_dir: Path) -> tuple[str, str]:
    return json_string(f"{old_dir}/")[1:-1], json_string(f"{new_dir}/")[1:-1]


def rewrite(data: bytes, replacements: Iterable[tuple[str, str]]) -> bytes:
    for old, new in replacements:
        data = data.replace(old.encode(), new.encode())
    return data
