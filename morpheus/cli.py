from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import NamedTuple

from rich.console import Console
from rich.table import Table
from rich.text import Text


class InstallResult(NamedTuple):
    status: str
    skill: str
    destination: Path
    detail: str


class Style:
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    CYAN = "cyan"
    DIM = "dim"


CONSOLE = Console()
ERR_CONSOLE = Console(stderr=True)


def _default_source_dir() -> Path:
    return Path(__file__).resolve().parent / "bundled_skills"


def _discover_skills(source_dir: Path) -> list[str]:
    if not source_dir.exists():
        return []

    skills: list[str] = []
    for entry in sorted(source_dir.iterdir(), key=lambda p: p.name):
        if entry.is_dir() and (entry / "SKILL.md").is_file():
            skills.append(entry.name)
    return skills


def _resolve_target(agent: str, scope: str, target: str | None, repo_root: Path) -> Path:
    if target:
        return Path(target).expanduser()

    if agent == "codex":
        if scope == "repo":
            return repo_root / ".codex" / "skills"
        codex_home = os.environ.get("CODEX_HOME")
        if codex_home:
            return Path(codex_home).expanduser() / "skills"
        return Path.home() / ".codex" / "skills"

    if agent == "claude":
        if scope == "repo":
            return repo_root / ".claude" / "skills"
        return Path.home() / ".claude" / "skills"

    if agent == "custom":
        raise ValueError("custom agent requires --target")

    raise ValueError(f"Unsupported agent '{agent}'")


def _status_label(status: str) -> Text:
    labels = {
        "installed": Text("INSTALLED", style=Style.GREEN),
        "planned": Text("PLANNED", style=Style.CYAN),
        "skipped": Text("SKIPPED", style=Style.YELLOW),
        "error": Text("ERROR", style=Style.RED),
    }
    return labels.get(status, Text(status.upper()))


def _render_kv_table(title: str, rows: list[tuple[str, object]]) -> Table:
    table = Table(title=title, title_style="bold cyan", show_header=False, box=None)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for label, value in rows:
        table.add_row(label, str(value))
    return table


def _install_skill(
    *,
    source_dir: Path,
    destination: Path,
    skill: str,
    dry_run: bool,
    force: bool,
) -> InstallResult:
    src = source_dir / skill
    dst = destination / skill

    if not (src / "SKILL.md").is_file():
        return InstallResult("error", skill, dst, f"missing {src / 'SKILL.md'}")

    if dst.exists() and not force:
        return InstallResult("skipped", skill, dst, "destination exists (use --force to overwrite)")

    if dry_run:
        return InstallResult("planned", skill, dst, "dry run")

    destination.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return InstallResult("installed", skill, dst, "")


def _cmd_list(args: argparse.Namespace) -> int:
    source_dir = Path(args.source).expanduser() if args.source else _default_source_dir()
    skills = _discover_skills(source_dir)
    if not skills:
        ERR_CONSOLE.print(f"No skills found in {source_dir}", style="red")
        return 1

    CONSOLE.print(
        _render_kv_table(
            "Available Skills",
            [("Source", source_dir), ("Count", len(skills))],
        )
    )
    skill_table = Table(box=None, show_header=False)
    skill_table.add_column("Index", justify="right", style="dim")
    skill_table.add_column("Skill")
    for i, skill in enumerate(skills, start=1):
        skill_table.add_row(str(i), skill)
    CONSOLE.print(skill_table)
    return 0


def _cmd_install(args: argparse.Namespace) -> int:
    repo_root = Path.cwd()
    source_dir = Path(args.source).expanduser() if args.source else _default_source_dir()
    if not source_dir.exists():
        ERR_CONSOLE.print(f"Source directory does not exist: {source_dir}", style="red")
        return 1

    try:
        destination = _resolve_target(args.agent, args.scope, args.target, repo_root)
    except ValueError as exc:
        ERR_CONSOLE.print(str(exc), style="red")
        return 1

    skills = list(args.skill or [])
    if args.all:
        skills = _discover_skills(source_dir)

    if not skills:
        ERR_CONSOLE.print("No skills selected. Pass --all or one or more --skill.", style="red")
        return 1

    CONSOLE.print(
        _render_kv_table(
            "Install Plan",
            [
                ("Agent", args.agent),
                ("Scope", args.scope),
                ("Source", source_dir),
                ("Target", destination),
                ("Dry run", args.dry_run),
                ("Skills", ", ".join(skills)),
            ],
        )
    )

    installed = 0
    planned = 0
    skipped = 0
    errors = 0
    result_table = Table(title="Actions", title_style="bold cyan")
    result_table.add_column("Status", no_wrap=True)
    result_table.add_column("Skill", no_wrap=True)
    result_table.add_column("Destination")
    result_table.add_column("Detail")

    for skill in skills:
        result = _install_skill(
            source_dir=source_dir,
            destination=destination,
            skill=skill,
            dry_run=args.dry_run,
            force=args.force,
        )
        detail = result.detail if result.detail else ""
        detail_style = Style.DIM if result.status in {"skipped", "error"} else ""
        result_table.add_row(
            _status_label(result.status),
            result.skill,
            str(result.destination),
            Text(detail, style=detail_style),
        )
        if result.status == "installed":
            installed += 1
        elif result.status == "planned":
            planned += 1
        elif result.status == "skipped":
            skipped += 1
        elif result.status == "error":
            errors += 1

    CONSOLE.print(result_table)
    CONSOLE.print(
        _render_kv_table(
            "Summary",
            [
                ("Installed", installed),
                ("Planned", planned),
                ("Skipped", skipped),
                ("Errors", errors),
            ],
        )
    )
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="morpheus",
        description="Install skills for Codex, Claude, and compatible agent TUIs.",
        epilog=(
            "Examples:\n"
            "  morpheus list\n"
            "  morpheus install --agent codex --all\n"
            "  morpheus install --agent claude --scope repo --skill product-minded-dev --dry-run"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List available skills from a source directory.")
    list_parser.add_argument(
        "--source",
        help="Directory containing skill folders. Defaults to bundled skills in this package.",
    )
    list_parser.set_defaults(func=_cmd_list)

    install_parser = subparsers.add_parser("install", help="Install skills to a target agent directory.")
    install_parser.add_argument("--agent", choices=["codex", "claude", "custom"], required=True)
    install_parser.add_argument("--scope", choices=["user", "repo"], default="user")
    install_parser.add_argument(
        "--skill",
        action="append",
        help="Skill directory name to install. Repeatable.",
    )
    install_parser.add_argument("--all", action="store_true", help="Install all discovered skills.")
    install_parser.add_argument("--target", help="Override destination skills directory.")
    install_parser.add_argument(
        "--source",
        help="Directory containing skill folders. Defaults to bundled skills in this package.",
    )
    install_parser.add_argument("--force", action="store_true", help="Overwrite existing skill directories.")
    install_parser.add_argument("--dry-run", action="store_true", help="Print actions without copying files.")
    install_parser.set_defaults(func=_cmd_install)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
