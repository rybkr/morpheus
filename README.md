# morpheus-skills

Reusable AI agent skills stored as directory-based packages (each containing a `SKILL.md`).

## Recommended Package Manager

Use `uv` for package management and distribution.

- It is cross-platform (macOS/Linux/Windows), unlike Homebrew.
- It supports both project-local and global CLI installs.
- It works well for Python-based installer tooling and CI automation.

Use Homebrew only as an optional distribution channel for macOS users after the Python package is stable.

Repository/package branding: `morpheus-skills`  
Installer CLI command: `morpheus`

## Install (No Clone Required)

### With `uv` (recommended)

Install directly from PyPI:

```bash
uv tool install morpheus-skills
morpheus list
morpheus install --agent codex --all
```

### With `pipx`

```bash
pipx install morpheus-skills
morpheus install --agent codex --all
```

### With `pip`

```bash
python -m pip install --user morpheus-skills
morpheus install --agent codex --all
```

## Install From Local Repo (Optional for Development)

If you are developing this project locally, install from the checkout:

```bash
uv tool install .
```

You can also run without installing:

```bash
uv run morpheus list
uv run morpheus install --agent claude --all --dry-run
```

### Use Repo Skills Instead of Bundled Package Skills

The packaged CLI ships with bundled skills. To install directly from a local checkout, pass `--source`:

```bash
morpheus install --agent codex --all --source .
```

## CLI Usage

Install all bundled skills to Codex user scope:

```bash
morpheus install --agent codex --all
```

Install one skill to Claude project scope:

```bash
morpheus install --agent claude --scope repo --skill product-dev
```

Install to a custom agent directory:

```bash
morpheus install --agent custom --target ~/.my-agent/skills --all
```

## Supported Defaults

- Codex user scope: `$CODEX_HOME/skills` or `~/.codex/skills`
- Codex repo scope: `.codex/skills`
- Claude user scope: `~/.claude/skills`
- Claude repo scope: `.claude/skills`

For additional TUIs/agents, use `custom` with `--target`/`-Target`.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution, quality, and PR guidelines.

## Release to PyPI (GitHub Actions)

This repository includes `.github/workflows/publish.yml`.

1. Bump version in `pyproject.toml` and `morpheus/__init__.py`.
2. Commit and push to `main`.
3. Create and push a version tag (for example `v0.1.1`).

```bash
git tag v0.1.1
git push origin v0.1.1
```

The workflow builds `dist/*` and publishes to PyPI using trusted publishing.

One-time PyPI setup:

- In PyPI project settings for `morpheus-skills`, add a trusted publisher:
- Owner: your GitHub user/org
- Repository: `rybkr/morpheus`
- Workflow name: `publish.yml`
- Environment: `pypi`
