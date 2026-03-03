from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import NamedTuple


class InstallResult(NamedTuple):
    status: str
    skill: str
    destination: Path
    detail: str


class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"


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


def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _fmt(text: str, color: str) -> str:
    if not _supports_color():
        return text
    return f"{color}{text}{Style.RESET}"


def _heading(text: str) -> str:
    return _fmt(text, Style.BOLD + Style.CYAN)


def _status_label(status: str) -> str:
    labels = {
        "installed": _fmt("INSTALLED", Style.GREEN),
        "planned": _fmt("PLANNED", Style.CYAN),
        "skipped": _fmt("SKIPPED", Style.YELLOW),
        "error": _fmt("ERROR", Style.RED),
    }
    return labels.get(status, status.upper())


def _render_kv(label: str, value: object) -> str:
    return f"{label:<10}: {value}"


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
        print(f"No skills found in {source_dir}", file=sys.stderr)
        return 1

    print(_heading("Available Skills"))
    print(_render_kv("Source", source_dir))
    print(_render_kv("Count", len(skills)))
    print("")
    for i, skill in enumerate(skills, start=1):
        print(f"{i:>2}. {skill}")
    return 0


def _cmd_install(args: argparse.Namespace) -> int:
    repo_root = Path.cwd()
    source_dir = Path(args.source).expanduser() if args.source else _default_source_dir()
    if not source_dir.exists():
        print(f"Source directory does not exist: {source_dir}", file=sys.stderr)
        return 1

    try:
        destination = _resolve_target(args.agent, args.scope, args.target, repo_root)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    skills = list(args.skill or [])
    if args.all:
        skills = _discover_skills(source_dir)

    if not skills:
        print("No skills selected. Pass --all or one or more --skill.", file=sys.stderr)
        return 1

    print(_heading("Install Plan"))
    print(_render_kv("Agent", args.agent))
    print(_render_kv("Scope", args.scope))
    print(_render_kv("Source", source_dir))
    print(_render_kv("Target", destination))
    print(_render_kv("Dry run", args.dry_run))
    print(_render_kv("Skills", ", ".join(skills)))
    print("")

    installed = 0
    planned = 0
    skipped = 0
    errors = 0
    for skill in skills:
        result = _install_skill(
            source_dir=source_dir,
            destination=destination,
            skill=skill,
            dry_run=args.dry_run,
            force=args.force,
        )
        print(f"{_status_label(result.status):<12} {result.skill} -> {result.destination}")
        if result.detail and result.status in {"skipped", "error"}:
            print(f"             {_fmt(result.detail, Style.DIM)}")
        if result.status == "installed":
            installed += 1
        elif result.status == "planned":
            planned += 1
        elif result.status == "skipped":
            skipped += 1
        elif result.status == "error":
            errors += 1

    print("")
    print(_heading("Summary"))
    print(_render_kv("Installed", installed))
    print(_render_kv("Planned", planned))
    print(_render_kv("Skipped", skipped))
    print(_render_kv("Errors", errors))
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
