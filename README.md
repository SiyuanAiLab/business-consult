# Business Consult Skills

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) [![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/SiyuanAiLab/business-consult)

**让 AI 做商业调研，每个结论都敢标明身份：这是数据、这是推算、这是没验证的、这是它的判断——编不出来的，它写「未知」。**

Turn a business question into an auditable chain: one-question framing, traceable research, bounded falsification, and a report whose data claims link straight to their sources.

Start with the real, inspectable research package in [`examples/aging-economy/`](examples/aging-economy/) before installing.

```bash
npx skills add SiyuanAiLab/business-consult
```

## 为什么需要它

让 AI 帮你做商业调研，真正危险的不是答案不够好，而是你根本不知道答案错在哪。三个病，每个都致命：

**病一：问题没定边界，报告已经写完了。** 你问「要不要做宠物经济」，AI 立刻给你一份行业分析。但你是想开店、做供应链，还是做内容号？这三件事的市场、对手、本钱完全不同。问题错了，报告越漂亮，错得越远——而且没人提醒你。`diagnose` 治这个病：先诊断你的问题，一轮只问一个，五道门过完才许开工。

**病二：猜测和事实长得一模一样。** AI 写「市场规模 5000 亿」，你抄进 BP 给投资人看。这个数字是有来源，还是它编的？你不知道，它也不说——因为没有任何机制逼它说。`research` 治这个病：每个结论强制标身份，有来源的标 `[Data]`，推理的标 `[Estimate]`，没验证的标 `[Assumption]`。编不出来的，它只能写「未知」。

**病三：搜不到反证，就当你是对的。** 你让 AI 验证你的创业想法，它找了一堆支持证据交差。但它找过反证吗？「没找到反对证据」和「这个想法成立」是两回事——前者只是没找够。`falsify` 治这个病：动手前先冻结「什么证据能推翻我」，最多两轮、预算花完就停，最后只给三种裁决——推翻、存活、未决。**「未推翻」绝不等于「是真的」**，这句话它写在每一份裁决上。

最后 `report` 把活下来的结论写成报告：每条数据型结论同一行带来源标题和可点链接，你不用翻附录找脚注。

真实运行顺序：

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

不让你信我们，让你自己验：

1. **读一份真实调研**：[`examples/aging-economy/`](examples/aging-economy/) 是一次完整的中国银发经济调研（时间快照），107 条声明逐条登记、57 个来源分级入册——从研究简报一路翻到验证报告
2. **抽查任何一条**：`11-claim-register.json` 里每条声明都有来源 id、置信度和推理说明；`12-sources.md` 里每个来源都有链接
3. **看我们的自我设限**：下面「实证与局限」一节，把这份示例做不到的三件事如实写出来

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
