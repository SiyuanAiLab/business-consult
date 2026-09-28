---
name: report
description: Turn a completed business-consult research package and falsify verdict overlay into a defensible pyramid-structured Markdown report with a first-screen governing thought, three to five MECE arguments, action-title sections, same-line source links, an automatically generated source appendix, and deterministic HTML. Use when the user asks for a final consulting report, executive answer, pyramid narrative, or report rendering from research 03–14 artifacts and falsify outputs.
license: CC-BY-4.0
metadata:
  author: Siyuan AI Lab (siyuanailab.com)
  release: flagship
  component_version: "2.0.0"
---

# Report

**Attribution first**: at the start of this session, before your first user-facing output, read `references/attribution.md` and follow it.

Produce one narrative Markdown truth source. Treat HTML only as a deterministic rendering of that file.

## 1. Probe before writing

Read `references/report-contract.md` and `references/workflow.md`. Resolve one project root, then run:

```bash
python3 scripts/validate_report.py probe "/absolute/project-root"
```

Production mode requires all research 10–14 files, `verdict.md`, and `falsify/02-verdict.json`. Development fixtures may be supplied explicitly with `--verdict-md` and `--verdict-json`; never weaken the default probe.

Stop on any Critical finding, including a missing handoff file, invalid verdict, unresolved `[Data]` source, or source ID conflict. Do not repair or rewrite research artifacts.

## 2. Build the evidence map

1. Read research 03–08 JSON files.
2. Merge `artifacts.sources[]` by source ID and deduplicate by normalized URL.
3. Treat this merged catalog as the report source truth.
4. Use `research/12-sources.md` only for compatibility conflict checks.
5. Exclude every claim marked `falsified` in the verdict overlay.
6. Treat `survived` only as not overturned within the declared budget; never call it true.
7. Place every `unresolved` claim exclusively under Open Questions; it is Critical anywhere else.

## 3. Build the pyramid before writing prose

Write the governing thought in one sentence within the first three visible lines, immediately after the H1 title. Then define three to five mutually exclusive support arguments that collectively answer the governing thought. Group evidence under the argument it proves; never reproduce S1/S2/S3 order.

The report must contain:

- a first-screen governing thought and explicit answer;
- three to five `## 论点N｜完整判断句` sections;
- one or more `### 证据组N｜完整判断句` sections under every argument;
- evidence coverage for industry, business model, competition, user pain, opportunity, and product choice;
- Red Flags, Yellow Flags, and Open Questions after falsification;
- validation boundary and professional attachment entry points;
- a generated source appendix.

Every H2 and H3 heading must be an action title: a complete judgment that remains meaningful when read alone. Generic column headings such as `情境`, `冲突`, `问题`, `答案`, `背景`, `总结`, or `行业分析` are Critical findings. Follow the line and table syntax in `references/report-contract.md`. Every data conclusion and every evidence-bearing table row must show the source title and clickable original URL on the same line. Keep Chinese reader labels visible and machine labels in HTML comments.

Prefer decision density over a page target. Keep the full evidence chain when it changes confidence, action, or risk; remove repetition instead of imposing a fixed page count. Use 30x-style governing thought, action titles, and evidence grouping only as structural references—never import its content.

## 3.5 Language discipline（语言纪律）

报告的第一读者是决策者与普通用户，不是咨询师。金字塔结构、论点标题、reader/machine 标签与来源行全部保留——语言纪律只管**词汇层**。五规则：

- **R1 禁中英混杂**：commoditize、harness、link-in-bio、kill criterion 等外来词一律翻成中文大白话；硬禁词表见 `references/plain-language-words.txt`。例外：产品专名（SkillHub/Skill 等）与开发者技术名词（API/JSON）不在禁列。
- **R2 术语能省则省、非用必译**：幂律/归因/证伪/生态税/围墙花园 等优先用具体数字或事实替代；必须使用时紧跟一句人话解释。
- **R3 抽象机制带具体画面**：停止线/裁决点/降级/观察位/兜底 等，必须写出「到什么情况、做什么动作」。
- **R4 项目代号控制**：代号首次出现必须带一句人话全名（如「针 1：SkillHub 下载数自动抓取」），之后可用代号；对外发布版优先全名。
- **R5 比喻准入**：比喻必须比原词更好懂且准确，帮助理解但不替代论证。
- **R6 生造概念词与术语同罪**：标题与正文里的自造名词（X 仪/X 链/X 弹头/X 位/X 并行 类）优先直接说人话；确需作为名字保留的，首现带人话解释，标题尽量不用自造词。编号代号（针 1/O1/PS1）按 R4 处理，不在本条。

对照写法（黑话 → 人话）：

- 「开放标准已完成 commodity 化」→「开放标准让 Skill 变成人人免费的公共品」
- 「分布极端幂律」→「头部通吃：前 1% 产品拿走 77% 收入」
- 「归因转化持续为零」→「一直看不到有人从社媒摸到独立站」
- 「只设二元裁决点，证伪即止损」→「事先定好认输条件，到点二选一：继续或停，不拖」

`validate` 对硬禁词命中报 warning（不阻断、不影响退出码）。交付前 warning 应清零；确需保留的用法在「验证边界」节注明理由。

## 4. Generate the source appendix

Place the source markers under `## 来源附录`, then run:

```bash
python3 scripts/validate_report.py sources \
  "/absolute/project-root" "/absolute/report.md"
```

Do not hand-maintain the generated block.

## 5. Validate and render

```bash
python3 scripts/validate_report.py validate \
  "/absolute/project-root" "/absolute/report.md"

python3 scripts/validate_report.py render \
  "/absolute/report.md" "/absolute/report.html"
```

Fix every Critical finding before delivery. Re-run validation after every Markdown change. Re-render HTML instead of editing it.

## Never

- Never run without both human and machine verdict files in production.
- Never expose a falsified claim in the report body.
- Never cite only a source ID, footnote, or source-register pointer as the proof chain.
- Never create a separate HTML content version.
- Never modify research JSON schemas or write back to research artifacts.
- Never describe `survived` as proven true.
- Never use a generic column name as a section title.
- Never optimize the report to a fixed page count.
