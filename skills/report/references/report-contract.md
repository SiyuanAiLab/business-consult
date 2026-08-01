# Report contract

## Inputs

Production input is one project root containing:

```text
research/03-s1-foundations.json
research/04-s2-business-model.json
research/05-s2.5-landscape.json
research/06-s3-user-pains.json
research/07-s4-opportunities.json
research/08-s5-product-architecture.json
research/10-research-report.md
research/11-claim-register.json
research/12-sources.md
research/13-open-questions.md
research/14-validation-report.md
verdict.md
falsify/02-verdict.json
```

Do not change any upstream file.

## Verdict overlay

`falsify/02-verdict.json` must contain `schema_version`, `project`, `generated_at`, and a `verdicts` array. Each verdict contains:

- `claim_id`: an existing research claim ID;
- `claim_hash`: lowercase SHA-256 of the exact research claim text;
- `status`: `falsified`, `survived`, or `unresolved`;
- `reason`: non-empty adjudication summary;
- `stop_reason`: required for `unresolved`.

`verdict.md` must mention every adjudicated claim ID and state: `本次“未推翻”只代表在已声明范围内未找到足够反证，不代表该结论为真。`

The overlay may cover only high-impact claims. An omitted claim is untested, not survived.

## Required report sections

Use headings that contain these terms:

1. `执行摘要`
2. `情境`
3. `冲突`
4. `问题`
5. `答案`
6. `Red Flags`
7. `Yellow Flags`
8. `Open Questions`
9. `验证边界`
10. `专业附件入口`
11. `来源附录`

The SCQA body must explicitly cover industry, business model, competition, user pain, opportunity, and product choice. Stage-number headings are forbidden.

## Claim syntax

Write visible Chinese labels and hidden machine labels on the same Markdown line:

```markdown
**事实依据**：65 岁以上人口占比上升。来源：[国家统计局《……》](https://example.com) <!-- claims:S1-C004 --> <!-- [Data] -->
**推算判断**：窗口期约 18 个月。推算逻辑：以平台工具迭代周期外推。数据前提：[平台公告](https://example.com) <!-- claims:S4-C003 --> <!-- [Estimate] -->
**待验证假设**：客户愿意单独为诊断付费。 <!-- claims:S3-C014 --> <!-- [Assumption] -->
**建议判断**：先验证诊断形态。 <!-- claims:S5-C001 --> <!-- [Opinion] -->
```

Rules:

- Every `[Data]`, `[Estimate]`, `[Assumption]`, and `[Opinion]` line in the business argument requires at least one existing claim in `<!-- claims:... -->`.
- Every mapped claim must have the same machine label as the report line. A claim with a different label cannot stand in for the line's argument.
- An `unresolved` claim may appear only under `Open Questions`. Its ID or exact claim text anywhere else is Critical, including the executive summary, SCQA, answer, and Red/Yellow Flags.
- The only no-claim exception is an `[Opinion]` line containing pure delivery metadata under `验证边界` or `专业附件入口`. The validator accepts only narrow validation-input/method metadata or a named attachment-entry line with an inline file path; decisions, product choices, market recommendations, and actions do not qualify.
- `[Data]` requires at least one exact catalog title plus original URL on the same line.
- `[Estimate]` requires `推算逻辑：` and a same-line link to its data premise.
- `[Assumption]` and `[Opinion]` need no external link, but any link used must resolve to the catalog.
- Do not use `[S105]`, `[^S105]`, or `见来源册` as the primary evidence chain.
- Every non-appendix table body row is evidence-bearing and follows the same rules.

## Source appendix markers

```markdown
## 来源附录

<!-- REPORT:SOURCES:START -->
<!-- REPORT:SOURCES:END -->
```

`validate_report.py sources` replaces only the content between the markers using merged `artifacts.sources[]`. Markdown remains the sole content truth source.
