#!/usr/bin/env python3
# © Siyuan (AI·LAB), CC BY 4.0
"""Validate research methodology plans and completed research packages."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES = SKILL_ROOT / "references"
LABELS = {"[Data]", "[Estimate]", "[Assumption]", "[Opinion]"}
FRAMEWORKS = {
    "horizontal-vertical-analysis",
    "user-journey",
    "ai-value-evaluation",
    "product-system-blueprint",
    "questioning-chain",
    "day1-hypothesis",
    "quota-landscape-scan",
    "syntax-cross-validation",
}
STAGES = ["s1", "s2", "s2.5", "s3", "s4", "s5", "s6"]
STAGE_FILES = {
    "s1": "03-s1-foundations.json",
    "s2": "04-s2-business-model.json",
    "s2.5": "05-s2.5-landscape.json",
    "s3": "06-s3-user-pains.json",
    "s4": "07-s4-opportunities.json",
    "s5": "08-s5-product-architecture.json",
}
REQUIRED_PACKAGE = [
    "00-research-brief.md",
    "01-day1-hypothesis.md",
    "02-methodology-plan.json",
    *STAGE_FILES.values(),
    "09-ghost-outline.md",
    "10-research-report.md",
    "11-claim-register.json",
    "12-sources.md",
    "13-open-questions.md",
]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path.name}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.name}: {exc}") from None


def load_schema(path: Path) -> dict[str, Any]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"schema must be an object: {path.name}")
    return data


def resolve_pointer(document: Any, pointer: str) -> Any:
    current = document
    for token in pointer.lstrip("#/").split("/"):
        if not token:
            continue
        token = token.replace("~1", "/").replace("~0", "~")
        current = current[token]
    return current


def resolve_ref(ref: str, root_schema: dict[str, Any], schema_path: Path) -> tuple[dict[str, Any], dict[str, Any], Path]:
    if ref.startswith("#"):
        resolved = resolve_pointer(root_schema, ref)
        return resolved, root_schema, schema_path
    file_name, _, fragment = ref.partition("#")
    external_path = schema_path.parent / file_name
    external_root = load_schema(external_path)
    resolved = resolve_pointer(external_root, f"#{fragment}") if fragment else external_root
    return resolved, external_root, external_path


def validate_schema(
    value: Any,
    schema: dict[str, Any],
    path: str,
    root_schema: dict[str, Any],
    schema_path: Path,
) -> list[str]:
    errors: list[str] = []
    if "$ref" in schema:
        resolved, next_root, next_path = resolve_ref(schema["$ref"], root_schema, schema_path)
        return validate_schema(value, resolved, path, next_root, next_path)

    expected = schema.get("type")
    type_ok = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }.get(expected, True)
    if not type_ok:
        return [f"{path}: expected {expected}"]

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} not in enum")
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        errors.append(f"{path}: string is too short")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: value below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: value above maximum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: too few items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                errors.extend(validate_schema(item, item_schema, f"{path}[{index}]", root_schema, schema_path))
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required key {key}")
        for key, child_schema in schema.get("properties", {}).items():
            if key in value:
                errors.extend(
                    validate_schema(value[key], child_schema, f"{path}.{key}", root_schema, schema_path)
                )
    return errors


def schema_errors(data: Any, schema_name: str) -> list[str]:
    schema_path = REFERENCES / schema_name
    schema = load_schema(schema_path)
    return validate_schema(data, schema, "$", schema, schema_path)


def validate_plan(research_dir: Path) -> list[str]:
    errors: list[str] = []
    plan = load_json(research_dir / "02-methodology-plan.json")
    errors.extend(schema_errors(plan, "methodology-plan.schema.json"))
    if not isinstance(plan, dict):
        return errors
    missing_frameworks = FRAMEWORKS - set(plan.get("frameworks", []))
    if missing_frameworks:
        errors.append(f"plan missing frameworks: {', '.join(sorted(missing_frameworks))}")
    if plan.get("stages") != STAGES:
        errors.append(f"plan stages must be exactly: {', '.join(STAGES)}")
    if set(plan.get("gates", {}).get("claim_labels", [])) != LABELS:
        errors.append("plan claim_labels must contain all four honesty labels")
    return errors


def source_ids(path: Path) -> set[str]:
    found: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            for cell in cells[:2]:
                if re.fullmatch(r"S\d{3}", cell):
                    found.add(cell)
                    break
            continue
        match = re.match(r"^(?:[-*]\s*)?(S\d{3})(?=\s*(?::|\|))", stripped)
        if match:
            found.add(match.group(1))
    return found


def strip_frontmatter(lines: list[str]) -> list[str]:
    if not lines or lines[0] != "---":
        return lines
    for index in range(1, len(lines)):
        if lines[index] == "---":
            return lines[index + 1 :]
    return lines


def is_table_separator(line: str) -> bool:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return False
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def validate_tagged_markdown(path: Path) -> list[str]:
    errors: list[str] = []
    lines = strip_frontmatter(path.read_text(encoding="utf-8").splitlines())
    in_code = False
    for index, raw in enumerate(lines):
        number = index + 1
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line or line.startswith("#") or line == "---":
            continue
        if is_table_separator(line):
            continue
        if (
            line.startswith("|")
            and index + 1 < len(lines)
            and is_table_separator(lines[index + 1])
        ):
            continue
        if any(
            line.startswith(prefix + label)
            for label in LABELS
            for prefix in ("- ", "* ", "> ", "")
        ):
            continue
        if any(line.startswith(f"| {label} |") for label in LABELS):
            continue
        errors.append(f"{path.name}:{number}: untagged substantive line: {line[:80]}")
    return errors


def validate_quota(stage: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    artifacts = stage.get("artifacts", {})
    plan = artifacts.get("quota_plan", {})
    candidates = artifacts.get("candidates", [])
    required = {"direct", "substitutes", "ecosystem", "benchmarks"}
    if set(plan) != required:
        errors.append("s2.5 quota_plan must contain direct, substitutes, ecosystem, benchmarks")
        return errors
    counts = Counter(item.get("category") for item in candidates if isinstance(item, dict))
    for category in sorted(required):
        entry = plan.get(category, {})
        target = entry.get("target")
        if not isinstance(target, int) or target < 1:
            errors.append(f"s2.5 {category} target must be a positive integer")
            continue
        if counts[category] < target and not entry.get("gap"):
            errors.append(f"s2.5 {category} is under quota without an externalized gap")
    return errors


def build_validation_report(
    output: Path,
    critical: list[str],
    warnings: list[str],
    checks: list[str],
) -> None:
    status = "failed" if critical else "passed"
    lines = [
        "---",
        f"status: {status}",
        f"date: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "validation_type: qualitative",
        "---",
        "",
        "# Research validation report",
        "",
        "## Summary",
        "",
        f"- [Data] Validation status: {status}.",
        f"- [Data] Critical findings: {len(critical)}.",
        f"- [Data] Warnings: {len(warnings)}.",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- [Data] {item}" for item in checks)
    lines.extend(["", "## Critical", ""])
    lines.extend(f"- [Data] {item}" for item in critical or ["No critical findings."])
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- [Data] {item}" for item in warnings or ["No warnings."])
    lines.extend(["", "## Open Questions", ""])
    lines.append("- [Opinion] See `13-open-questions.md`; unresolved evidence gaps remain explicit.")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_package(research_dir: Path) -> tuple[list[str], list[str], list[str]]:
    critical: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []

    missing = [name for name in REQUIRED_PACKAGE if not (research_dir / name).exists()]
    if missing:
        critical.append(f"missing required files: {', '.join(missing)}")
        return critical, warnings, checks
    checks.append(f"Fixed output contract present: {len(REQUIRED_PACKAGE)} pre-validation files.")

    plan_errors: list[str] = []
    try:
        plan_errors = validate_plan(research_dir)
        critical.extend(plan_errors)
    except ValueError as exc:
        critical.append(str(exc))
    checks.append("Methodology plan passed schema and required-framework checks." if not plan_errors else "Methodology plan checked.")

    known_sources = source_ids(research_dir / "12-sources.md")
    if not known_sources:
        critical.append("12-sources.md contains no parseable source rows")
    checks.append(f"Source register parsed: {len(known_sources)} source IDs.")

    all_claims: list[dict[str, Any]] = []
    stage_ids: list[str] = []
    for expected_stage, file_name in STAGE_FILES.items():
        try:
            stage = load_json(research_dir / file_name)
            stage_errors = schema_errors(stage, "stage.schema.json")
            critical.extend(f"{file_name}: {error}" for error in stage_errors)
            if isinstance(stage, dict):
                if stage.get("stage") != expected_stage:
                    critical.append(f"{file_name}: stage must be {expected_stage}")
                if expected_stage == "s2.5":
                    critical.extend(validate_quota(stage))
                for claim in stage.get("claims", []):
                    if not isinstance(claim, dict):
                        continue
                    all_claims.append(claim)
                    stage_ids.append(claim.get("id", ""))
                    label = claim.get("label")
                    sources = claim.get("source_ids", [])
                    if label == "[Data]" and not sources:
                        critical.append(f"{claim.get('id')}: [Data] claim has no source IDs")
                    if label in {"[Estimate]", "[Assumption]"} and not claim.get("reasoning"):
                        critical.append(f"{claim.get('id')}: {label} claim has no reasoning")
                    for source_id in sources:
                        if source_id not in known_sources:
                            critical.append(f"{claim.get('id')}: unknown source ID {source_id}")
        except ValueError as exc:
            critical.append(str(exc))
    duplicates = [claim_id for claim_id, count in Counter(stage_ids).items() if claim_id and count > 1]
    if duplicates:
        critical.append(f"duplicate stage claim IDs: {', '.join(sorted(duplicates))}")
    checks.append(f"Stage schemas and claim labels checked: {len(all_claims)} claims.")

    try:
        register = load_json(research_dir / "11-claim-register.json")
        critical.extend(schema_errors(register, "claim-register.schema.json"))
        register_claims = register.get("claims", []) if isinstance(register, dict) else []
        register_ids = [claim.get("id") for claim in register_claims if isinstance(claim, dict)]
        if Counter(register_ids) != Counter(stage_ids):
            critical.append("claim register IDs do not exactly match stage claim IDs")
    except ValueError as exc:
        critical.append(str(exc))
    checks.append("Claim register reconciled against stage files.")

    for markdown_name in ("10-research-report.md", "13-open-questions.md"):
        critical.extend(validate_tagged_markdown(research_dir / markdown_name))
    checks.append("Report and Open Questions passed claim-tag coverage checks.")

    if any(claim.get("confidence") == "low" for claim in all_claims):
        warnings.append("Low-confidence claims remain; review them before final report use.")
    return critical, warnings, checks


def validate_stage_file(stage_file: Path) -> list[str]:
    try:
        stage = load_json(stage_file)
    except ValueError as exc:
        return [str(exc)]
    return schema_errors(stage, "stage.schema.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "package"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("project_root")
    stage_parser = subparsers.add_parser("stage")
    stage_parser.add_argument("stage_file")
    args = parser.parse_args()

    if args.command == "stage":
        errors = validate_stage_file(Path(args.stage_file).expanduser().resolve())
        if errors:
            print("STAGE CHECK FAILED")
            for error in errors:
                print(f"- {error}")
            return 1
        print("STAGE CHECK PASSED")
        return 0

    research_dir = Path(args.project_root).expanduser().resolve() / "research"

    if args.command == "plan":
        try:
            errors = validate_plan(research_dir)
        except ValueError as exc:
            errors = [str(exc)]
        if errors:
            print("STOP CHECK FAILED")
            for error in errors:
                print(f"- {error}")
            return 1
        print("STOP CHECK PASSED")
        return 0

    critical, warnings, checks = validate_package(research_dir)
    research_dir.mkdir(parents=True, exist_ok=True)
    build_validation_report(research_dir / "14-validation-report.md", critical, warnings, checks)
    print(f"package validation: critical={len(critical)} warnings={len(warnings)}")
    return 1 if critical else 0


if __name__ == "__main__":
    sys.exit(main())
