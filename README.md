# resumove

Move a Claude Code conversation to another folder, so `claude --resume <id>` finds it
when run from there.

Claude Code files each conversation under `~/.claude/projects/<folder>/`, where
`<folder>` is the working directory with every non-alphanumeric character turned
into `-`. `claude --resume` only lists conversations of the current folder. This
tool moves the transcript (`<id>.jsonl`) and its companion directory (tool
results, subagent logs) to the target folder's project, and rewrites the recorded
`cwd` and the paths into that companion directory.

## Usage

```bash
resumove <session-id> <target-dir>
cd <target-dir> && claude --resume <session-id>
```

It refuses to move a conversation that is still open in a running `claude`
(read from `~/.claude/sessions/`), to overwrite anything at the destination, or to
encode a target path longer than 200 characters. `CLAUDE_CONFIG_DIR` is honoured.

File paths mentioned inside the conversation itself are left untouched.

## Install

```bash
mise run install-tool    # uv tool install --editable, so edits to the repo apply immediately
```

## Development

```bash
mise run install     # uv sync
mise run test        # fails under 100% line and branch coverage
mise run check       # ty + ruff
mise run fmt
```

## License

MIT, see [LICENSE](LICENSE).
