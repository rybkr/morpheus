# Contributing

`morpheus-skills` is an open collection of reusable AI agent skills.

## Scope

- Keep skills focused on one capability per folder.
- Follow the Agent Skills structure (`SKILL.md`, optional `scripts/`, `references/`, `assets/`).
- Prefer clear, deterministic instructions over style-heavy prompts.

## Repository Layout

- One top-level directory per skill.
- Each skill directory must include `SKILL.md`.
- Optional helper code should live under that skill's own `scripts/`.
- Installer tooling is provided via the Python package CLI (`morpheus`).

## Skill Quality Bar

- `name` and `description` in frontmatter must be present and accurate.
- Instructions should be executable as-written and avoid hidden assumptions.
- Add concrete examples when behavior might be ambiguous.
- Keep changes minimal and backward compatible unless a breaking change is necessary.

## Local Validation Before PR

1. Confirm every skill folder includes `SKILL.md`.
2. Run CLI installer in dry-run mode: `uv run morpheus install --agent codex --all --dry-run --source .`.
3. Validate install output for both Codex and Claude paths.
4. Re-open changed `SKILL.md` files and verify formatting is intact.

## Pull Request Guidelines

1. Open an issue for large changes first.
2. Keep PRs scoped to one skill or one tooling concern.
3. Include:
   - What changed
   - Why it changed
   - How to test it
4. If behavior changes, include before/after examples.
5. Request at least one reviewer before merge.

## Versioning and Compatibility

- Treat `SKILL.md` behavior changes as user-facing changes.
- Document breaking behavior changes in the PR description.
- Keep CLI behavior backwards compatible when possible.

## Security

- Do not commit secrets, tokens, or private URLs.
- Treat third-party scripts and downloaded assets as untrusted.
- Prefer least-privilege defaults in any automation.

## License and Attribution

- By contributing, you agree your contribution can be distributed under the repository license.
- If you reuse external content, include proper attribution and compatible licensing notes.
