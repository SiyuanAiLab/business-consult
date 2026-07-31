---
status: active
---

# Executable multi-source query syntax

Use search engines for discovery, then open the original source. Do not use result snippets as final evidence.

## Query variants

Generate two or three independent variants per information need:

```text
"{subject}" "{metric}" site:gov.cn
"{subject}" "{metric}" site:org.cn OR site:edu.cn
"{subject in English}" "{metric in English}" filetype:pdf
```

Use bilingual variants for Chinese-market research.

## Source-specific syntax

| Need | Query syntax | Preferred tier |
|---|---|---|
| regulation or official statistics | `"{topic}" site:gov.cn filetype:pdf` | T1/T2 |
| company product and pricing | `site:{official-domain} pricing OR 价格 OR 套餐` | T1 |
| company filings or announcements | `"{company}" 年报 OR 公告 site:cninfo.com.cn` | T1 |
| market study | `"{metric}" 研究报告 filetype:pdf` | T2 |
| practitioner pain | `"{role}" "{pain phrase}" site:zhihu.com` | T3 |
| product reviews | `"{product}" 评价 OR 投诉 OR 替代` | T3 |
| supply-side price | `"{product}" site:1688.com` | T3 lead |
| company registration lead | `"{company}" 企查查 OR 天眼查` | T3 lead |
| platform discussion | `"{topic}" site:xiaohongshu.com OR site:bilibili.com` | T3 lead |

Treat lead sources as discovery inputs until an original page or an independent source supports the claim.

## Cross-validation

For each load-bearing claim:

1. Find the original source.
2. Find one independent source using a different query wording and domain.
3. Check whether both pages ultimately cite the same upstream dataset.
4. If they do, count them as one source.
5. Record collection date and source tier.
6. If no independent source exists, label the conclusion `[Estimate]` or `[Assumption]`.

## Adversarial variants

For each leading conclusion, run at least two:

```text
"{claim subject}" failure OR criticism OR limitations
"{claim subject}" alternative OR substitute
"{claim subject}" disputed OR overstated
"{metric}" methodology problems
```

Do not use positive-only queries as a falsification attempt.

## Source tiers

- T1: official source, company-owned facts, filings, first-party pricing.
- T2: named research, government statistics, peer-reviewed or established institutions.
- T3: identifiable practitioner account, original review, or platform post.
- T4: SEO aggregator or unattributed summary.

Use T4 only as a lead. Price and product facts require T1. Market size and adoption require T2 or explicit downgrade. Pain requires T3 evidence or `[Assumption]`.

