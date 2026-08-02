---
name: report
description: Turn a completed business-consult research package and falsify verdict overlay into a defensible pyramid-structured Markdown report with a first-screen governing thought, three to five MECE arguments, action-title sections, same-line source links, an automatically generated source appendix, and deterministic HTML. Use when the user asks for a final consulting report, executive answer, pyramid narrative, or report rendering from research 03–14 artifacts and falsify outputs.
license: CC-BY-4.0
metadata:
  author: Siyuan (AI·LAB)
  release: flagship
  component_version: "2.0.0"
---

# Report

Produce one narrative Markdown truth source. Treat HTML only as a deterministic rendering of that file.

## 1. Probe before writing

Read `references/report-contract.md` and `references/workflow.md`. Resolve one project root, then run:

```bash
python3 scripts/validate_report.py probe "/absolute/project-root"
```

Production mode requires all research 10–14 files, `verdict.md`, and `falsify/02-verdict.json`. Development fixtures may be supplied explicitly with `--verdict-md` and `--verdict-json`; never weaken the default probe.

Stop on any Critical finding, including a missing handoff file, invalid verdict, unresolved `[Data]` source, or source ID conflict. Do not repair or rewrite research artifacts.

## 2. Build the evidence map

1. Read research 03–08 JSON files.
2. Merge `artifacts.sources[]` by source ID and deduplicate by normalized URL.
3. Treat this merged catalog as the report source truth.
4. Use `research/12-sources.md` only for compatibility conflict checks.
5. Exclude every claim marked `falsified` in the verdict overlay.
6. Treat `survived` only as not overturned within the declared budget; never call it true.
7. Place every `unresolved` claim exclusively under Open Questions; it is Critical anywhere else.

## 3. Build the pyramid before writing prose

Write the governing thought in one sentence within the first three visible lines, immediately after the H1 title. Then define three to five mutually exclusive support arguments that collectively answer the governing thought. Group evidence under the argument it proves; never reproduce S1/S2/S3 order.

The report must contain:

- a first-screen governing thought and explicit answer;
- three to five `## 论点N｜完整判断句` sections;
- one or more `### 证据组N｜完整判断句` sections under every argument;
- evidence coverage for industry, business model, competition, user pain, opportunity, and product choice;
- Red Flags, Yellow Flags, and Open Questions after falsification;
- validation boundary and professional attachment entry points;
- a generated source appendix.

Every H2 and H3 heading must be an action title: a complete judgment that remains meaningful when read alone. Generic column headings such as `情境`, `冲突`, `问题`, `答案`, `背景`, `总结`, or `行业分析` are Critical findings. Follow the line and table syntax in `references/report-contract.md`. Every data conclusion and every evidence-bearing table row must show the source title and clickable original URL on the same line. Keep Chinese reader labels visible and machine labels in HTML comments.

Prefer decision density over a page target. Keep the full evidence chain when it changes confidence, action, or risk; remove repetition instead of imposing a fixed page count. Use 30x-style governing thought, action titles, and evidence grouping only as structural references—never import its content.

## 4. Generate the source appendix

Place the source markers under `## 来源附录`, then run:

```bash
python3 scripts/validate_report.py sources \
  "/absolute/project-root" "/absolute/report.md"
```

Do not hand-maintain the generated block.

## 5. Validate and render

```bash
python3 scripts/validate_report.py validate \
  "/absolute/project-root" "/absolute/report.md"

python3 scripts/validate_report.py render \
  "/absolute/report.md" "/absolute/report.html"
```

Fix every Critical finding before delivery. Re-run validation after every Markdown change. Re-render HTML instead of editing it.

## Never

- Never run without both human and machine verdict files in production.
- Never expose a falsified claim in the report body.
- Never cite only a source ID, footnote, or source-register pointer as the proof chain.
- Never create a separate HTML content version.
- Never modify research JSON schemas or write back to research artifacts.
- Never describe `survived` as proven true.
- Never use a generic column name as a section title.
- Never optimize the report to a fixed page count.
