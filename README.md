# Business Consult Skills

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) [![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/SiyuanAiLab/business-consult)

**Turn a business question into an auditable chain: one-question framing, traceable research, bounded falsification, and a report whose data claims link straight to their sources.**

Start with the real, inspectable research package in [`examples/aging-economy/`](examples/aging-economy/) before installing.

```bash
npx skills add SiyuanAiLab/business-consult
```

## 为什么需要它

商业调研最危险的不是答案不够长，而是三件事混在一起：问题边界没定、猜测写成事实、搜不到反证就当作结论成立。这个 Skill 簇把它们拆成可检查的四段，并用同一个项目目录保存状态和交接物。

真实运行顺序是：

```text
diagnose → research → falsify → report
```

## 五个可安装 Skill

| Skill | 当前能力 | 关键边界 |
|---|---|---|
| `business-consult` | 路由四段流程并维护 `PROGRESS.md` | owner 只使用 `diagnose / research / falsify / report` |
| `diagnose` | 每轮一个问题、会话可恢复、完成后交给 research | 这是外放交互壳；内部诊断方法细节未包含 |
| `business-consult-research` | 生成分阶段研究、声明册、来源册与验证报告 | 是可辩护的公开资料研究，不是尽职调查 |
| `falsify` | 搜索前冻结判据与预算，用三态输出独立裁决 | `survived` 只表示预算内未推翻，绝不等于真实 |
| `report` | 把 research 与裁决覆盖层写成咨询叙事 | 每条数据结论同一行显示来源标题与可点链接；来源附录从阶段 JSON 自动生成 |

## 它怎么证明自己

### 1. 问题与流程都能恢复

`diagnose/session.json` 保存待回答问题。没有用户回复就不能前进；完成态必须通过 validator（校验器，把文件和状态规则逐项核对的脚本），research 才接受交接。公开版只提供这套交互与状态骨架，不包含私有诊断细则。

### 2. 调研结论带身份

research 使用四类诚实标签：`[Data]`、`[Estimate]`、`[Assumption]`、`[Opinion]`。计划未通过 STOP CHECK 前不开始搜索；阶段文件和最终包分别校验。

### 3. 反证有上限，也有未决

falsify 在检索前冻结 claim 哈希、推翻判据、查询计划、来源预算和最多两轮上限。裁决只有 `falsified / survived / unresolved` 三态，并保留未覆盖范围与停止原因。

> 本次“未推翻”只代表在已声明范围内未找到足够反证，不代表该结论为真。

### 4. 报告不让读者来回找脚注

report 要求每条数据型结论和承重表格行在同一行给出来源标题与原始可点链接。来源附录不手抄，而是从 research 阶段 JSON 的 `artifacts.sources[]` 合并、校验并自动生成。

## 实证与局限：aging-economy

[`examples/aging-economy/`](examples/aging-economy/) 是一次中国银发经济的时间点研究包，包含 107 条登记声明和 57 个分级来源，可从研究简报追到声明册、来源册与验证报告。

它能证明的是：当前公开 research 副本可以保存完整结构、诚实标签和来源关系。它不能证明以下事情：

- 不是法律、财务或投资尽调；公开来源的覆盖度与可达性会随时间变化。
- repo 内没有把这份修正版 research 包包装成可复跑的完整四段演示。
- 一份历史裁决记录绑定了不同的 research 文件哈希；本版本没有改写预注册或伪造搜索来制造“全链已通过”。
- 因此这里的 00–14 研究文件不能被当作与某份未收录裁决逐字匹配的端到端证明。

## 安装与调用

一次安装会发现五个 Skill。也可以按名称调用：

```text
$diagnose
$business-consult-research
$falsify
$report
```

把 `business-consult` 当入口时，先选定一个项目目录。每个子 Skill 只在自己的 owner 状态下继续，并在交接前运行对应 validator。

research 仍支持独立调用。你可以提供自己的经营模型、决策原则或约束文档；不提供时，它记录 `[Assumption] No business context supplied` 后继续，不依赖私有目录。

## Roadmap

v1.1.0 当前包含 parent、research、diagnose shell、falsify 与 report。唯一 pending 路由是：

- `zh-data` — 中文平台与企业数据采集；当前不创建空壳或假实现。

维护采用单人、best-effort 模式，不承诺固定发布日期或响应时限。欢迎通过 issue 提交可复现问题和公开案例；外部使用见证目前留白，不编造评价。

## English summary

Version `v1.1.0` ships five installable Skills in a flat `skills/` layout. The public diagnose component is an interaction shell, research produces claim-level evidence artifacts, falsify applies preregistered bounded three-state adjudication, and report enforces same-line source-title links plus a JSON-generated source appendix. The bundled aging-economy example demonstrates the research layer only, with its evidence and historical-hash limitations stated above.

## License

CC BY 4.0 — attribution required. Copyright © 2026 Siyuan (AI·LAB).
