#!/usr/bin/env python3
# © Siyuan (AI·LAB), CC BY 4.0
"""Validate report inputs and Markdown, generate sources, and render deterministic HTML."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Any
from urllib.parse import urlsplit, urlunsplit


STAGE_FILES = (
    "03-s1-foundations.json",
    "04-s2-business-model.json",
    "05-s2.5-landscape.json",
    "06-s3-user-pains.json",
    "07-s4-opportunities.json",
    "08-s5-product-architecture.json",
)
HANDOFF_FILES = (
    "10-research-report.md",
    "11-claim-register.json",
    "12-sources.md",
    "13-open-questions.md",
    "14-validation-report.md",
)
LABELS = {
    "[Data]": "事实依据",
    "[Estimate]": "推算判断",
    "[Assumption]": "待验证假设",
    "[Opinion]": "建议判断",
}
REQUIRED_HEADINGS = (
    "执行摘要",
    "Red Flags",
    "Yellow Flags",
    "Open Questions",
    "验证边界",
    "专业附件入口",
    "来源附录",
)
REQUIRED_DIMENSIONS = ("行业", "商业模式", "竞争", "用户痛点", "机会", "产品选择")
BOUNDARY_SENTENCE = "本次“未推翻”只代表在已声明范围内未找到足够反证，不代表该结论为真。"
SOURCE_START = "<!-- REPORT:SOURCES:START -->"
SOURCE_END = "<!-- REPORT:SOURCES:END -->"
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
TAG_RE = re.compile(r"<!--\s*(\[(?:Data|Estimate|Assumption|Opinion)\])\s*-->")
CLAIMS_RE = re.compile(r"<!--\s*claims:([^>]+?)\s*-->")
METADATA_SECTIONS = {"验证边界", "专业附件入口"}
VALIDATION_METADATA_RE = re.compile(
    r"(?:裁决夹具|验证范围|验证边界|验证方法|未覆盖|来源真相源|"
    r"artifacts\.sources|research/|falsify/|verdict\.md|机器裁决)"
)
ATTACHMENT_METADATA_RE = re.compile(
    r"^(?:原始阶段数据与声明册|反证后边界|上游质量证据|专业附件)入口：.*`[^`]+`"
)
ANSWER_BYPASS_RE = re.compile(
    r"(?:值得|建议|应当|应该|必须|须|首选|第二顺位|优先|选择|进入|切入|"
    r"启动|停止|立项|推出|定价|销售|投放|扩张|聚焦|采用|放弃|行动|"
    r"产品选择|商业模式)"
)
GENERIC_HEADING_RE = re.compile(
    r"^(?:\d+[.、]\s*)?(?:情境|冲突|问题|答案|背景|总结|行业分析|竞争分析|"
    r"用户痛点|机会分析|产品选择)(?:\s*$|\s*[:：·—-])",
    re.IGNORECASE,
)
SUPPORT_HEADING_RE = re.compile(
    r"^论点\s*(?:[1-5]|一|二|三|四|五)\s*[｜|:：]\s*(.+)$",
    re.IGNORECASE,
)
EVIDENCE_GROUP_HEADING_RE = re.compile(
    r"^证据组\s*(?:[1-9]\d*|一|二|三|四|五|六|七|八|九|十)\s*[｜|:：]\s*(.+)$",
    re.IGNORECASE,
)
STRUCTURAL_PREFIX_RE = re.compile(
    r"^(?:执行摘要|论点\s*(?:[1-5]|一|二|三|四|五)|"
    r"证据组\s*(?:[1-9]\d*|一|二|三|四|五|六|七|八|九|十)|"
    r"Red Flags|Yellow Flags|Open Questions|验证边界|专业附件入口|来源附录)\s*[｜|:：]\s*",
    re.IGNORECASE,
)
JUDGMENT_CUE_RE = re.compile(
    r"(?:是|不是|仍|已|将|会|应|需|必须|可以|可|不能|不会|决定|取决于|"
    r"意味着|表明|证明|支持|支撑|构成|成立|失效|优于|高于|低于|强于|弱于|"
    r"足以|不足|尚未|存在|缺失|拖住|击穿|收缩|上移|归零|完成|保留|绕开|"
    r"进入|退出|维持|改为|不等于|只影响|不影响|分化|收敛|可信|不可|未决|待验证)"
)


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    tier: str
    collected: str
    supported_claim_ids: tuple[str, ...]


@dataclass
class Findings:
    critical: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)

    def extend(self, other: "Findings") -> None:
        self.critical.extend(other.critical)
        self.warnings.extend(other.warnings)
        self.checks.extend(other.checks)


@dataclass
class Context:
    project: str
    claims: dict[str, dict[str, Any]]
    sources: dict[str, Source]
    verdicts: dict[str, dict[str, Any]]
    findings: Findings


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from None


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        tmp.write(content)
        temp_path = Path(tmp.name)
    temp_path.replace(path)


def claim_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit((scheme, netloc, path, parsed.query, ""))


def valid_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def valid_date(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))


def parse_source_table(path: Path) -> tuple[dict[str, tuple[str, str]], list[str]]:
    rows: dict[str, tuple[str, str]] = {}
    errors: list[str] = []
    header: list[str] | None = None
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if "ID" in cells and "Source" in cells and "URL" in cells:
            header = cells
            continue
        if not header or all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if len(cells) != len(header):
            continue
        record = dict(zip(header, cells))
        source_id = record.get("ID", "")
        if not re.fullmatch(r"S\d+", source_id):
            continue
        title, url = record.get("Source", ""), record.get("URL", "")
        prior = rows.get(source_id)
        current = (title, url)
        if prior and prior != current:
            errors.append(f"{path.name}:{number}: duplicate source ID conflict: {source_id}")
        rows[source_id] = current
    return rows, errors


def load_context(project_root: Path, verdict_json: Path | None, verdict_md: Path | None) -> Context:
    root = project_root.expanduser().resolve()
    research = root / "research"
    findings = Findings()

    missing = [name for name in (*STAGE_FILES, *HANDOFF_FILES) if not (research / name).is_file()]
    if missing:
        findings.critical.append(f"missing research files: {', '.join(missing)}")

    claims: dict[str, dict[str, Any]] = {}
    sources: dict[str, Source] = {}
    for file_name in STAGE_FILES:
        path = research / file_name
        if not path.is_file():
            continue
        try:
            data = read_json(path)
        except ValueError as exc:
            findings.critical.append(str(exc))
            continue
        if not isinstance(data, dict):
            findings.critical.append(f"{file_name}: root must be an object")
            continue
        for claim in data.get("claims", []):
            if not isinstance(claim, dict):
                findings.critical.append(f"{file_name}: claim must be an object")
                continue
            claim_id = claim.get("id")
            if not isinstance(claim_id, str) or not claim_id:
                findings.critical.append(f"{file_name}: claim missing id")
                continue
            if claim_id in claims and claims[claim_id] != claim:
                findings.critical.append(f"claim ID conflict: {claim_id}")
            claims[claim_id] = claim
        artifacts = data.get("artifacts", {})
        if not isinstance(artifacts, dict):
            findings.critical.append(f"{file_name}: artifacts must be an object")
            continue
        stage_sources = artifacts.get("sources", [])
        if not isinstance(stage_sources, list):
            findings.critical.append(f"{file_name}: artifacts.sources must be an array")
            continue
        for index, item in enumerate(stage_sources):
            where = f"{file_name}:artifacts.sources[{index}]"
            if not isinstance(item, dict):
                findings.critical.append(f"{where}: source must be an object")
                continue
            required = ("id", "title", "url", "tier", "collected", "supported_claim_ids")
            absent = [key for key in required if key not in item]
            if absent:
                findings.critical.append(f"{where}: missing {', '.join(absent)}")
                continue
            source_id = item["id"]
            supported = item["supported_claim_ids"]
            if not isinstance(source_id, str) or not re.fullmatch(r"S\d+", source_id):
                findings.critical.append(f"{where}: invalid source id")
                continue
            if not isinstance(item["title"], str) or not item["title"].strip():
                findings.critical.append(f"{where}: missing title")
            if not valid_url(item["url"]):
                findings.critical.append(f"{where}: invalid URL")
            if item["tier"] not in {"T1", "T2", "T3", "T4"}:
                findings.critical.append(f"{where}: invalid tier")
            if not valid_date(item["collected"]):
                findings.critical.append(f"{where}: collected must be YYYY-MM-DD")
            if not isinstance(supported, list) or any(not isinstance(value, str) for value in supported):
                findings.critical.append(f"{where}: supported_claim_ids must be strings")
                supported = []
            source = Source(
                id=source_id,
                title=str(item["title"]).strip(),
                url=str(item["url"]).strip(),
                tier=str(item["tier"]),
                collected=str(item["collected"]),
                supported_claim_ids=tuple(sorted(set(supported))),
            )
            prior = sources.get(source_id)
            if prior and (prior.title != source.title or normalize_url(prior.url) != normalize_url(source.url)):
                findings.critical.append(f"source ID conflict: {source_id} maps to different title or URL")
            elif prior and prior != source:
                findings.critical.append(f"source metadata conflict: {source_id}")
            else:
                sources[source_id] = source

    for claim_id, claim in claims.items():
        source_ids = claim.get("source_ids", [])
        if not isinstance(source_ids, list):
            findings.critical.append(f"{claim_id}: source_ids must be an array")
            continue
        if claim.get("label") == "[Data]" and not source_ids:
            findings.critical.append(f"{claim_id}: [Data] claim has no source IDs")
        for source_id in source_ids:
            if source_id not in sources:
                findings.critical.append(f"{claim_id}: dangling source ID {source_id}")

    if not sources:
        findings.critical.append("stage artifacts contain no report source catalog")

    register_project = ""
    register_path = research / "11-claim-register.json"
    if register_path.is_file():
        try:
            register = read_json(register_path)
            if isinstance(register, dict):
                register_project = str(register.get("project", ""))
                register_ids = [entry.get("id") for entry in register.get("claims", []) if isinstance(entry, dict)]
                if set(register_ids) != set(claims):
                    findings.critical.append("claim register IDs do not match stage claim IDs")
        except ValueError as exc:
            findings.critical.append(str(exc))

    compatibility_path = research / "12-sources.md"
    if compatibility_path.is_file():
        compatibility, table_errors = parse_source_table(compatibility_path)
        findings.critical.extend(table_errors)
        for source_id, source in sources.items():
            if source_id not in compatibility:
                findings.warnings.append(f"12-sources.md omits stage source {source_id}")
                continue
            title, url = compatibility[source_id]
            if title != source.title or not valid_url(url) or normalize_url(url) != normalize_url(source.url):
                findings.critical.append(f"12-sources.md conflicts with stage source {source_id}")
        extras = sorted(set(compatibility) - set(sources))
        if extras:
            findings.warnings.append(f"12-sources.md has non-catalog IDs: {', '.join(extras)}")

    verdict_json_path = (verdict_json or root / "falsify" / "02-verdict.json").expanduser().resolve()
    verdict_md_path = (verdict_md or root / "verdict.md").expanduser().resolve()
    verdicts: dict[str, dict[str, Any]] = {}
    if not verdict_json_path.is_file():
        findings.critical.append(f"missing machine verdict: {verdict_json_path}")
    else:
        try:
            overlay = read_json(verdict_json_path)
            if not isinstance(overlay, dict):
                findings.critical.append("machine verdict root must be an object")
            else:
                for key in ("schema_version", "project", "generated_at", "verdicts"):
                    if key not in overlay:
                        findings.critical.append(f"machine verdict missing {key}")
                if register_project and overlay.get("project") != register_project:
                    findings.critical.append("machine verdict project does not match claim register")
                entries = overlay.get("verdicts", [])
                if not isinstance(entries, list) or not entries:
                    findings.critical.append("machine verdicts must be a non-empty array")
                    entries = []
                for index, verdict in enumerate(entries):
                    where = f"machine verdict[{index}]"
                    if not isinstance(verdict, dict):
                        findings.critical.append(f"{where}: must be an object")
                        continue
                    claim_id = verdict.get("claim_id")
                    status = verdict.get("status")
                    if claim_id not in claims:
                        findings.critical.append(f"{where}: unknown claim ID {claim_id}")
                        continue
                    if claim_id in verdicts:
                        findings.critical.append(f"duplicate machine verdict claim ID: {claim_id}")
                    if status not in {"falsified", "survived", "unresolved"}:
                        findings.critical.append(f"{where}: invalid status")
                    if not isinstance(verdict.get("reason"), str) or not verdict.get("reason", "").strip():
                        findings.critical.append(f"{where}: missing reason")
                    if status == "unresolved" and not str(verdict.get("stop_reason", "")).strip():
                        findings.critical.append(f"{where}: unresolved verdict missing stop_reason")
                    expected_hash = claim_hash(str(claims[claim_id].get("claim", "")))
                    if verdict.get("claim_hash") != expected_hash:
                        findings.critical.append(f"{where}: claim_hash mismatch for {claim_id}")
                    verdicts[claim_id] = verdict
        except ValueError as exc:
            findings.critical.append(str(exc))

    if not verdict_md_path.is_file():
        findings.critical.append(f"missing human verdict: {verdict_md_path}")
    else:
        verdict_text = verdict_md_path.read_text(encoding="utf-8")
        if BOUNDARY_SENTENCE not in verdict_text:
            findings.critical.append("verdict.md missing bounded-epistemology sentence")
        for claim_id in verdicts:
            if claim_id not in verdict_text:
                findings.critical.append(f"verdict.md does not mention {claim_id}")

    findings.checks.append(f"research handoff checked: {len(claims)} claims")
    findings.checks.append(f"stage source catalog merged: {len(sources)} source IDs")
    findings.checks.append(f"machine verdict checked: {len(verdicts)} adjudicated claims")
    return Context(register_project, claims, sources, verdicts, findings)


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def source_block(sources: dict[str, Source]) -> str:
    grouped: dict[str, list[Source]] = {}
    for source in sources.values():
        grouped.setdefault(normalize_url(source.url), []).append(source)
    rows: list[str] = [
        SOURCE_START,
        "| ID | Tier | Source | Collected | Supported claims |",
        "|---|---|---|---|---|",
    ]
    groups = sorted(grouped.values(), key=lambda group: min(item.id for item in group))
    for group in groups:
        ordered = sorted(group, key=lambda item: item.id)
        canonical = ordered[0]
        aliases = ", ".join(item.id for item in ordered)
        claims = sorted({claim for item in ordered for claim in item.supported_claim_ids})
        supported = ", ".join(claims) if claims else "—"
        rows.append(
            f"| {escape_cell(aliases)} | {canonical.tier} | "
            f"[{escape_cell(canonical.title)}]({canonical.url}) | {canonical.collected} | {escape_cell(supported)} |"
        )
    rows.append(SOURCE_END)
    return "\n".join(rows)


def replace_source_block(text: str, replacement: str) -> str:
    if text.count(SOURCE_START) != 1 or text.count(SOURCE_END) != 1:
        raise ValueError("report must contain exactly one source marker pair")
    start = text.index(SOURCE_START)
    end = text.index(SOURCE_END, start) + len(SOURCE_END)
    return text[:start] + replacement + text[end:]


def strip_frontmatter(lines: list[str]) -> list[str]:
    if not lines or lines[0].strip() != "---":
        return lines
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[index + 1 :]
    return lines


def is_table_separator(line: str) -> bool:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return False
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def parse_claim_ids(line: str) -> list[str]:
    match = CLAIMS_RE.search(line)
    if not match:
        return []
    return [part.strip() for part in match.group(1).split(",") if part.strip()]


def report_section(heading: str) -> str | None:
    for required in REQUIRED_HEADINGS:
        if required.lower() in heading.lower():
            return required
    return None


def visible_claim_text(line: str) -> str:
    value = re.sub(r"<!--.*?-->", "", line).strip().strip("|").strip()
    for label in LABELS.values():
        value = value.replace(f"**{label}**：", "", 1)
    return value.strip()


def action_title_core(heading: str) -> str:
    """Remove a recognized structural prefix and Markdown decoration."""
    core = STRUCTURAL_PREFIX_RE.sub("", heading.strip(), count=1)
    core = re.sub(r"[*_`#]", "", core)
    return core.strip()


def is_generic_heading(heading: str) -> bool:
    return bool(GENERIC_HEADING_RE.search(heading.strip()))


def is_action_title(heading: str) -> bool:
    """Use a conservative deterministic proxy for a complete judgment title."""
    core = action_title_core(heading)
    visible_chars = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", core)
    if len(visible_chars) < 8:
        return False
    if re.search(r"(?:分析|概览|背景|总结|现状|情况|介绍|复盘|研究)$", core):
        return False
    return bool(JUDGMENT_CUE_RE.search(core))


def validate_structure(text: str, report_name: str = "report.md") -> Findings:
    """Validate pyramid placement, action titles, and evidence grouping."""
    findings = Findings()
    heading_records = [
        (len(match.group(1)), match.group(2).strip(), match.start())
        for match in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)
    ]

    for level, heading, _ in heading_records:
        if level not in {2, 3}:
            continue
        if is_generic_heading(heading):
            findings.critical.append(f"generic column heading is forbidden: {heading}")
            continue
        if not is_action_title(heading):
            findings.critical.append(f"section heading is not a complete judgment: {heading}")

    body = text.split(SOURCE_START, 1)[0]
    visible_lines = [
        line.strip()
        for line in strip_frontmatter(body.splitlines())
        if line.strip() and not (line.strip().startswith("<!--") and line.strip().endswith("-->"))
    ]
    governing_positions = [
        index for index, line in enumerate(visible_lines) if "**最高判断**" in line
    ]
    if not governing_positions:
        findings.critical.append("missing governing thought marker: **最高判断**")
    elif len(governing_positions) > 1:
        findings.critical.append("governing thought marker must appear exactly once")
    elif governing_positions[0] > 2:
        findings.critical.append("governing thought must appear within the first three visible lines")

    support_records = [
        (heading, position)
        for level, heading, position in heading_records
        if level == 2 and SUPPORT_HEADING_RE.match(heading)
    ]
    if not 3 <= len(support_records) <= 5:
        findings.critical.append(
            f"report needs 3-5 support arguments; found {len(support_records)}"
        )
    for index, (heading, position) in enumerate(support_records):
        next_h2_positions = [
            candidate_position
            for level, _, candidate_position in heading_records
            if level == 2 and candidate_position > position
        ]
        section_end = min(next_h2_positions) if next_h2_positions else len(text)
        evidence_groups = [
            candidate_heading
            for level, candidate_heading, candidate_position in heading_records
            if level == 3
            and position < candidate_position < section_end
            and EVIDENCE_GROUP_HEADING_RE.match(candidate_heading)
        ]
        if not evidence_groups:
            findings.critical.append(f"support argument has no evidence group: {heading}")

    findings.checks.append(f"pyramid support arguments checked: {len(support_records)}")
    findings.checks.append("action-title headings checked")
    return findings


def is_metadata_exception(section: str | None, line: str, tag: str) -> bool:
    """Allow only narrowly recognizable delivery metadata to omit a claim mapping."""
    if section not in METADATA_SECTIONS or tag != "[Opinion]":
        return False
    content = visible_claim_text(line)
    if ANSWER_BYPASS_RE.search(content):
        return False
    if section == "验证边界":
        return bool(VALIDATION_METADATA_RE.search(content))
    return bool(ATTACHMENT_METADATA_RE.search(content))


def validate_report(context: Context, report_path: Path) -> Findings:
    findings = Findings()
    try:
        text = report_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        findings.critical.append(f"missing report: {report_path}")
        return findings

    findings.extend(validate_structure(text, report_path.name))

    headings = [match.group(1).strip() for match in re.finditer(r"^#{1,6}\s+(.+)$", text, re.MULTILINE)]
    for required in REQUIRED_HEADINGS:
        if not any(required.lower() in heading.lower() for heading in headings):
            findings.critical.append(f"missing required heading: {required}")
    for dimension in REQUIRED_DIMENSIONS:
        if dimension not in text:
            findings.critical.append(f"report does not cover required dimension: {dimension}")
    for heading in headings:
        if re.search(r"(?:^|\s)(?:S[1-6](?:\.5)?|Stage\s*\d+)(?:\s|$|[:：])", heading, re.IGNORECASE):
            findings.critical.append(f"mechanical stage heading is forbidden: {heading}")

    expected = source_block(context.sources)
    try:
        actualized = replace_source_block(text, expected)
        if actualized != text:
            findings.critical.append("source appendix is stale or manually edited; rerun sources")
    except ValueError as exc:
        findings.critical.append(str(exc))

    body = text.split(SOURCE_START, 1)[0]
    lines = strip_frontmatter(body.splitlines())
    known_links: dict[tuple[str, str], list[Source]] = {}
    for source in context.sources.values():
        known_links.setdefault((source.title, normalize_url(source.url)), []).append(source)
    falsified = {claim_id for claim_id, verdict in context.verdicts.items() if verdict.get("status") == "falsified"}
    unresolved = {claim_id for claim_id, verdict in context.verdicts.items() if verdict.get("status") == "unresolved"}
    used_unresolved: set[str] = set()

    for claim_id in falsified:
        if re.search(rf"\b{re.escape(claim_id)}\b", body):
            findings.critical.append(f"falsified claim ID leaked into report body: {claim_id}")
        claim_text = str(context.claims[claim_id].get("claim", "")).strip()
        if claim_text and claim_text in body:
            findings.critical.append(f"falsified claim text leaked into report body: {claim_id}")

    current_section: str | None = None
    for index, raw in enumerate(lines):
        number = index + 1
        line = raw.strip()
        heading_match = re.match(r"^#{1,6}\s+(.+)$", line)
        if heading_match:
            matched_section = report_section(heading_match.group(1).strip())
            if matched_section is not None:
                current_section = matched_section

        for claim_id in unresolved:
            claim_text = str(context.claims[claim_id].get("claim", "")).strip()
            claim_is_present = bool(re.search(rf"\b{re.escape(claim_id)}\b", line))
            claim_is_present = claim_is_present or bool(claim_text and claim_text in line)
            if not claim_is_present:
                continue
            if current_section == "Open Questions":
                used_unresolved.add(claim_id)
            else:
                findings.critical.append(
                    f"{report_path.name}:{number}: unresolved claim outside Open Questions: {claim_id}"
                )

        if not line or heading_match or line == "---" or line in {SOURCE_START, SOURCE_END}:
            continue
        if is_table_separator(line):
            continue
        if line.startswith("|") and index + 1 < len(lines) and is_table_separator(lines[index + 1]):
            continue
        if line.startswith("<!--") and line.endswith("-->"):
            continue

        tags = TAG_RE.findall(line)
        if len(tags) != 1:
            findings.critical.append(f"{report_path.name}:{number}: substantive line needs exactly one machine label")
            continue
        tag = tags[0]
        human = LABELS[tag]
        visible_labels = [label for label in LABELS.values() if f"**{label}**" in line]
        if visible_labels != [human]:
            findings.critical.append(f"{report_path.name}:{number}: human label does not match {tag}")

        claim_ids = parse_claim_ids(line)
        if not claim_ids and not is_metadata_exception(current_section, line, tag):
            findings.critical.append(f"{report_path.name}:{number}: {tag} line missing claim mapping")
        for claim_id in claim_ids:
            if claim_id not in context.claims:
                findings.critical.append(f"{report_path.name}:{number}: unknown claim ID {claim_id}")
                continue
            if claim_id in falsified:
                findings.critical.append(f"{report_path.name}:{number}: falsified claim leaked: {claim_id}")
            expected_label = context.claims[claim_id].get("label")
            if expected_label != tag:
                findings.critical.append(
                    f"{report_path.name}:{number}: {claim_id} is {expected_label}, not {tag}"
                )

        links = LINK_RE.findall(line)
        resolved_links: list[Source] = []
        for title, url in links:
            matches = known_links.get((title, normalize_url(url)), []) if valid_url(url) else []
            if not matches:
                findings.critical.append(
                    f"{report_path.name}:{number}: link title/URL not in stage source catalog: {title}"
                )
            resolved_links.extend(matches)

        if tag == "[Data]":
            if not links:
                findings.critical.append(f"{report_path.name}:{number}: [Data] needs same-line title and URL")
            for claim_id in claim_ids:
                if claim_id in context.claims and not any(
                    claim_id in source.supported_claim_ids for source in resolved_links
                ):
                    findings.critical.append(
                        f"{report_path.name}:{number}: no same-line source supports {claim_id}"
                    )
        if tag == "[Estimate]":
            if "推算逻辑：" not in line:
                findings.critical.append(f"{report_path.name}:{number}: [Estimate] missing 推算逻辑：")
            if not links:
                findings.critical.append(f"{report_path.name}:{number}: [Estimate] needs a linked data premise")

        if re.search(r"\[(?:S\d+|\^S\d+)\]", line):
            findings.critical.append(f"{report_path.name}:{number}: ID-only or footnote citation is forbidden")
        if "见来源册" in line:
            findings.critical.append(f"{report_path.name}:{number}: source-register pointer is not a proof chain")

    if used_unresolved:
        findings.warnings.append(f"unresolved claims remain visible: {', '.join(sorted(used_unresolved))}")
    findings.checks.append(f"report body checked: {len(lines)} lines")
    findings.checks.append(f"falsified claim exclusion checked: {len(falsified)} claims")
    findings.checks.append(f"source appendix checked: {len(context.sources)} source IDs")
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


def inline_html(value: str) -> str:
    clean = re.sub(r"<!--.*?-->", "", value).strip()
    escaped = html.escape(clean, quote=True)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
        lambda match: f'<a href="{match.group(2)}">{match.group(1)}</a>',
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    classes = {
        "事实依据": "data",
        "推算判断": "estimate",
        "待验证假设": "assumption",
        "建议判断": "opinion",
    }
    for label, css_class in classes.items():
        escaped = escaped.replace(
            f"<strong>{label}</strong>：",
            f'<span class="claim-badge {css_class}">{label}</span>',
        )
        escaped = escaped.replace(
            f"<strong>{label}</strong>",
            f'<span class="claim-badge {css_class}">{label}</span>',
        )
    return escaped


def render_markdown(markdown_text: str) -> str:
    lines = strip_frontmatter(markdown_text.splitlines())
    output: list[str] = []
    index = 0
    heading_counter = 0
    while index < len(lines):
        raw = lines[index]
        line = raw.strip()
        if not line or (line.startswith("<!--") and line.endswith("-->")):
            index += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            heading_counter += 1
            output.append(f'<h{level} id="section-{heading_counter}">{inline_html(heading.group(2))}</h{level}>')
            index += 1
            continue
        if line == "---":
            output.append("<hr>")
            index += 1
            continue
        if line.startswith("|") and index + 1 < len(lines) and is_table_separator(lines[index + 1]):
            headers = [cell.strip() for cell in line.strip("|").split("|")]
            index += 2
            rows: list[list[str]] = []
            while index < len(lines):
                candidate = re.sub(r"\s*<!--.*?-->", "", lines[index]).strip()
                if not (candidate.startswith("|") and candidate.endswith("|")):
                    break
                rows.append([cell.strip() for cell in candidate.strip("|").split("|")])
                index += 1
            table = ["<table><thead><tr>"]
            table.extend(f"<th>{inline_html(cell)}</th>" for cell in headers)
            table.append("</tr></thead><tbody>")
            for row in rows:
                table.append("<tr>")
                table.extend(f"<td>{inline_html(cell)}</td>" for cell in row)
                table.append("</tr>")
            table.append("</tbody></table>")
            output.append("".join(table))
            continue
        if line.startswith("- "):
            items: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                items.append(lines[index].strip()[2:])
                index += 1
            output.append("<ul>" + "".join(f"<li>{inline_html(item)}</li>" for item in items) + "</ul>")
            continue
        if re.match(r"\d+\.\s+", line):
            items = []
            while index < len(lines) and re.match(r"\d+\.\s+", lines[index].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[index].strip()))
                index += 1
            output.append("<ol>" + "".join(f"<li>{inline_html(item)}</li>" for item in items) + "</ol>")
            continue
        if line.startswith("> "):
            output.append(f"<blockquote>{inline_html(line[2:])}</blockquote>")
            index += 1
            continue
        output.append(f"<p>{inline_html(line)}</p>")
        index += 1
    return "\n".join(output)


CSS = """
:root{--ink:#172033;--muted:#667085;--line:#d9dee8;--paper:#fff;--wash:#f5f7fa;--navy:#17365d}
*{box-sizing:border-box}body{margin:0;background:var(--wash);color:var(--ink);font:16px/1.75 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC",sans-serif}
main{max-width:900px;margin:0 auto;padding:64px 72px;background:var(--paper);min-height:100vh;box-shadow:0 2px 18px rgba(23,32,51,.06)}
h1,h2,h3{color:var(--navy);line-height:1.3}h1{font-size:34px}h2{margin-top:2.4em;border-bottom:1px solid var(--line);padding-bottom:.35em}h3{margin-top:1.8em}
p,li{margin:.7em 0}a{color:#175cd3;text-underline-offset:3px}table{width:100%;border-collapse:collapse;margin:1.3em 0;font-size:14px}th,td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}th{background:#eef2f7;color:var(--navy)}
.claim-badge{display:inline-block;margin-right:.55em;padding:.08em .55em;border:1px solid var(--line);border-radius:999px;color:var(--muted);font-size:.78em;font-weight:600;background:#fafbfc}.claim-badge.data{border-color:#b8d2c0}.claim-badge.estimate{border-color:#d8c18b}.claim-badge.assumption{border-color:#d8a8a8}.claim-badge.opinion{border-color:#b8c5dc}
code{background:#eef2f7;padding:.12em .35em;border-radius:4px}blockquote{margin:1em 0;padding:.7em 1em;border-left:3px solid var(--navy);background:#f8fafc;color:var(--muted)}
@media(max-width:700px){main{padding:28px 20px}h1{font-size:28px}table{display:block;overflow-x:auto}}@media print{body{background:#fff}main{box-shadow:none;padding:0}}
""".strip()


def render_html(markdown_path: Path, output_path: Path) -> None:
    markdown_text = markdown_path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", markdown_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "商业咨询报告"
    digest = hashlib.sha256(markdown_text.encode("utf-8")).hexdigest()
    body = render_markdown(markdown_text)
    document = (
        "<!doctype html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        f"<meta name=\"source-sha256\" content=\"{digest}\">\n"
        f"<title>{html.escape(title)}</title>\n<style>{CSS}</style>\n</head>\n<body>\n"
        f"<main>\n{body}\n</main>\n</body>\n</html>\n"
    )
    atomic_write(output_path, document)


def add_verdict_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--verdict-json", type=Path)
    parser.add_argument("--verdict-md", type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    probe = subparsers.add_parser("probe")
    probe.add_argument("project_root", type=Path)
    add_verdict_args(probe)
    sources = subparsers.add_parser("sources")
    sources.add_argument("project_root", type=Path)
    sources.add_argument("report_md", type=Path)
    add_verdict_args(sources)
    validate = subparsers.add_parser("validate")
    validate.add_argument("project_root", type=Path)
    validate.add_argument("report_md", type=Path)
    add_verdict_args(validate)
    render = subparsers.add_parser("render")
    render.add_argument("report_md", type=Path)
    render.add_argument("output_html", type=Path, nargs="?")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "render":
        output = args.output_html or args.report_md.with_suffix(".html")
        try:
            render_html(args.report_md.expanduser().resolve(), output.expanduser().resolve())
        except (FileNotFoundError, ValueError) as exc:
            print(f"RENDER FAILED: {exc}")
            return 1
        print(f"rendered {output.expanduser().resolve()}")
        return 0

    context = load_context(args.project_root, args.verdict_json, args.verdict_md)
    if args.command == "probe":
        return print_findings("report probe", context.findings)
    if context.findings.critical:
        return print_findings("report probe", context.findings)
    if args.command == "sources":
        report = args.report_md.expanduser().resolve()
        try:
            text = report.read_text(encoding="utf-8")
            atomic_write(report, replace_source_block(text, source_block(context.sources)))
        except (FileNotFoundError, ValueError) as exc:
            print(f"SOURCE GENERATION FAILED: {exc}")
            return 1
        print(f"generated source appendix: {report}")
        return 0
    findings = Findings()
    findings.extend(context.findings)
    findings.extend(validate_report(context, args.report_md.expanduser().resolve()))
    return print_findings("report validation", findings)


if __name__ == "__main__":
    sys.exit(main())
