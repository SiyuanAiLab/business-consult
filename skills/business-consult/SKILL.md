---
name: business-consult
description: Route a business question to the appropriate business-consult child Skill and maintain the shared project progress file. Use for industry entry, commercial opportunity, customer diagnosis, market research, adversarial validation, consulting reports, or Chinese-source research. Works as the cluster entry point; child Skills also work standalone.
metadata:
  status: active（2026-07-31 三轮定性验收闭环转正）
  validation_type: qualitative
  validation_loop_max: 3
  author: Siyuan (AI·LAB)
  release: flagship
license: CC-BY-4.0
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
  --skill "diagnose" \
  --mode "live"
```

## Route

| Child Skill | Status | Route when the user needs | Prior-work probe |
|---|---|---|---|
| `diagnose` | active shell | One-question-at-a-time problem framing | `diagnosis.md` + `diagnose/session.json` |
| `business-consult-research` | active | Industry, market, competition, user pain, opportunity, or product-system research | accepted diagnose handoff or standalone intake |
| `falsify` | active | Adversarial testing of claims | fixed research handoff set in `references/contract.md` |
| `report` | active | A defensible consulting narrative | validated verdict plus research handoff set |
| `zh-data` | pending | Chinese-platform or Chinese-company data collection | request from another child |

For a pending route, state that the route is reserved but unavailable in this build. Do not simulate an undeveloped child.

## Dispatch

For `diagnose`:

1. Initialize or resume `PROGRESS.md` only with owner `diagnose`.
2. Invoke `$diagnose`; it asks exactly one question, persists the session, and stops for the reply.
3. Keep ownership with `diagnose` until the public-shell validator accepts completion:

```bash
python3 ../diagnose/scripts/validate_diagnose.py completed "/absolute/project-root"
python3 ../diagnose/scripts/validate_diagnose.py research-probe "/absolute/project-root"
```

4. Hand off only when the probe emits `handoff: accepted` and `skip_duplicate_intake: true`.

For `business-consult-research`:

1. Resume only when `PROGRESS.md` is owned by `research`.
2. Probe `{project-root}/diagnosis.md` and `{project-root}/diagnose/session.json` as one pair.
3. If either exists, run the public diagnose `research-probe`; stop on a missing pair, in-progress state, invalid state, or any payload other than `handoff: accepted`.
4. Pass only the accepted payload to `$business-consult-research` and skip duplicate intake fields.
5. If neither diagnose output exists, invoke `$business-consult-research` in standalone mode.

For `falsify`:

1. Resume only when `PROGRESS.md` is owned by `falsify`.
2. Run `python3 ../falsify/scripts/validate_falsify.py probe "/absolute/project-root"`.
3. Invoke `$falsify` only after the fixed research input set passes.
4. Run the `validate` command before handing off to `report`.

For `report`:

1. Resume only when `PROGRESS.md` is owned by `report`.
2. Run `python3 ../report/scripts/validate_report.py probe "/absolute/project-root"` without fixture overrides.
3. Invoke `$report` only after both verdict inputs and every required research input pass.

## Progress discipline

- Run `progress.py resume` before every child dispatch.
- Mark a stage complete immediately after its required output passes validation.
- Do not mark completion based on prose alone.
- Hand off only after the current skill is `completed`.
- Preserve notes and timestamps.

```bash
python3 scripts/progress.py resume --project-root "/absolute/project-root" --skill research
python3 scripts/progress.py mark --project-root "/absolute/project-root" --skill research --stage s1
python3 scripts/progress.py handoff --project-root "/absolute/project-root" --from-skill research --to-skill falsify
```

## Stop conditions

- Stop on a skill ownership mismatch.
- Stop when a required output exists but fails its schema or claim-label check.
- Stop before any route marked `pending`.
- Never write outside the selected project root during a run.
