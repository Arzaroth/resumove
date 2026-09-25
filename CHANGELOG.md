# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- A move that fails while moving the companion directory no longer leaves the
  transcript in both projects, which made the next attempt refuse the session as
  found in several projects.

## [0.1.0] - 2026-09-25

### Added

- `resumove <session-id> <target-dir>` moves a Claude Code conversation to the
  project of another folder, so `claude --resume <session-id>` finds it when run
  from there. The transcript and its companion directory (tool results,
  subagent logs) move together, and the recorded `cwd` and the paths into the
  companion directory are rewritten.
- It refuses to move a conversation still open in a running `claude`, read from
  `~/.claude/sessions/` and checked against the process start time so a reused
  PID does not block it. It never overwrites anything at the destination.
- `CLAUDE_CONFIG_DIR` is honoured.

[Unreleased]: https://github.com/Arzaroth/resumove/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Arzaroth/resumove/releases/tag/v0.1.0
