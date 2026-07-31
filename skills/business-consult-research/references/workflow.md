---
status: active
---

# Research workflow and output contract

## Fixed files

Write exactly these files under `{project-root}/research/`:

```text
00-research-brief.md
01-day1-hypothesis.md
02-methodology-plan.json
03-s1-foundations.json
04-s2-business-model.json
05-s2.5-landscape.json
06-s3-user-pains.json
07-s4-opportunities.json
08-s5-product-architecture.json
09-ghost-outline.md
10-research-report.md
11-claim-register.json
12-sources.md
13-open-questions.md
14-validation-report.md
```

## Common stage record

Every stage JSON must contain:

```json
{
  "schema_version": "1.0",
  "stage": "s1",
  "subject": "example",
  "generated_at": "ISO-8601 timestamp",
  "revision_round": 0,
  "score": 8,
  "claims": [
    {
      "id": "S1-C001",
      "category": "current-state",
      "claim": "Atomic claim text",
      "label": "[Data]",
      "confidence": "medium",
      "source_ids": ["S001"],
      "reasoning": ""
    }
  ],
  "artifacts": {}
}
```

Use one claim per observable or inferential statement. Keep `revision_round` between 0 and 2.

## S1: Fundamentals

Read `横纵分析法.md` and collect:

- origin and formation
- 3-5 evolution stages
- turning points
- current stage and tensions
- 1-2 year visible trends

Write `03-s1-foundations.json`. Self-check the chronology and flag stale evidence.

Before saving, run `python3 scripts/validate_research.py stage "{project-root}/research/03-s1-foundations.json"`.

## S2: Business model

Read `横纵分析法.md` and analyze:

- representative players across head, middle, and long tail
- business-model topology
- upstream, midstream, and downstream value chain
- profit cores and cost cores
- four horizontal-vertical cross judgments

Write `04-s2-business-model.json`. Do not treat market prominence as profitability.

Before saving, run `python3 scripts/validate_research.py stage "{project-root}/research/04-s2-business-model.json"`.

## S2.5: Quota-based landscape

Write a quota plan before discovery. Default standard depth:

| Category | Target |
|---|---:|
| direct competitors | 5 |
| substitutes and manual workflows | 4 |
| upstream/downstream ecosystem actors | 4 |
| cross-industry benchmarks | 3 |

Put `quota_plan` and `candidates` in `artifacts`. Each candidate must include category, role, URL, evidence state, and supported claim IDs.

If a category is under quota, add a specific `gap` instead of padding with famous names or duplicate sources.

Write `05-s2.5-landscape.json`.

Before saving, run `python3 scripts/validate_research.py stage "{project-root}/research/05-s2.5-landscape.json"`.

## S3: User journeys and pains

Read `使用者旅程框架.md` and produce:

- role-by-stage matrix
- 5-7 step journey per priority role
- pain candidates meeting at least two pain tests
- pain scores for frequency, impact, and current resolution cost
- verbatim practitioner evidence when available

Write `06-s3-user-pains.json`. Mark unsupported pain points `[Assumption]`.

Before saving, run `python3 scripts/validate_research.py stage "{project-root}/research/06-s3-user-pains.json"`.

## S4: Opportunity evaluation

Read `AI价值评估矩阵.md` and assess:

- output form and feasible AI intervention
- required knowledge, context, and tools
- current comparable products
- technical maturity
- defensibility and adoption friction
- expected time or cost change

Write `07-s4-opportunities.json`. Express unsupported numeric savings as `[Estimate]` with reasoning.

Before saving, run `python3 scripts/validate_research.py stage "{project-root}/research/07-s4-opportunities.json"`.

## S5: Product-system architecture

Read `产品体系蓝图模板.md` and design the top one to three evidence-backed opportunities across:

- scenario
- knowledge
- context
- capability modules
- six-week validation path
- risks and reusable fallback assets

Write `08-s5-product-architecture.json`. Do not convert a research gap into a product requirement.

Before saving, run `python3 scripts/validate_research.py stage "{project-root}/research/08-s5-product-architecture.json"`.

## S6: Synthesis

Update the ghost outline and write the report from stage files.

The report must include:

- executive answer
- industry anatomy
- business and value-chain map
- quota-based competition landscape
- user pains
- opportunity evaluation
- product-system options
- Red Flags
- Yellow Flags
- Open Questions

Use a heading for structure. Write every substantive Markdown line as:

```markdown
- [Data] Claim with source IDs [S001][S004].
- [Estimate] Inference and explicit reasoning.
- [Assumption] Testable unknown.
- [Opinion] Recommendation or interpretation.
```

Tables must use the honesty tag as the first column.

Write `12-sources.md` using this table contract:

```markdown
| Label | ID | Tier | Source | Collected | URL | Supported claims |
|---|---|---|---|---|---|---|
| [Data] | S001 | T1 | Example source | 2026-07-31 | https://example.com | S1-C001 |
```

Keep the source ID in the first or second column. The validator also accepts `S001:` and `- S001 | ...` list records when merging collector notes.

Before synthesis, run the stage validator on all six stage JSON files. S6 has no separate stage JSON.

## Falsify handoff

The next child probes:

- `10-research-report.md`
- `11-claim-register.json`
- `12-sources.md`
- `13-open-questions.md`
- `14-validation-report.md`
