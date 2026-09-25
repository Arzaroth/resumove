#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import annotations

from pathlib import Path

from claude_mv_session.transcript import (
    cwd_replacement,
    json_string,
    prefix_replacement,
    recorded_cwd,
    rewrite,
)


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


def test_json_string_keeps_non_ascii() -> None:
    assert json_string('/é/"q"') == '"/é/\\"q\\""'


def test_cwd_replacement() -> None:
    assert cwd_replacement("/a", "/b c") == ('"cwd":"/a"', '"cwd":"/b c"')


def test_prefix_replacement_is_unquoted_and_slash_terminated() -> None:
    assert prefix_replacement(Path("/p/-a/id"), Path("/p/-b/id")) == ("/p/-a/id/", "/p/-b/id/")


def test_rewrite_applies_every_replacement() -> None:
    data = b'{"cwd":"/a","p":"/p/-a/id/x","q":"/p/-a/idx"}'
    result = rewrite(data, [cwd_replacement("/a", "/é"), ("/p/-a/id/", "/p/-b/id/")])
    assert result == '{"cwd":"/é","p":"/p/-b/id/x","q":"/p/-a/idx"}'.encode()


def test_rewrite_leaves_other_cwd_mentions() -> None:
    data = b'{"cwd":"/a/b","text":"cd /a"}'
    assert rewrite(data, [cwd_replacement("/a", "/z")]) == data
