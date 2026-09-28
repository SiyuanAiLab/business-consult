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

Put one governing thought line immediately after the H1 title and within the first three visible lines:

```markdown
# 报告标题
> **建议判断**：**最高判断**：先做 A，因为 B，并以 C 作为停止线。 <!-- claims:S5-C001 --> <!-- [Opinion] -->
```

The body must contain three to five H2 support arguments:

```markdown
## 论点一｜客户已为结果型交付付费
### 证据组一｜陪跑客单与续费均高于纯内容
```

Every support argument needs at least one H3 evidence group. Evidence is grouped by the argument it proves, not by research stage.

Use action-title headings that contain these operational terms:

1. `执行摘要`
2. `Red Flags`
3. `Yellow Flags`
4. `Open Questions`
5. `验证边界`
6. `专业附件入口`
7. `来源附录`

Examples: `## Red Flags｜私域基数不足会先击穿小规模试点` and `## 来源附录｜全部原始链接均可零跳转复核`.

Every H2 and H3 must be a complete judgment sentence. A generic heading—including `情境`, `冲突`, `问题`, `答案`, `背景`, `总结`, `行业分析`, `竞争分析`, `用户痛点`, `机会分析`, or `产品选择`—is Critical whether used alone or as a colon-style prefix. The report must explicitly cover industry, business model, competition, user pain, opportunity, and product choice. Stage-number headings are forbidden.

There is no page-count target. Optimize for decision density, preserve evidence that changes confidence or action, and remove only duplication. Keep source links on the same line as the claim so the reader can open the original without jumping to an appendix.

## Language discipline（语言纪律）

The report's first reader is the decision maker and general users, not consultants. Structure, headings, reader/machine labels, and source lines are unchanged; these rules govern **vocabulary only**:

- **R1 No mixed-language jargon**: loanwords such as commoditize, harness, link-in-bio, kill criterion must be rewritten in plain Chinese. The hard-ban wordlist lives in `references/plain-language-words.txt` and is scanned by `validate` as warnings. Product names (SkillHub, Skill) and developer terms (API, JSON) are exempt.
- **R2 Terms: drop or translate**: prefer concrete numbers or facts over jargon (幂律/归因/证伪/生态税/围墙花园); when a term is unavoidable, attach one plain-language explanation on first use.
- **R3 Abstract mechanisms need concrete pictures**: 停止线/裁决点/降级/观察位/兜底 must state the trigger condition and the action taken.
- **R4 Project codenames**: a codename must carry a plain full name on first use (e.g. 「针 1：SkillHub 下载数自动抓取」); codenames may be used afterwards. Public-release versions prefer full names.
- **R5 Metaphors**: must be simpler and more accurate than the term they replace; they aid understanding and never substitute for argument.
- **R6 Coined concept words count as jargon**: self-invented nouns in titles and body (X 仪/X 链/X 弹头/X 位/X 并行 style) must be rewritten in plain language by default; if one must be kept as a name, attach a plain explanation on first use and keep it out of titles. Numbered codenames (针 1/O1/PS1) follow R4, not this rule.

Warnings from the jargon scan do not block delivery, but every warning must be resolved or justified in the `验证边界` section before delivery.

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
## 来源附录｜全部原始链接均可零跳转复核

<!-- REPORT:SOURCES:START -->
<!-- REPORT:SOURCES:END -->
```

`validate_report.py sources` replaces only the content between the markers using merged `artifacts.sources[]`. Markdown remains the sole content truth source.
