#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

import argparse
import os
import shlex
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .errors import MoveError
from .mover import MovePlan, execute, plan_move
from .paths import config_dir

PROG = "claude-mv-session"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Move a Claude Code conversation so `claude --resume` works from a new folder.",
    )
    parser.add_argument("session_id", help="id of the conversation to move")
    parser.add_argument("target", type=Path, help="folder to resume the conversation from")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def report(plan: MovePlan) -> str:
    origin = plan.old_cwd or str(plan.source.project_dir)
    return (
        f"moved {plan.source.id}\n"
        f"  from {origin}\n"
        f"  to   {plan.target}\n"
        f"resume with: cd {shlex.quote(str(plan.target))} && claude --resume {plan.source.id}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        plan = plan_move(config_dir(os.environ), args.session_id, args.target)
        execute(plan)
    except MoveError as error:
        print(f"{PROG}: {error}", file=sys.stderr)
        return 1
    print(report(plan))
    return 0
