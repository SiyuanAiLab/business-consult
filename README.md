# Business Consult Skills

A traceable business-research Skill pair built around claim-level honesty labels, a pre-search STOP CHECK, and source gates that keep evidence attached to the claims it supports.

## What is available

- `business-consult` routes work and maintains the shared progress contract.
- `business-consult-research` is the currently available analysis Skill for industry fundamentals, business models, competitive landscapes, user pains, opportunities, and product-system options.
- Every substantive claim is labeled `[Data]`, `[Estimate]`, `[Assumption]`, or `[Opinion]`.
- The workflow validates the research plan before search, each structured stage before synthesis, and the complete package before handoff.

## Install

```bash
npx skills add SiyuanAiLab/business-consult \
  --skill business-consult \
  --skill business-consult-research
```

## Quick use

Ask `business-consult` to route a business or industry question, or invoke
`business-consult-research` directly with a decision and scope. Choose one project
directory; the Skills keep all run state and outputs inside it.

The research Skill produces `PROGRESS.md` plus a fixed `research/` package from
`00-research-brief.md` through `14-validation-report.md`. See the complete
[aging-economy example](examples/aging-economy/) for a real proof chain.

## Roadmap

The reserved routes remain pending in this order:

1. `falsify` — adversarial testing of the research claims.
2. `report` — a defensible consulting narrative after falsification.
3. `diagnose` — question diagnosis and reframing.
4. `zh-data` — Chinese-platform and Chinese-company data collection.

The router will state that a pending route is unavailable; it does not simulate
undeveloped capabilities.

## Limitations

- This release produces defensible research estimates, not due diligence.
- Evidence quality depends on the sources available for the selected market and period.
- Low-confidence claims and unresolved contradictions remain visible as warnings or Open Questions.
- Optional business context is user-supplied. If omitted, the workflow records an explicit assumption and continues with general decision questions.

## Release

Snapshot version: `v1.0.0`. This public shell is a detached, generalized snapshot;
source-to-release correspondence is maintained in private release records outside
the repository.

## 中文说明

这是一组可追溯的商业咨询 Skill。母体 `business-consult` 负责路由和进度契约；当前可用的 `business-consult-research` 负责行业、商业模式、竞争格局、用户痛点、机会与产品体系调研。

工作流先写 Day-1 假设和幽灵大纲，再通过 STOP CHECK 才开始搜集证据；每个结构化阶段都单独校验，最后生成来源册、Claim Register、Open Questions 与验证报告。所有关键结论必须标记为数据、估算、假设或观点，避免把推断写成事实。

示例目录 `examples/aging-economy/` 展示从研究简报到最终验证报告的完整证明链。`falsify / report / diagnose / zh-data` 仍是 pending 路线，不会被伪装成已经可用的能力。

## License

CC BY 4.0. Copyright © 2026 Siyuan (AI·LAB).
