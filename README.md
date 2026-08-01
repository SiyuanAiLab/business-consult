# Business Consult Skills

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) [![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/SiyuanAiLab/business-consult)

**AI-written business research you can actually audit: every claim carries an honesty label, every number carries a source, and the search doesn't start until the methodology passes a STOP CHECK.**

A Skill pair for Claude (and compatible agents): `business-consult` routes; `business-consult-research` investigates. The proof is in [`examples/aging-economy/`](examples/aging-economy/) — a complete, real research run on China's silver economy, from brief to validation report.

**Install**: `npx skills add SiyuanAiLab/business-consult`

---

## 为什么需要它

让 AI 做行业调研，最大的问题是它会把猜测写得像事实。这个 Skill 的核心承诺只有一条：**每条结论都标身份**——`[Data]` 有来源直接支持、`[Estimate]` 有明确推理链、`[Assumption]` 是没验证的、`[Opinion]` 是解读。编不出来的，它写「未知」，不写漂亮话。

## 先看产物，再决定装不装

`examples/aging-economy/` 是一次完整的真实调研（中国银发经济：独立创业者该不该进入），15 个文件从研究简报到验证报告全在。报告里的几个发现：

- **[Data] 市场规模比舆论小近一倍**：政策口径「银发经济 7 万亿」，实际老年消费潜力测算约 4.37 万亿——两个数字都有来源，口径分层本身就是结论
- **[Data] 最赚钱的银发公司正在逃离**：毛利率 85%、年净利 3.57 亿的头部玩家，收入 -28%，转型去做潮玩了
- **[Data] 监管已经重锤快钱模型**：市监总局专项整治查办 4516 件、罚没 6876.91 万元
- **[Opinion] 可执行的进入姿势**：报告没有停在「市场很大」，而是收敛到两个 10-50 万资金可验证的具体切口，含六周验证路径和冻结判据

107 条声明逐条登记（`11-claim-register.json`），57 个来源分级入册（`12-sources.md`）。你可以抽查任何一条。

> 我们用这个 Skill 调研自己的商业决策（这就是我们的日常工具）。外部使用见证位留白——你用了觉得好或不好，欢迎开 issue 告诉我们，真实的反馈会出现在这里。

## 它怎么工作

1. **先写答案再搜证**：Day-1 假设 + 幽灵提纲双前置，搜证前冻结判断，之后对照证据标注「证实/修正/推翻」
2. **方法论闸门**：调研计划不过 schema 校验（STOP CHECK），不许开始搜索
3. **分阶段结构化**：行业基本面 → 商业模式 → 配额式竞争格局 → 用户痛点 → 机会评估 → 产品体系，每个阶段单独产出、单独校验
4. **诚实标签贯穿**：从阶段 JSON 到最终报告，标签不落一行
5. **断点续跑**：`PROGRESS.md` 记录归属与进度，中断可续，多项目不串线

## 安装

```bash
npx skills add SiyuanAiLab/business-consult
```

## 使用

把 `business-consult` 当入口，直接向它抛一个商业问题；或者单独调用 `business-consult-research`，给它一个决策和范围。选定一个项目目录，所有运行状态和产物都只写进这个目录。

可选：挂入你自己的经营模型文档作为对齐过滤器（比如你的定价纪律、你的渠道约束），调研会按你的框架框题；不挂也能跑，它会标注 `[Assumption]` 并继续。

## 路线图

当前可用：`business-consult-research`。规划中（路由会如实声明不可用，不伪装）：

1. `falsify` — 对调研声明做对抗性证伪
2. `report` — 证伪后生成可辩护的咨询叙事
3. `diagnose` — 问题诊断与重构（先问「你问的对不对」）
4. `zh-data` — 中文平台与企业数据采集

## 诚实的边界

- 产出是**可辩护的调研估计**，不是尽职调查
- 证据质量取决于所选市场与时期的公开来源质量
- 低置信声明与未解决矛盾不会被抹掉，会作为警告和 Open Questions 留在产物里

## 维护状态

AI·LAB 单人维护，我们自己天天在用（internal-first）。issue 会在一周内响应；路线图四件按 falsify → report → diagnose → zh-data 推进，不设假日期。

## What you get (English)

- `business-consult` — router + shared progress contract
- `business-consult-research` — the analysis Skill: fundamentals, business models, landscape, user pains, opportunities, product-system options
- Claim-level honesty labels (`[Data]` / `[Estimate]` / `[Assumption]` / `[Opinion]`), a pre-search STOP CHECK, per-stage schema validation, quota-based landscape scan, Day-1 hypothesis with pre-registered falsification criteria, and a full source register
- A complete worked example in `examples/aging-economy/`

Snapshot version: `v1.0.0`.

## License

CC BY 4.0 — 署名即可商用。Copyright © 2026 Siyuan (AI·LAB).
