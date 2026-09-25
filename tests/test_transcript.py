#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

from pathlib import Path

from resumove.transcript import recorded_cwd, relocate

OLD = Path("/p/-a/id")
NEW = Path("/p/-b/id")


def test_recorded_cwd_takes_first_usable_entry(tmp_path: Path) -> None:
    transcript = tmp_path / "t.jsonl"
    lines = [
        "not json",
        "[1]",
        '{"type":"summary"}',
        '{"cwd":42}',
        '{"cwd":"/first"}',
        '{"cwd":"/second"}',
    ]
    transcript.write_text("\n".join(lines) + "\n")
    assert recorded_cwd(transcript) == "/first"


def test_recorded_cwd_without_any(tmp_path: Path) -> None:
    transcript = tmp_path / "t.jsonl"
    transcript.write_text('{"type":"summary"}\n')
    assert recorded_cwd(transcript) is None


def test_relocate_rewrites_artifact_paths_and_cwd() -> None:
    data = b'{"cwd":"/a","p":"/p/-a/id/x","q":"/p/-a/idx"}'
    result = relocate(data, OLD, NEW, "/a", Path("/é"))
    assert result == '{"cwd":"/é","p":"/p/-b/id/x","q":"/p/-a/idx"}'.encode()


def test_relocate_matches_json_escaped_values() -> None:
    data = '{"cwd":"/é/\\"q\\"","p":"/p/-é/id/x"}'.encode()
    result = relocate(data, Path("/p/-é/id"), NEW, '/é/"q"', Path("/z"))
    assert result == b'{"cwd":"/z","p":"/p/-b/id/x"}'


def test_relocate_leaves_other_cwd_mentions() -> None:
    data = b'{"cwd":"/a/b","text":"cd /a"}'
    assert relocate(data, OLD, NEW, "/a", Path("/z")) == data


def test_relocate_without_cwd_keeps_it() -> None:
    data = b'{"cwd":"/a","p":"/p/-a/id/x"}'
    assert relocate(data, OLD, NEW, None, Path("/z")) == b'{"cwd":"/a","p":"/p/-b/id/x"}'
