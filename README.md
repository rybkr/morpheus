# AI Skills Repository

Reusable AI agent skills stored as directory-based packages (each containing a `SKILL.md`).

## Install

### Bash (macOS/Linux)

Install all skills to Codex user scope:

```bash
./scripts/install-skills.sh --agent codex --all
```

Install one skill to Claude project scope:

```bash
./scripts/install-skills.sh --agent claude --scope repo --skill product-minded-dev
```

Install to a custom agent directory:

```bash
./scripts/install-skills.sh --agent custom --target ~/.my-agent/skills --all
```

### PowerShell (Windows)

```powershell
./scripts/install-skills.ps1 -Agent codex -All
./scripts/install-skills.ps1 -Agent claude -Scope repo -Skill product-minded-dev
./scripts/install-skills.ps1 -Agent custom -Target "$HOME/.my-agent/skills" -All
```

## Supported Defaults

- Codex user scope: `$CODEX_HOME/skills` or `~/.codex/skills`
- Codex repo scope: `.codex/skills`
- Claude user scope: `~/.claude/skills`
- Claude repo scope: `.claude/skills`

For additional TUIs/agents, use `custom` with `--target`/`-Target`.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution, quality, and PR guidelines.
