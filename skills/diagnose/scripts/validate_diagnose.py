#!/usr/bin/env python3
# © Siyuan (AI·LAB), CC BY 4.0
"""Validate the public diagnose interaction shell and research handoff."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any


SESSION_KEYS = (
    "schema_version",
    "project",
    "status",
    "current_step",
    "updated_at",
    "raw_question",
    "interactions",
    "pending_question",
    "awaiting_user",
    "handoff",
)
INTERACTION_KEYS = ("turn", "judgment", "question", "response")
HANDOFF_KEYS = ("decision", "scope", "exclusions", "research_question", "evidence_needs")
FRONTMATTER_KEYS = ("schema_version", "project", "status", "current_step")
COMPLETED_HEADINGS = (
    "Decision",
    "Scope",
    "Exclusions",
    "Research question",
    "Evidence needs",
    "Completion reason",
)
IN_PROGRESS_HEADINGS = ("Current judgment", "Pending question")
SPEC_START = "<!-- DIAGNOSE:SHELL-HANDOFF:START -->"
SPEC_END = "<!-- DIAGNOSE:SHELL-HANDOFF:END -->"


@dataclass
class Findings:
    critical: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)

    def extend(self, other: "Findings") -> None:
        self.critical.extend(other.critical)
        self.warnings.extend(other.warnings)
        self.checks.extend(other.checks)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def key_order(value: Any, expected: tuple[str, ...], where: str, findings: Findings) -> bool:
    if not isinstance(value, dict):
        findings.critical.append(f"{where} must be an object")
        return False
    if tuple(value.keys()) != expected:
        findings.critical.append(f"{where} keys must use canonical order")
        return False
    return True


def sorted_strings(value: Any, where: str, findings: Findings) -> list[str]:
    if not isinstance(value, list) or not value or any(not nonempty(item) for item in value):
        findings.critical.append(f"{where} must be a non-empty string array")
        return []
    if value != sorted(set(value)):
        findings.critical.append(f"{where} must be unique and sorted")
    return value


def load_session(path: Path) -> tuple[Findings, dict[str, Any]]:
    findings = Findings()
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except FileNotFoundError:
        findings.critical.append(f"missing session: {path}")
        return findings, {}
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        findings.critical.append(f"invalid session: {exc}")
        return findings, {}
    if not key_order(data, SESSION_KEYS, "session", findings):
        return findings, data if isinstance(data, dict) else {}
    if text != json.dumps(data, ensure_ascii=False, indent=2) + "\n":
        findings.critical.append("session must use canonical two-space JSON formatting")
    if data.get("schema_version") != "1.0":
        findings.critical.append("session schema_version must be 1.0")
    for key in ("project", "raw_question"):
        if not nonempty(data.get(key)):
            findings.critical.append(f"session {key} is required")
    try:
        datetime.fromisoformat(str(data.get("updated_at", "")).replace("Z", "+00:00"))
    except ValueError:
        findings.critical.append("session updated_at must be ISO-8601")
    validate_interactions(data, findings)
    return findings, data


def validate_interactions(data: dict[str, Any], findings: Findings) -> None:
    interactions = data.get("interactions")
    if not isinstance(interactions, list) or not interactions:
        findings.critical.append("session requires at least one interaction")
        return
    questions: list[str] = []
    for index, item in enumerate(interactions):
        where = f"interactions[{index}]"
        if not key_order(item, INTERACTION_KEYS, where, findings):
            continue
        if item.get("turn") != index + 1:
            findings.critical.append(f"{where}: turn must be consecutive")
        if not nonempty(item.get("judgment")):
            findings.critical.append(f"{where}: judgment is required")
        question = item.get("question")
        if not nonempty(question):
            findings.critical.append(f"{where}: question is required")
        elif question.count("?") + question.count("？") != 1:
            findings.critical.append(f"{where}: exactly one question is allowed")
        else:
            questions.append(question)
        response = item.get("response")
        if response is not None and not nonempty(response):
            findings.critical.append(f"{where}: response must be null or non-empty")
    if len(questions) != len(set(questions)):
        findings.critical.append("resume repeated a prior question")
    if data.get("current_step") != len(interactions):
        findings.critical.append("current_step must equal the interaction count")

    status = data.get("status")
    responses = [item.get("response") for item in interactions if isinstance(item, dict)]
    if status == "in_progress":
        if any(response is None for response in responses[:-1]):
            findings.critical.append("session advanced without a recorded reply")
        if responses[-1] is not None:
            findings.critical.append("in-progress final interaction must await a reply")
        if data.get("pending_question") != interactions[-1].get("question"):
            findings.critical.append("pending_question must equal the final question")
        if data.get("awaiting_user") is not True:
            findings.critical.append("in-progress session must await the user")
        if data.get("handoff") is not None:
            findings.critical.append("in-progress session cannot contain a handoff")
    elif status == "completed":
        if any(response is None for response in responses):
            findings.critical.append("completed session requires a reply for every interaction")
        if data.get("pending_question") is not None or data.get("awaiting_user") is not False:
            findings.critical.append("completed session cannot await the user")
        validate_handoff(data.get("handoff"), findings)
    else:
        findings.critical.append("session status must be in_progress or completed")
    findings.checks.append(f"interaction protocol checked: {len(interactions)} turns")


def validate_handoff(value: Any, findings: Findings) -> None:
    if not key_order(value, HANDOFF_KEYS, "handoff", findings):
        return
    for key in ("decision", "scope", "research_question"):
        if not nonempty(value.get(key)):
            findings.critical.append(f"handoff {key} is required")
    sorted_strings(value.get("exclusions"), "handoff exclusions", findings)
    sorted_strings(value.get("evidence_needs"), "handoff evidence_needs", findings)


def parse_diagnosis(path: Path) -> tuple[Findings, dict[str, str], dict[str, str], str]:
    findings = Findings()
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        findings.critical.append(f"missing diagnosis: {path}")
        return findings, {}, {}, ""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        findings.critical.append("diagnosis must start with frontmatter")
        return findings, {}, {}, text
    try:
        end = lines.index("---", 1)
    except ValueError:
        findings.critical.append("diagnosis frontmatter is not closed")
        return findings, {}, {}, text
    frontmatter: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            findings.critical.append(f"invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"')
    if tuple(frontmatter.keys()) != FRONTMATTER_KEYS:
        findings.critical.append("diagnosis frontmatter keys must use canonical order")
    headings: list[str] = []
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines[end + 1 :]:
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            current = match.group(1)
            headings.append(current)
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    normalized = {key: "\n".join(value).strip() for key, value in sections.items()}
    expected = COMPLETED_HEADINGS if frontmatter.get("status") == "completed" else IN_PROGRESS_HEADINGS
    if tuple(headings) != expected:
        findings.critical.append(f"diagnosis headings must be: {', '.join(expected)}")
    for heading in expected:
        if not normalized.get(heading):
            findings.critical.append(f"diagnosis section is empty: {heading}")
    return findings, frontmatter, normalized, text


def extract_handoff(text: str, findings: Findings) -> dict[str, Any]:
    pattern = re.compile(
        re.escape(SPEC_START) + r"\s*```json\s*(\{.*?\})\s*```\s*" + re.escape(SPEC_END),
        re.DOTALL,
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        findings.critical.append("completed diagnosis requires one handoff JSON block")
        return {}
    try:
        value = json.loads(matches[0])
    except json.JSONDecodeError as exc:
        findings.critical.append(f"invalid handoff JSON: {exc}")
        return {}
    validate_handoff(value, findings)
    return value


def validate_project(root: Path) -> tuple[Findings, dict[str, Any]]:
    root = root.expanduser().resolve()
    findings = Findings()
    runtime = root / "diagnose"
    if runtime.is_dir():
        for item in runtime.iterdir():
            if item.name != "session.json" or not item.is_file() or item.is_symlink():
                findings.critical.append(f"forbidden diagnose runtime output: {item.name}")
    session_findings, session = load_session(runtime / "session.json")
    diagnosis_findings, frontmatter, sections, text = parse_diagnosis(root / "diagnosis.md")
    findings.extend(session_findings)
    findings.extend(diagnosis_findings)
    for key in ("schema_version", "project", "status", "current_step"):
        if frontmatter.get(key) != str(session.get(key, "")):
            findings.critical.append(f"session and diagnosis disagree on {key}")
    if session.get("status") == "in_progress":
        if session.get("pending_question") not in sections.get("Pending question", ""):
            findings.critical.append("diagnosis pending question does not match session")
    elif session.get("status") == "completed":
        handoff = extract_handoff(text, findings)
        if handoff != session.get("handoff"):
            findings.critical.append("session and diagnosis handoff disagree")
    findings.checks.append("fixed output pair checked")
    return findings, session


def print_findings(label: str, findings: Findings) -> int:
    print(f"{label}: critical={len(findings.critical)} warnings={len(findings.warnings)}")
    for item in findings.critical:
        print(f"CRITICAL: {item}")
    for item in findings.warnings:
        print(f"WARNING: {item}")
    for item in findings.checks:
        print(f"CHECK: {item}")
    return 1 if findings.critical else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate", "completed", "research-probe"))
    parser.add_argument("project_root", type=Path)
    args = parser.parse_args()
    findings, session = validate_project(args.project_root)
    if args.command in {"completed", "research-probe"} and session.get("status") != "completed":
        findings.critical.append("research handoff rejected: diagnosis is not completed")
    if findings.critical:
        return print_findings("diagnose shell", findings)
    if args.command == "research-probe":
        print(json.dumps({
            "handoff": "accepted",
            "skip_duplicate_intake": True,
            "project": session["project"],
            "research_specification": session["handoff"],
        }, ensure_ascii=False, indent=2))
        return 0
    return print_findings("diagnose shell", findings)


if __name__ == "__main__":
    sys.exit(main())
