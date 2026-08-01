---
name: report
description: Turn a completed business-consult research package and falsify verdict overlay into a defensible narrative Markdown report with same-line source links, reader-facing honesty labels, an automatically generated source appendix, and deterministic HTML. Use when the user asks for a final consulting report, executive answer, SCQA narrative, or report rendering from research 03–14 artifacts and falsify outputs.
license: CC-BY-4.0
metadata:
  author: Siyuan (AI·LAB)
  release: flagship
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

## 3. Write a narrative, not a stage dump

Use SCQA as the spine: situation, complication, question, answer. Integrate industry, business model, competition, user pain, opportunity, and product choice into the argument. Do not reproduce S1/S2/S3 order.

The report must contain:

- execution summary and explicit answer;
- SCQA narrative covering every required business dimension;
- Red Flags, Yellow Flags, and Open Questions after falsification;
- validation boundary and professional attachment entry points;
- a generated source appendix.

Follow the line and table syntax in `references/report-contract.md`. Every data conclusion and every evidence-bearing table row must show the source title and clickable original URL on the same line. Keep Chinese reader labels visible and machine labels in HTML comments.

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
