#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

from .errors import MoveError

MAX_PROJECT_NAME_LENGTH = 200

_UNSAFE = re.compile(r"[^a-zA-Z0-9]")


def config_dir(env: Mapping[str, str]) -> Path:
    configured = env.get("CLAUDE_CONFIG_DIR")
    if configured:
        return Path(configured)
    return Path.home() / ".claude"


def project_name(folder: Path) -> str:
    name = _UNSAFE.sub("-", str(folder))
    if len(name) > MAX_PROJECT_NAME_LENGTH:
        raise MoveError(
            f"target path too long to encode safely ({len(name)} > {MAX_PROJECT_NAME_LENGTH} chars)"
        )
    return name
