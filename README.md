# morpheus-skills

Install and manage reusable AI agent `SKILL.md` packages for Codex, Claude, and compatible tools.

Package name: `morpheus-skills`  
CLI command: `morpheus`

## Install

Recommended: `uv`

```bash
uv tool install morpheus-skills
morpheus list
morpheus install --agent codex --all
```

Alternatives:

```bash
pipx install morpheus-skills
# or
python3 -m pip install --user morpheus-skills
```

## Usage

```bash
# list bundled skills
morpheus list

# install all bundled skills for Codex user scope
morpheus install --agent codex --all

# install one skill for Claude repo scope
morpheus install --agent claude --scope repo --skill product-minded-dev

# preview actions without copying
morpheus install --agent codex --all --dry-run
```

Install from a local checkout (development):

```bash
uv tool install .
# or run without installing
uv run morpheus list
```

Use repo skills instead of bundled package skills:

```bash
morpheus install --agent codex --all --source .
```

## Default Targets

- Codex user: `$CODEX_HOME/skills` or `~/.codex/skills`
- Codex repo: `.codex/skills`
- Claude user: `~/.claude/skills`
- Claude repo: `.claude/skills`

For other agents, use `--agent custom --target <path>`.

## Release (PyPI)

Tag pushes (`v*`) trigger `.github/workflows/publish.yml` to build and publish to PyPI.

```bash
git tag v0.1.3
git push origin v0.1.3
```

Trusted publishing must match:

- Project: `morpheus-skills`
- Owner: your GitHub user/org
- Repository: `rybkr/morpheus`
- Workflow: `publish.yml`
- Environment: `pypi`

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
