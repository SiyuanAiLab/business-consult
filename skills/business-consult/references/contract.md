---
status: active
---

# business-consult file contract

Use one project root per consulting question. Treat these names as APIs: do not rename them inside a run.

## Shared root

```text
{project-root}/
├── PROGRESS.md
├── diagnosis.md                  # optional public-shell diagnose output
├── diagnose/
│   └── session.json              # optional resumable state; paired with diagnosis
├── research/                     # research output
├── verdict.md                    # human falsify verdict
├── falsify/
│   ├── 00-preregistration.json
│   ├── 01-attempts.json
│   ├── 02-verdict.json
│   └── 03-quarantine.json
├── report.md                     # report content truth source
└── report.html                   # optional deterministic derivative
```

## Progress ownership

`PROGRESS.md` must contain:

```yaml
project: project-slug
skill: research
status: in_progress
mode: live
current_stage: s2
updated_at: 2026-07-31T12:00:00+08:00
```

Valid `skill` values are `diagnose`, `research`, `falsify`, and `report`. The pending `zh-data` route is not a progress owner in this release.

Rules:

- Resume only when `skill` matches the child being invoked.
- Reject silent ownership changes.
- Permit handoff only when the current owner is `completed`.
- Keep a checklist for every stage; the first unchecked item is the resume point.

## Diagnose outputs and research handoff

`diagnose` owns exactly `diagnosis.md` and `diagnose/session.json`. If either exists, both are required. The public shell guarantees one question per interaction, a recoverable pending question, response-gated advancement, and a validated completed handoff. It intentionally does not contain the private diagnostic method.

Before handoff, run:

```bash
python3 ../diagnose/scripts/validate_diagnose.py completed {project-root}
python3 ../diagnose/scripts/validate_diagnose.py research-probe {project-root}
```

Both commands must exit zero, and the probe must emit `handoff: accepted` plus `skip_duplicate_intake: true`. Research rejects partial or invalid state. When neither diagnose output exists, research may run standalone intake.

## Research files

`research` owns this fixed set:

```text
research/
├── 00-research-brief.md
├── 01-day1-hypothesis.md
├── 02-methodology-plan.json
├── 03-s1-foundations.json
├── 04-s2-business-model.json
├── 05-s2.5-landscape.json
├── 06-s3-user-pains.json
├── 07-s4-opportunities.json
├── 08-s5-product-architecture.json
├── 09-ghost-outline.md
├── 10-research-report.md
├── 11-claim-register.json
├── 12-sources.md
├── 13-open-questions.md
└── 14-validation-report.md
```

## Falsify handoff probe

`falsify` may start from research only when all eleven immutable inputs exist:

- `research/03-s1-foundations.json`
- `research/04-s2-business-model.json`
- `research/05-s2.5-landscape.json`
- `research/06-s3-user-pains.json`
- `research/07-s4-opportunities.json`
- `research/08-s5-product-architecture.json`
- `research/10-research-report.md`
- `research/11-claim-register.json`
- `research/12-sources.md`
- `research/13-open-questions.md`
- `research/14-validation-report.md`

Run `python3 ../falsify/scripts/validate_falsify.py probe {project-root}`. If any file is missing or invalid, return to `research`; never infer a missing artifact or mutate an upstream file.

## Falsify outputs

`falsify` owns exactly `verdict.md` plus `falsify/00-preregistration.json` through `03-quarantine.json`. Run `python3 ../falsify/scripts/validate_falsify.py validate {project-root}` before handoff. Quarantine is audit-only and never moves, deletes, or rewrites research.

## Report handoff probe

`report` production input is fixed and requires:

- `research/03-s1-foundations.json`
- `research/04-s2-business-model.json`
- `research/05-s2.5-landscape.json`
- `research/06-s3-user-pains.json`
- `research/07-s4-opportunities.json`
- `research/08-s5-product-architecture.json`
- `research/10-research-report.md`
- `research/11-claim-register.json`
- `research/12-sources.md`
- `research/13-open-questions.md`
- `research/14-validation-report.md`
- `verdict.md`
- `falsify/02-verdict.json`

Run `python3 ../report/scripts/validate_report.py probe {project-root}`. If a verdict or research input is absent or invalid, stop. `report.md` remains the content truth source; `report.html` is only its deterministic derivative.
