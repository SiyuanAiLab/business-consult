# Report workflow

## 1. Probe

Run `validate_report.py probe`. Stop on non-zero exit. In development only, pass the approved fixture paths explicitly:

```bash
python3 scripts/validate_report.py probe PROJECT_ROOT \
  --verdict-md FIXTURE/verdict.md \
  --verdict-json FIXTURE/falsify/02-verdict.json
```

The probe verifies the research handoff, merges all stage source catalogs, checks claim-to-source resolution, compares the compatibility source register, and authenticates the verdict overlay against exact claim hashes.

## 2. Plan the pyramid

Create a dot-dash argument map before prose:

- one governing thought that states the answer, reason, and decision boundary;
- three to five MECE support arguments;
- one or more evidence groups under each argument;
- rejected alternatives and action thresholds inside the argument they affect;
- red/yellow flags and open questions.

Draft and read only the action titles first. They must form a coherent answer without body text. Then map every `[Data]`, `[Estimate]`, `[Assumption]`, and `[Opinion]` argument line to one or more existing, same-label claim IDs. Drop falsified claims before drafting. Put every unresolved claim exclusively under Open Questions; do not use it in summaries, arguments, answers, or flags.

Only pure delivery metadata under `验证边界` or `专业附件入口` may omit a claim. Keep this exception to validation inputs/methods and explicit attachment paths; never place a decision, recommendation, product choice, or action inside it.

## 3. Draft Markdown

Use the syntax in `report-contract.md`. Cite one to three load-bearing sources on the same line, preferring T1. A source title and URL must come from the merged stage catalog; do not copy them from `12-sources.md`.

Keep the report narrative. Group evidence by the conclusion it supports. Do not concatenate stage summaries or name sections after S1–S5. Do not target a fixed page count; optimize for decision density and retain evidence that changes confidence, risk, or action.

## 4. Generate the appendix

Add the two source markers and run the `sources` command. Re-run it after upstream source changes. The command merges by ID, deduplicates by normalized URL, sorts deterministically, and atomically replaces the generated block.

## 5. Validate

Run `validate`. It checks:

- a governing thought within the first three visible lines;
- three to five support arguments and evidence groups;
- action-title H2/H3 headings, with generic column headings blocked as Critical;
- required operational sections and business dimensions;
- reader/machine label pairing;
- claim mapping for all four substantive labels and claim-label consistency;
- same-line source title and original link;
- estimate reasoning and data premise;
- evidence-bearing table rows;
- falsified claim leakage;
- unresolved claims outside Open Questions;
- exact generated source appendix;
- compatibility source conflicts.

Fix all Critical findings. Warnings remain visible in the delivery boundary.

## 6. Render HTML

Run `render` only after Markdown validation passes. The renderer uses no network calls, removes hidden machine tags, turns Chinese reader labels into subdued badges, and embeds the Markdown SHA-256. Re-render after every Markdown change; never edit HTML.
