---
name: business-consult
description: Route a business question to the appropriate business-consult child Skill and maintain the shared project progress file. Use for industry entry, commercial opportunity, customer diagnosis, market research, adversarial validation, consulting reports, or Chinese-source research. Works as the cluster entry point; child Skills also work standalone.
metadata:
  status: active（2026-07-31 三轮定性验收闭环转正）
  validation_type: qualitative
  validation_loop_max: 3
author: Siyuan (AI·LAB)
license: CC-BY-4.0
release: flagship
---

# Business Consult

Route only. Do not perform a child's analysis inside this Skill.

## Phase 0: Resolve the project

1. Choose one explicit project root. Keep all child outputs inside it.
2. Read `references/contract.md`.
3. Inspect `{project-root}/PROGRESS.md`.
4. Resume only when its `skill` field matches the selected child.
5. If it belongs to another active child, do not overwrite it. Finish or hand off through the progress script.
6. If no progress file exists, initialize it:

```bash
python3 scripts/progress.py init \
  --project-root "/absolute/project-root" \
  --project "project-slug" \
  --skill "business-consult-research" \
  --mode "live"
```

## Route

| Child Skill | Status | Route when the user needs | Prior-work probe |
|---|---|---|---|
| `diagnose` | pending | Question diagnosis or problem reframing | none |
| `business-consult-research` | active | Industry, market, competition, user pain, opportunity, or product-system research | `diagnosis.md` |
| `falsify` | pending | Adversarial testing of claims | research handoff set in `references/contract.md` |
| `report` | pending | A defensible consulting narrative | `verdict.md` plus research handoff set |
| `zh-data` | pending | Chinese-platform or Chinese-company data collection | request from another child |

For a pending route, state that the route is reserved but unavailable in this build. Do not simulate an undeveloped child.

## Dispatch

For `business-consult-research`:

1. Probe `{project-root}/diagnosis.md`.
2. If found, pass its research specification to `$business-consult-research` and skip duplicate intake fields.
3. If absent, invoke `$business-consult-research` in standalone mode with the user's question.
4. Tell the user whether prior work was found.
5. Let `$business-consult-research` own its stage execution and files.

## Progress discipline

- Run `progress.py resume` before every child dispatch.
- Mark a stage complete immediately after its required output passes validation.
- Do not mark completion based on prose alone.
- Hand off only after the current skill is `completed`.
- Preserve notes and timestamps.

```bash
python3 scripts/progress.py resume --project-root "/absolute/project-root" --skill business-consult-research
python3 scripts/progress.py mark --project-root "/absolute/project-root" --skill business-consult-research --stage s1
python3 scripts/progress.py handoff --project-root "/absolute/project-root" --from-skill research --to-skill falsify
```

## Stop conditions

- Stop on a skill ownership mismatch.
- Stop when a required output exists but fails its schema or claim-label check.
- Stop before any route marked `pending`.
- Never write outside the selected project root during a run.
