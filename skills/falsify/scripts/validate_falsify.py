#!/usr/bin/env python3
# © Siyuan (AI·LAB), CC BY 4.0
"""Validate immutable falsify inputs, preregistration, attempts, and verdict outputs."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlsplit


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES = SKILL_ROOT / "references"
PROTECTED_PATHS = (
    "research/03-s1-foundations.json",
    "research/04-s2-business-model.json",
    "research/05-s2.5-landscape.json",
    "research/06-s3-user-pains.json",
    "research/07-s4-opportunities.json",
    "research/08-s5-product-architecture.json",
    "research/10-research-report.md",
    "research/11-claim-register.json",
    "research/12-sources.md",
    "research/13-open-questions.md",
    "research/14-validation-report.md",
)
HANDOFF_PATHS = PROTECTED_PATHS[6:]
BOUNDARY_SENTENCE = "本次“未推翻”只代表在已声明范围内未找到足够反证，不代表该结论为真。"
STATUSES = {"falsified", "survived", "unresolved"}
CREDIBLE_KINDS = {"primary", "authoritative-secondary"}
SEARCH_HOSTS = {"google.com", "www.google.com", "www.google.com.hk", "bing.com", "www.bing.com"}
TRUE_RE = re.compile(
    r"已证明(?:为)?真|证明[^。；\n]{0,20}为真|事实为真|结论为真|"
    r"\b(?:is|was)\s+true\b|\b(?:verified|proven|confirmed)\s+true\b",
    re.IGNORECASE,
)


@dataclass
class Findings:
    critical: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)

    def extend(self, other: "Findings") -> None:
        self.critical.extend(other.critical)
        self.warnings.extend(other.warnings)
        self.checks.extend(other.checks)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path}") from None
    except UnicodeDecodeError as exc:
        raise ValueError(f"file is not UTF-8: {path}: {exc}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from None


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def claim_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def valid_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def parse_time(value: Any, where: str, findings: Findings) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        findings.critical.append(f"{where}: timestamp is required")
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        findings.critical.append(f"{where}: invalid ISO-8601 timestamp")
        return None


def schema_errors(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    type_map = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
    }
    if expected in type_map and not type_map[expected](value):
        return [f"{path}: expected {expected}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: invalid enum value {value!r}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is too short")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: does not match required pattern")
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: value below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: value above maximum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: too few items")
        child = schema.get("items")
        if isinstance(child, dict):
            for index, item in enumerate(value):
                errors.extend(schema_errors(item, child, f"{path}[{index}]"))
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required key {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}: unexpected key {key}")
        for key, child in properties.items():
            if key in value:
                errors.extend(schema_errors(value[key], child, f"{path}.{key}"))
    return errors


def validate_structure(data: Any, schema_name: str, findings: Findings) -> None:
    try:
        schema = read_json(REFERENCES / schema_name)
    except ValueError as exc:
        findings.critical.append(str(exc))
        return
    findings.critical.extend(f"{schema_name}: {item}" for item in schema_errors(data, schema))


def load_claim_register(root: Path, findings: Findings) -> tuple[str, dict[str, dict[str, Any]]]:
    path = root / "research/11-claim-register.json"
    try:
        data = read_json(path)
    except ValueError as exc:
        findings.critical.append(str(exc))
        return "", {}
    if not isinstance(data, dict):
        findings.critical.append("claim register root must be an object")
        return "", {}
    project = data.get("project")
    if not isinstance(project, str) or not project:
        findings.critical.append("claim register project is required")
        project = ""
    entries = data.get("claims")
    if not isinstance(entries, list) or not entries:
        findings.critical.append("claim register claims must be a non-empty array")
        return project, {}
    claims: dict[str, dict[str, Any]] = {}
    for index, claim in enumerate(entries):
        if not isinstance(claim, dict):
            findings.critical.append(f"claim register[{index}] must be an object")
            continue
        claim_id, text = claim.get("id"), claim.get("claim")
        if not isinstance(claim_id, str) or not claim_id:
            findings.critical.append(f"claim register[{index}] missing claim ID")
            continue
        if not isinstance(text, str) or not text:
            findings.critical.append(f"claim {claim_id} missing exact text")
        if claim_id in claims:
            findings.critical.append(f"duplicate research claim ID: {claim_id}")
        claims[claim_id] = claim
    return project, claims


def probe_inputs(root: Path) -> tuple[Findings, str, dict[str, dict[str, Any]]]:
    findings = Findings()
    missing_handoff = [path for path in HANDOFF_PATHS if not (root / path).is_file()]
    missing_protected = [path for path in PROTECTED_PATHS if not (root / path).is_file()]
    if missing_handoff:
        findings.critical.append(f"missing research handoff files: {', '.join(missing_handoff)}")
    if missing_protected:
        findings.critical.append(f"missing protected research files: {', '.join(missing_protected)}")
    project, claims = load_claim_register(root, findings)
    validation_path = root / "research/14-validation-report.md"
    if validation_path.is_file():
        text = validation_path.read_text(encoding="utf-8")
        explicit_critical = re.search(r"Critical findings:\s*([0-9]+)\b", text, re.IGNORECASE)
        if explicit_critical and int(explicit_critical.group(1)) != 0:
            findings.critical.append("research/14-validation-report.md reports Critical findings")
        if re.search(r"^status:\s*failed\s*$", text, re.IGNORECASE | re.MULTILINE):
            findings.critical.append("research/14-validation-report.md reports failed status")
    findings.checks.append(f"research handoff checked: {len(HANDOFF_PATHS) - len(missing_handoff)} files")
    findings.checks.append(f"protected input set checked: {len(PROTECTED_PATHS) - len(missing_protected)} files")
    findings.checks.append(f"claim register parsed: {len(claims)} claims")
    return findings, project, claims


def validate_preregistration(root: Path) -> tuple[Findings, dict[str, Any], dict[str, dict[str, Any]]]:
    findings, project, research_claims = probe_inputs(root)
    path = root / "falsify/00-preregistration.json"
    try:
        prereg = read_json(path)
    except ValueError as exc:
        findings.critical.append(str(exc))
        return findings, {}, research_claims
    validate_structure(prereg, "00-preregistration.schema.json", findings)
    if not isinstance(prereg, dict):
        return findings, {}, research_claims
    if prereg.get("project") != project:
        findings.critical.append("preregistration project does not match claim register")
    parse_time(prereg.get("generated_at"), "preregistration.generated_at", findings)

    manifest = prereg.get("input_manifest", [])
    manifest_paths = [entry.get("path") for entry in manifest if isinstance(entry, dict)]
    if manifest_paths != sorted(manifest_paths):
        findings.critical.append("input manifest must be sorted by path")
    if tuple(manifest_paths) != PROTECTED_PATHS:
        findings.critical.append("input manifest paths must exactly match the protected input set")
    for entry in manifest:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        input_path = root / entry["path"]
        if input_path.is_file() and entry.get("sha256") != sha256_bytes(input_path):
            findings.critical.append(f"protected input hash changed: {entry['path']}")

    selected: dict[str, dict[str, Any]] = {}
    entries = prereg.get("claims", [])
    ids = [entry.get("claim_id") for entry in entries if isinstance(entry, dict)]
    if ids != sorted(ids):
        findings.critical.append("preregistered claims must be sorted by claim_id")
    if len(ids) != len(set(ids)):
        findings.critical.append("duplicate preregistered claim ID")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        claim_id = entry.get("claim_id")
        where = f"preregistration.claims[{index}]"
        if claim_id not in research_claims:
            findings.critical.append(f"{where}: unknown claim ID {claim_id}")
            continue
        exact = research_claims[claim_id].get("claim")
        if entry.get("exact_claim") != exact:
            findings.critical.append(f"{where}: exact claim text mismatch for {claim_id}")
        expected_hash = claim_hash(str(exact))
        if entry.get("claim_hash") != expected_hash:
            findings.critical.append(f"{where}: claim_hash mismatch for {claim_id}")
        plans = entry.get("adversarial_query_plan", [])
        rounds = [plan.get("round") for plan in plans if isinstance(plan, dict)]
        if rounds != sorted(rounds) or len(rounds) != len(set(rounds)):
            findings.critical.append(f"{where}: query-plan rounds must be unique and sorted")
        planned_queries: list[str] = []
        for plan in plans:
            if isinstance(plan, dict) and isinstance(plan.get("queries"), list):
                planned_queries.extend(plan["queries"])
        if len(planned_queries) != len(set(planned_queries)):
            findings.critical.append(f"{where}: duplicate planned query")
        if entry.get("planned_query_count") != len(planned_queries):
            findings.critical.append(f"{where}: planned_query_count does not match query plan")
        budget = entry.get("source_budget")
        if not isinstance(budget, dict):
            findings.critical.append(f"{where}: source budget is missing")
        else:
            max_rounds = budget.get("max_rounds")
            if isinstance(max_rounds, int) and rounds and max(rounds) > max_rounds:
                findings.critical.append(f"{where}: planned round exceeds source budget")
            if isinstance(max_rounds, int) and max_rounds > 2:
                findings.critical.append(f"{where}: two-round hard cap exceeded")
        selected[str(claim_id)] = entry
    findings.checks.append(f"preregistration checked: {len(selected)} high-impact claims")
    findings.checks.append(f"protected input hashes matched: {len(PROTECTED_PATHS)} files")
    return findings, prereg, selected


def query_rounds(prereg: dict[str, Any]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for entry in prereg.get("claims", []):
        if not isinstance(entry, dict):
            continue
        lookup: dict[str, int] = {}
        for plan in entry.get("adversarial_query_plan", []):
            if not isinstance(plan, dict):
                continue
            for query in plan.get("queries", []):
                lookup[query] = plan.get("round")
        result[entry.get("claim_id")] = lookup
    return result


def validate_attempt_claim(
    entry: dict[str, Any], prereg_entry: dict[str, Any], prereg_time: datetime | None, findings: Findings
) -> tuple[set[tuple[str, str, str]], dict[str, Any]]:
    claim_id = str(entry.get("claim_id"))
    where = f"attempts.{claim_id}"
    if entry.get("claim_hash") != prereg_entry.get("claim_hash"):
        findings.critical.append(f"{where}: claim_hash does not match preregistration")
    if entry.get("planned_query_count") != prereg_entry.get("planned_query_count"):
        findings.critical.append(f"{where}: planned query count changed after preregistration")
    planned = query_rounds({"claims": [prereg_entry]}).get(claim_id, {})
    attempts = entry.get("attempts", [])
    attempt_ids: list[str] = []
    executed_queries: list[str] = []
    opened: set[str] = set()
    credible: set[str] = set()
    credible_refs: set[tuple[str, str, str]] = set()
    used_rounds: list[int] = []
    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, dict):
            continue
        attempt_id = attempt.get("attempt_id")
        attempt_ids.append(attempt_id)
        query = attempt.get("query")
        executed_queries.append(query)
        round_number = attempt.get("round")
        if isinstance(round_number, int):
            used_rounds.append(round_number)
        if query not in planned:
            findings.critical.append(f"{where}.attempts[{index}]: query was not preregistered")
        elif planned[query] != round_number:
            findings.critical.append(f"{where}.attempts[{index}]: query used in wrong round")
        attempted_at = parse_time(attempt.get("attempted_at"), f"{where}.attempts[{index}].attempted_at", findings)
        if attempted_at and prereg_time:
            try:
                if attempted_at < prereg_time:
                    findings.critical.append(f"{where}.attempts[{index}]: search predates preregistration")
            except TypeError:
                findings.critical.append(f"{where}.attempts[{index}]: timestamp timezone mismatch")
        sources = attempt.get("opened_sources", [])
        if attempt.get("status") == "failed" and not str(attempt.get("failure_reason", "")).strip():
            findings.critical.append(f"{where}.attempts[{index}]: failed query missing failure_reason")
        source_urls = [str(source.get("url", "")) for source in sources if isinstance(source, dict)]
        if source_urls != sorted(source_urls):
            findings.critical.append(f"{where}.attempts[{index}]: opened_sources must be sorted by url")
        for source_index, source in enumerate(sources):
            if not isinstance(source, dict):
                continue
            source_where = f"{where}.attempts[{index}].opened_sources[{source_index}]"
            url, title = source.get("url"), source.get("title")
            if not valid_url(url):
                findings.critical.append(f"{source_where}: invalid original page URL")
                continue
            if source.get("fetch_status") == "opened":
                opened.add(url)
                if not isinstance(title, str) or not title.strip():
                    findings.critical.append(f"{source_where}: opened source missing title")
            if source.get("final_evidence"):
                if source.get("fetch_status") != "opened":
                    findings.critical.append(f"{source_where}: final evidence was not opened")
                host = urlsplit(url).netloc.lower()
                if host in SEARCH_HOSTS and "/search" in urlsplit(url).path:
                    findings.critical.append(f"{source_where}: search result page cannot be final evidence")
            if (
                source.get("final_evidence")
                and source.get("fetch_status") == "opened"
                and source.get("relation") == "contradicts"
                and source.get("source_kind") in CREDIBLE_KINDS
            ):
                credible.add(url)
                credible_refs.add((str(attempt_id), str(url), str(title)))
    if attempt_ids != sorted(attempt_ids):
        findings.critical.append(f"{where}: attempts must be sorted by attempt_id")
    if len(attempt_ids) != len(set(attempt_ids)):
        findings.critical.append(f"{where}: duplicate attempt_id")
    if len(executed_queries) != len(set(executed_queries)):
        findings.critical.append(f"{where}: duplicate executed query")
    if entry.get("actual_query_count") != len(attempts):
        findings.critical.append(f"{where}: actual_query_count does not match attempts")
    if len(attempts) > len(planned):
        findings.critical.append(f"{where}: actual queries exceed preregistered plan")
    actual_rounds = max(used_rounds, default=0)
    if entry.get("rounds_used") != actual_rounds:
        findings.critical.append(f"{where}: rounds_used does not match attempts")
    budget = prereg_entry.get("source_budget", {})
    if actual_rounds > 2 or actual_rounds > budget.get("max_rounds", 0):
        findings.critical.append(f"{where}: two-round or preregistered round cap exceeded")
    if len(opened) > budget.get("max_opened_sources", 0):
        findings.critical.append(f"{where}: opened-source budget exceeded")
    if entry.get("successful_open_count") != len(opened):
        findings.critical.append(f"{where}: successful_open_count does not match opened sources")
    if entry.get("credible_counterevidence_count") != len(credible):
        findings.critical.append(f"{where}: credible_counterevidence_count does not match sources")
    return credible_refs, {
        "planned_query_count": entry.get("planned_query_count"),
        "actual_query_count": entry.get("actual_query_count"),
        "successful_open_count": entry.get("successful_open_count"),
        "credible_counterevidence_count": entry.get("credible_counterevidence_count"),
        "uncovered_scope": entry.get("uncovered_scope"),
        "stop_reason": entry.get("stop_reason"),
    }


def verdict_section(text: str, claim_id: str, status: str) -> str | None:
    pattern = re.compile(
        rf"^###\s+{re.escape(claim_id)}\s+—\s+{re.escape(status)}\s*$\n(.*?)(?=^###\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1) if match else None


def validate_verdict_md(path: Path, verdicts: dict[str, dict[str, Any]], findings: Findings) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        findings.critical.append(f"missing human verdict: {path}")
        return
    if BOUNDARY_SENTENCE not in text:
        findings.critical.append("verdict.md missing bounded-epistemology sentence")
    if "验证穷尽度" not in text:
        findings.critical.append("verdict.md missing validation exhaustiveness section")
    for claim_id, verdict in verdicts.items():
        status = verdict.get("status")
        section = verdict_section(text, claim_id, str(status))
        if section is None:
            findings.critical.append(f"verdict.md missing exact claim section for {claim_id}")
            continue
        number_fields = {
            "计划查询数": verdict.get("planned_query_count"),
            "实际查询数": verdict.get("actual_query_count"),
            "成功打开源数": verdict.get("successful_open_count"),
            "可信反证数": verdict.get("credible_counterevidence_count"),
        }
        for label, expected in number_fields.items():
            match = re.search(rf"^-\s+{label}：([0-9]+)\s*$", section, re.MULTILINE)
            if not match:
                findings.critical.append(f"verdict.md {claim_id} missing exhaustiveness field {label}")
            elif int(match.group(1)) != expected:
                findings.critical.append(f"verdict.md {claim_id} {label} does not match machine verdict")
        for label in ("未覆盖范围", "停止原因"):
            match = re.search(rf"^-\s+{label}：(.+)$", section, re.MULTILINE)
            if not match or not match.group(1).strip():
                findings.critical.append(f"verdict.md {claim_id} missing exhaustiveness field {label}")
        if status == "survived" and TRUE_RE.search(section):
            findings.critical.append(f"verdict.md describes survived claim as true: {claim_id}")


def validate_outputs(root: Path) -> Findings:
    findings, prereg, selected = validate_preregistration(root)
    if not prereg:
        return findings
    prereg_path = root / "falsify/00-preregistration.json"
    attempts_path = root / "falsify/01-attempts.json"
    verdict_path = root / "falsify/02-verdict.json"
    quarantine_path = root / "falsify/03-quarantine.json"
    documents: dict[str, Any] = {}
    for key, path, schema in (
        ("attempts", attempts_path, "01-attempts.schema.json"),
        ("verdict", verdict_path, "02-verdict.schema.json"),
        ("quarantine", quarantine_path, "03-quarantine.schema.json"),
    ):
        try:
            documents[key] = read_json(path)
            validate_structure(documents[key], schema, findings)
        except ValueError as exc:
            findings.critical.append(str(exc))
            documents[key] = {}
    attempts_doc, verdict_doc, quarantine_doc = (
        documents["attempts"], documents["verdict"], documents["quarantine"]
    )
    if not all(isinstance(item, dict) and item for item in (attempts_doc, verdict_doc, quarantine_doc)):
        return findings
    project = prereg.get("project")
    for label, document in documents.items():
        if document.get("project") != project:
            findings.critical.append(f"{label} project does not match preregistration")
    prereg_sha = sha256_bytes(prereg_path)
    attempts_sha = sha256_bytes(attempts_path)
    verdict_sha = sha256_bytes(verdict_path)
    if attempts_doc.get("preregistration_sha256") != prereg_sha:
        findings.critical.append("attempts preregistration_sha256 mismatch")
    if verdict_doc.get("preregistration_sha256") != prereg_sha:
        findings.critical.append("verdict preregistration_sha256 mismatch")
    if verdict_doc.get("attempts_sha256") != attempts_sha:
        findings.critical.append("verdict attempts_sha256 mismatch")
    if quarantine_doc.get("verdict_sha256") != verdict_sha:
        findings.critical.append("quarantine verdict_sha256 mismatch")

    prereg_time = parse_time(prereg.get("generated_at"), "preregistration.generated_at", findings)
    attempt_entries = attempts_doc.get("claims", [])
    attempt_ids = [entry.get("claim_id") for entry in attempt_entries if isinstance(entry, dict)]
    verdict_entries = verdict_doc.get("verdicts", [])
    verdict_ids = [entry.get("claim_id") for entry in verdict_entries if isinstance(entry, dict)]
    expected_ids = sorted(selected)
    if attempt_ids != expected_ids:
        findings.critical.append("attempt claim IDs must exactly match sorted preregistered claim IDs")
    if verdict_ids != expected_ids:
        findings.critical.append("verdict claim IDs must exactly match sorted preregistered claim IDs")
    metrics: dict[str, dict[str, Any]] = {}
    credible_refs: dict[str, set[tuple[str, str, str]]] = {}
    for entry in attempt_entries:
        if not isinstance(entry, dict):
            continue
        claim_id = entry.get("claim_id")
        if claim_id not in selected:
            findings.critical.append(f"attempt for claim was not preregistered: {claim_id}")
            continue
        refs, values = validate_attempt_claim(entry, selected[claim_id], prereg_time, findings)
        credible_refs[claim_id] = refs
        metrics[claim_id] = values

    verdicts: dict[str, dict[str, Any]] = {}
    for entry in verdict_entries:
        if not isinstance(entry, dict):
            continue
        claim_id, status = entry.get("claim_id"), entry.get("status")
        if claim_id not in selected:
            findings.critical.append(f"verdict issued without preregistration: {claim_id}")
            continue
        if status not in STATUSES:
            findings.critical.append(f"invalid verdict status for {claim_id}: {status!r}")
        if entry.get("claim_hash") != selected[claim_id].get("claim_hash"):
            findings.critical.append(f"verdict claim_hash mismatch for {claim_id}")
        for key, expected in metrics.get(claim_id, {}).items():
            if entry.get(key) != expected:
                findings.critical.append(f"verdict {claim_id} {key} does not match attempts")
        if status == "falsified" and entry.get("credible_counterevidence_count", 0) < 1:
            findings.critical.append(f"falsified verdict lacks credible counterevidence: {claim_id}")
        if status == "unresolved" and not str(entry.get("stop_reason", "")).strip():
            findings.critical.append(f"unresolved verdict missing stop_reason: {claim_id}")
        if status == "survived":
            planned_count = entry.get("planned_query_count")
            actual_count = entry.get("actual_query_count")
            opened_count = entry.get("successful_open_count")
            max_opened = selected[claim_id].get("source_budget", {}).get("max_opened_sources")
            if actual_count != planned_count and opened_count != max_opened:
                findings.critical.append(
                    f"survived verdict stopped before query or opened-source budget was exhausted: {claim_id}"
                )
            if entry.get("credible_counterevidence_count") != 0:
                findings.critical.append(f"survived verdict has credible counterevidence: {claim_id}")
            if TRUE_RE.search(str(entry.get("reason", ""))):
                findings.critical.append(f"survived verdict is written as true: {claim_id}")
        verdicts[claim_id] = entry

    validate_verdict_md(root / "verdict.md", verdicts, findings)

    falsified_ids = sorted(cid for cid, entry in verdicts.items() if entry.get("status") == "falsified")
    quarantine_entries = quarantine_doc.get("entries", [])
    quarantine_ids = [entry.get("claim_id") for entry in quarantine_entries if isinstance(entry, dict)]
    if quarantine_ids != sorted(quarantine_ids):
        findings.critical.append("quarantine entries must be sorted by claim_id")
    if quarantine_ids != falsified_ids:
        findings.critical.append("quarantine entries must exactly match sorted falsified claim IDs")
    for entry in quarantine_entries:
        if not isinstance(entry, dict):
            continue
        claim_id = entry.get("claim_id")
        if entry.get("claim_hash") != selected.get(claim_id, {}).get("claim_hash"):
            findings.critical.append(f"quarantine claim_hash mismatch for {claim_id}")
        if entry.get("action") != "audit-reference-only" or entry.get("original_preserved") is not True:
            findings.critical.append(f"quarantine is not audit-only for {claim_id}")
        counterevidence_refs = entry.get("counterevidence_refs", [])
        ref_keys = [
            (str(ref.get("attempt_id", "")), str(ref.get("url", "")), str(ref.get("title", "")))
            for ref in counterevidence_refs
            if isinstance(ref, dict)
        ]
        if ref_keys != sorted(ref_keys):
            findings.critical.append(f"quarantine counterevidence_refs must be stably sorted: {claim_id}")
        for ref in counterevidence_refs:
            if not isinstance(ref, dict):
                continue
            key = (str(ref.get("attempt_id")), str(ref.get("url")), str(ref.get("title")))
            if key not in credible_refs.get(claim_id, set()):
                findings.critical.append(f"quarantine source is not credible attempt evidence for {claim_id}")

    status_counts = {status: sum(1 for entry in verdicts.values() if entry.get("status") == status) for status in sorted(STATUSES)}
    if not status_counts.get("falsified"):
        findings.warnings.append("real run contains no falsified claim; cover this boundary with a fixture")
    if not status_counts.get("survived"):
        findings.warnings.append("real run contains no survived claim; cover this boundary with a fixture")
    if not status_counts.get("unresolved"):
        findings.warnings.append("real run contains no unresolved claim; cover this boundary with a negative fixture")
    findings.checks.append(f"attempt logs reconciled: {len(metrics)} claims")
    findings.checks.append(f"verdicts reconciled: {len(verdicts)} claims; states={status_counts}")
    findings.checks.append(f"quarantine audit entries checked: {len(quarantine_entries)}")
    findings.checks.append(f"protected input hashes unchanged: {len(PROTECTED_PATHS)} files")
    return findings


def print_findings(label: str, findings: Findings) -> int:
    print(f"{label}: critical={len(findings.critical)} warnings={len(findings.warnings)}")
    for item in findings.critical:
        print(f"CRITICAL: {item}")
    for item in findings.warnings:
        print(f"WARNING: {item}")
    for item in findings.checks:
        print(f"CHECK: {item}")
    return 1 if findings.critical else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("probe", "preregister", "validate", "hashes"):
        child = subparsers.add_parser(command)
        child.add_argument("project_root", type=Path)
    claim = subparsers.add_parser("claim-hash")
    claim.add_argument("project_root", type=Path)
    claim.add_argument("claim_id")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.project_root.expanduser().resolve()
    if args.command == "probe":
        findings, _, _ = probe_inputs(root)
        return print_findings("falsify probe", findings)
    if args.command == "preregister":
        findings, _, _ = validate_preregistration(root)
        return print_findings("falsify preregistration", findings)
    if args.command == "validate":
        return print_findings("falsify validation", validate_outputs(root))
    if args.command == "hashes":
        findings, _, _ = probe_inputs(root)
        if findings.critical:
            return print_findings("falsify probe", findings)
        manifest = [{"path": path, "sha256": sha256_bytes(root / path)} for path in PROTECTED_PATHS]
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    findings, _, claims = probe_inputs(root)
    if findings.critical:
        return print_findings("falsify probe", findings)
    claim = claims.get(args.claim_id)
    if claim is None:
        print(f"unknown claim ID: {args.claim_id}")
        return 1
    print(claim_hash(str(claim.get("claim", ""))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
