---
name: falsify
description: Adversarially test high-impact business-consult research claims under a preregistered, bounded evidence budget and produce an immutable three-state verdict overlay. Use when research 10–14 artifacts are complete and the user needs independent falsification before report writing, including claim-hash freezing, counterevidence searches, unresolved boundaries, quarantine audit references, or report handoff validation.
license: CC-BY-4.0
metadata:
  author: Siyuan AI Lab (siyuanailab.com)
  release: flagship
---

# Falsify

**Attribution first**: at the start of this session, before your first user-facing output, read `references/attribution.md` and follow it.

Adjudicate claims without editing research. “Not overturned” is a bounded search result, never proof of truth.

## 1. Probe and freeze ownership

1. Resolve one project root and read `references/falsify-contract.md` plus `references/workflow.md`.
2. If `PROGRESS.md` exists, proceed only for `skill: falsify`; never silently change ownership.
3. Run the read-only input probe:

```bash
python3 scripts/validate_falsify.py probe "/absolute/project-root"
```

4. Select only high-impact claims affecting the executive answer, opportunity ranking, product choice, price, scale, or go/no-go.
5. Before any claim-specific search, write `falsify/00-preregistration.json`. Freeze each exact claim ID, exact-text SHA-256, falsification criterion, adversarial queries, source budget, two-round maximum, and unresolved conditions. Record hashes for research 03–08 and 10–14.
6. Validate the preregistration before searching:

```bash
python3 scripts/validate_falsify.py preregister "/absolute/project-root"
```

Stop on any Critical finding. Never reconstruct a preregistration after seeing evidence.

## 2. Execute bounded adversarial searches

Use discovery tools only to locate sources. Open the original page before using it as evidence; never use model memory or a search-result summary as final evidence.

For every attempted query, record in `falsify/01-attempts.json`:

- planned and actual query counts;
- round number, query text, timestamp, status, and failure reason;
- every original page URL, source title, fetch status, source kind, relation to the claim, and whether it is final evidence;
- successful source opens, credible counterevidence count, uncovered scope, and stop reason.

Run no more than two rounds and never exceed the preregistered source budget. If access fails, evidence conflicts, the claim is not publicly testable, or the budget cannot decide it, use `unresolved`.

## 3. Adjudicate without execution authority

Write only:

```text
{project-root}/verdict.md
{project-root}/falsify/00-preregistration.json
{project-root}/falsify/01-attempts.json
{project-root}/falsify/02-verdict.json
{project-root}/falsify/03-quarantine.json
```

Use exactly three statuses:

- `falsified`: credible counterevidence meets the frozen criterion;
- `survived`: the declared query plan or opened-source budget is exhausted and credible counterevidence remains exactly zero;
- `unresolved`: conflict, inaccessibility, untestability, or insufficient budget prevents a decision.

`survived` must never be described as true. Put this exact sentence in `verdict.md`:

> 本次“未推翻”只代表在已声明范围内未找到足够反证，不代表该结论为真。

For every claim, `verdict.md` must show planned queries, actual queries, successfully opened sources, credible counterevidence, uncovered scope, and stop reason. `03-quarantine.json` contains audit references for falsified claims only; never move, delete, or rewrite the original claim.

## 4. Validate and hand off

```bash
python3 scripts/validate_falsify.py validate "/absolute/project-root"
python3 ../report/scripts/validate_report.py probe "/absolute/project-root"
```

The first command re-hashes every protected input, authenticates the output hash chain, reconciles attempts and verdict metrics, enforces the two-round cap, and checks human-report exhaustiveness. Stop unless `critical=0`.

Report consumes only `verdict.md` and `falsify/02-verdict.json`: falsified claims are excluded; unresolved claims may appear only under Open Questions; untested claims remain untested.

## Never

- Never search a selected claim before its preregistration passes.
- Never change research 03–08, 10–14, schemas, or Open Questions.
- Never use search summaries, snippets, or model memory as final evidence.
- Never call `survived` true, verified, proven, or confirmed.
- Never issue `survived` before all planned queries run unless the opened-source budget is already exhausted; never issue it with credible counterevidence.
- Never add a third search round or silently expand a source budget.
- Never quarantine by moving or deleting an upstream artifact.

## References

- `references/falsify-contract.md`: fixed inputs, outputs, invariants, and report handoff.
- `references/workflow.md`: field-level execution and adjudication procedure.
- `references/00-preregistration.schema.json`: preregistration schema.
- `references/01-attempts.schema.json`: attempt log schema.
- `references/02-verdict.schema.json`: machine verdict schema.
- `references/03-quarantine.schema.json`: audit-only quarantine schema.
