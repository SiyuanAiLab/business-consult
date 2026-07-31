---
name: business-consult-research
description: Conduct a traceable business or industry investigation from a diagnosis file or a standalone question. Use for industry fundamentals, business models, competitive landscapes, user journeys and pains, AI opportunity evaluation, or product-system architecture. Produces a fixed research directory with claim-level honesty labels, structured stage data, sources, open questions, and validation evidence.
metadata:
  status: active（2026-07-31 三轮定性验收闭环转正）
  validation_type: qualitative
  validation_loop_max: 3
author: Siyuan (AI·LAB)
license: CC-BY-4.0
release: flagship
---

# Research

Produce defensible estimates, not due diligence. Work standalone or consume `diagnosis.md`.

## Phase 0: Resume and probe

1. Read the cluster file contract if available; otherwise use the fixed paths in `references/workflow.md`.
2. Inspect `{project-root}/PROGRESS.md`.
3. Resume only when `skill: research`; stop on any other active owner.
4. Probe `{project-root}/diagnosis.md`.
5. Reuse its decision, scope, and research specification when present. Otherwise run the intake.
6. Read only the reference required by the current stage.

## Phase 1: Clarify

0. Context alignment first: ask whether the user wants to supply business context such as an operating model, decision principles, or constraints. If no context is supplied, write `[Assumption] No business context supplied` in the brief and continue with the general decision questions. If readable context is supplied, align the framing to it and record the provided file identifier plus its version or date. If the user explicitly supplies an unreadable path or mutually conflicting context documents, stop and request usable or reconciled input.
1. Read `references/question-chain.md`. Resolve the decision, audience, geography, period, subject boundary, known competitors, supplied numbers, and exclusions. Echo supplied numbers exactly.

Write `research/00-research-brief.md`. Mark unknowns as `[Assumption]`.

## Phase 2: Write both pre-search artifacts

Before collecting evidence:

1. Write `research/01-day1-hypothesis.md` as a falsifiable draft answer.
2. Write a provisional `research/09-ghost-outline.md` using conclusion-style headings.
3. Write `research/02-methodology-plan.json`.
4. Run the STOP CHECK:

```bash
python3 scripts/validate_research.py plan "/absolute/project-root"
```

Do not search until this command passes.

## Phase 3: Collect and analyze

Read `references/workflow.md` and execute in order:

1. S1 fundamentals
2. S2 business model
3. S2.5 quota-based landscape
4. S3 user journeys and pains
5. S4 opportunity evaluation
6. S5 product-system architecture
7. S6 synthesis

Before any executor, including a sub-agent, writes a stage JSON, read `references/stage.schema.json` and satisfy every required field. After writing each stage JSON, run:

```bash
python3 scripts/validate_research.py stage "/absolute/project-root/research/03-s1-foundations.json"
```

For each stage:

- Use the matching method reference.
- Use `references/query-syntax.md` for executable source queries.
- Write and validate the stage JSON before synthesis.
- Prefix every claim with one of `[Data]`, `[Estimate]`, `[Assumption]`, `[Opinion]`.
- Put source IDs on every `[Data]` claim.
- Separate collection evidence from analytical framework labels.
- Record sparse evidence as an Open Question; never fill a quota with weak duplicates.

## Phase 4: Apply the bounded repair loop

Score every stage from 1 to 10 on specificity, source independence, contradiction handling, and decision relevance.

- If score is greater than 7, continue.
- If score is 7 or lower, strengthen the best opposing explanation and revise.
- Run at most two repair rounds.
- After round two, move unresolved gaps to `research/13-open-questions.md`.

Never loop a third time.

## Phase 5: Synthesize

1. Revise `09-ghost-outline.md` after evidence collection.
2. Write `10-research-report.md` from the stage files, not from memory.
3. Merge atomic claims into `11-claim-register.json`.
4. Write `12-sources.md` with source tier, date, URL, and supported claim IDs.
5. Write `13-open-questions.md`; write `No open questions identified` with `[Opinion]` when empty.
6. Include Red Flags and Yellow Flags in the report even when none are found.

## Phase 6: Validate and hand off

Run:

```bash
python3 scripts/validate_research.py package "/absolute/project-root"
```

The validator writes `research/14-validation-report.md`. Fix all Critical findings. Run at most three qualitative validation iterations across the Skill build; keep remaining non-critical gaps visible.

Hand off only when the five-file falsify probe set exists and validation reports zero Critical findings.

## Reference index

| Reference | Read when |
|---|---|
| `references/question-chain.md` | intake and stage self-checks |
| `references/workflow.md` | stage execution and output paths |
| `references/query-syntax.md` | live evidence collection |
| `references/横纵分析法.md` | S1-S2 |
| `references/使用者旅程框架.md` | S3 |
| `references/AI价值评估矩阵.md` | S4 |
| `references/产品体系蓝图模板.md` | S5 |
