#!/usr/bin/env python3
# © Siyuan (AI·LAB), CC BY 4.0
"""Create, resume, update, and hand off a business-consult PROGRESS.md file."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import tempfile


STAGES = {
    "diagnose": ["intake", "diagnosis"],
    "research": ["intake", "hypothesis", "plan", "s1", "s2", "s2.5", "s3", "s4", "s5", "s6", "validation"],
    "falsify": ["probe", "preregister", "challenge", "verdict"],
    "report": ["probe", "outline", "draft", "quality-gate"],
    "zh-data": ["request", "collect", "validate", "handoff"],
}


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def progress_path(root: str) -> Path:
    return Path(root).expanduser().resolve() / "PROGRESS.md"


def parse(path: Path) -> tuple[dict[str, str], dict[str, bool], list[str]]:
    if not path.exists():
        raise SystemExit(f"ERROR: missing {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    meta: dict[str, str] = {}
    checks: dict[str, bool] = {}
    notes: list[str] = []
    in_header = False
    in_notes = False
    for line in lines:
        if line == "---":
            in_header = not in_header
            continue
        if in_header and ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
        elif line == "## Notes":
            in_notes = True
        elif line.startswith("- [") and "] " in line:
            checks[line[6:]] = line.startswith("- [x]")
        elif in_notes and line.startswith("- "):
            notes.append(line[2:])
    return meta, checks, notes


def render(meta: dict[str, str], checks: dict[str, bool], notes: list[str]) -> str:
    stages = STAGES[meta["skill"]]
    body = [
        "---",
        f"project: {meta['project']}",
        f"skill: {meta['skill']}",
        f"status: {meta['status']}",
        f"mode: {meta['mode']}",
        f"current_stage: {meta['current_stage']}",
        f"updated_at: {meta['updated_at']}",
        "---",
        "",
        "# Progress",
        "",
    ]
    body.extend(f"- [{'x' if checks.get(stage, False) else ' '}] {stage}" for stage in stages)
    body.extend(["", "## Notes", ""])
    body.extend(f"- {note}" for note in notes)
    return "\n".join(body).rstrip() + "\n"


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def require_owner(meta: dict[str, str], skill: str) -> None:
    if meta.get("skill") != skill:
        raise SystemExit(f"ERROR: progress belongs to {meta.get('skill')!r}, not {skill!r}")


def cmd_init(args: argparse.Namespace) -> None:
    path = progress_path(args.project_root)
    if path.exists():
        raise SystemExit(f"ERROR: refusing to overwrite {path}")
    if args.skill not in STAGES:
        raise SystemExit(f"ERROR: unknown skill {args.skill}")
    stages = STAGES[args.skill]
    meta = {
        "project": args.project,
        "skill": args.skill,
        "status": "in_progress",
        "mode": args.mode,
        "current_stage": stages[0],
        "updated_at": now(),
    }
    atomic_write(path, render(meta, {stage: False for stage in stages}, [f"{now()} initialized"]))
    print(f"initialized {path}")


def cmd_resume(args: argparse.Namespace) -> None:
    path = progress_path(args.project_root)
    meta, checks, _ = parse(path)
    require_owner(meta, args.skill)
    remaining = [stage for stage in STAGES[args.skill] if not checks.get(stage, False)]
    point = remaining[0] if remaining else "completed"
    print(f"skill={args.skill} status={meta.get('status')} resume={point}")


def cmd_mark(args: argparse.Namespace) -> None:
    path = progress_path(args.project_root)
    meta, checks, notes = parse(path)
    require_owner(meta, args.skill)
    if args.stage not in STAGES[args.skill]:
        raise SystemExit(f"ERROR: unknown stage {args.stage}")
    prior = STAGES[args.skill][: STAGES[args.skill].index(args.stage)]
    missing = [stage for stage in prior if not checks.get(stage, False)]
    if missing:
        raise SystemExit(f"ERROR: complete prior stages first: {', '.join(missing)}")
    checks[args.stage] = True
    remaining = [stage for stage in STAGES[args.skill] if not checks.get(stage, False)]
    meta["current_stage"] = remaining[0] if remaining else "completed"
    meta["status"] = "in_progress" if remaining else "completed"
    meta["updated_at"] = now()
    notes.append(f"{now()} completed {args.stage}")
    atomic_write(path, render(meta, checks, notes))
    print(f"marked {args.stage}; resume={meta['current_stage']}")


def cmd_handoff(args: argparse.Namespace) -> None:
    path = progress_path(args.project_root)
    meta, _, notes = parse(path)
    require_owner(meta, args.from_skill)
    if meta.get("status") != "completed":
        raise SystemExit("ERROR: current skill must be completed before handoff")
    if args.to_skill not in STAGES:
        raise SystemExit(f"ERROR: unknown skill {args.to_skill}")
    stages = STAGES[args.to_skill]
    meta.update(
        skill=args.to_skill,
        status="in_progress",
        current_stage=stages[0],
        updated_at=now(),
    )
    notes.append(f"{now()} handoff {args.from_skill} -> {args.to_skill}")
    atomic_write(path, render(meta, {stage: False for stage in stages}, notes))
    print(f"handed off to {args.to_skill}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--project-root", required=True)
    init.add_argument("--project", required=True)
    init.add_argument("--skill", required=True, choices=STAGES)
    init.add_argument("--mode", choices=["live", "knowledge-based"], default="live")
    init.set_defaults(func=cmd_init)
    resume = sub.add_parser("resume")
    resume.add_argument("--project-root", required=True)
    resume.add_argument("--skill", required=True, choices=STAGES)
    resume.set_defaults(func=cmd_resume)
    mark = sub.add_parser("mark")
    mark.add_argument("--project-root", required=True)
    mark.add_argument("--skill", required=True, choices=STAGES)
    mark.add_argument("--stage", required=True)
    mark.set_defaults(func=cmd_mark)
    handoff = sub.add_parser("handoff")
    handoff.add_argument("--project-root", required=True)
    handoff.add_argument("--from-skill", required=True, choices=STAGES)
    handoff.add_argument("--to-skill", required=True, choices=STAGES)
    handoff.set_defaults(func=cmd_handoff)
    return parser


if __name__ == "__main__":
    arguments = build_parser().parse_args()
    arguments.func(arguments)
