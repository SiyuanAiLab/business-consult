---
status: active
---

# business-consult file contract

Use one project root per consulting question. Treat these names as APIs: do not rename them inside a run.

## Shared root

```text
{project-root}/
├── PROGRESS.md
├── diagnosis.md                  # optional upstream input
├── research/                     # research output
└── verdict.md                    # reserved for falsify
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

Valid `skill` values are `diagnose`, `research`, `falsify`, `report`, and `zh-data`.

Rules:

- Resume only when `skill` matches the child being invoked.
- Reject silent ownership changes.
- Permit handoff only when the current owner is `completed`.
- Keep a checklist for every stage; the first unchecked item is the resume point.

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

`falsify` may start from research only when all five files exist:

- `research/10-research-report.md`
- `research/11-claim-register.json`
- `research/12-sources.md`
- `research/13-open-questions.md`
- `research/14-validation-report.md`

If any file is missing, run `falsify` standalone or return to `research`; never infer the missing artifact.

## Report handoff probe

`report` should prefer:

- `verdict.md`
- the complete falsify handoff set above

When `verdict.md` is absent, `report` remains unavailable in this build rather than treating unverified research as a final consulting conclusion.

