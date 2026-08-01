# Falsify workflow

## 1. Select claims

Read the research report, claim register, sources, open questions, and validation report. Prefer claims that materially change the executive answer, opportunity order, product choice, price, scale, or go/no-go. Do not treat an omitted claim as survived.

## 2. Preregister

For each selected claim:

1. Copy the exact claim text and compute its lowercase SHA-256.
2. State one observable falsification criterion.
3. Plan specific opposing queries, assigned to round 1 or round 2.
4. Set `max_opened_sources` and `max_rounds` no greater than two.
5. State conditions that force `unresolved`.
6. Count planned queries from the plan, not by hand.

Record every protected input hash, then run the preregistration validator. Search only after it passes.

## 3. Search adversarially

Execute only preregistered queries. Round 2 may refine the attack but cannot introduce an unregistered query. Log failed tools, access walls, and no-result paths. Count a source as opened only when the original page content was retrieved. Do not count a search results page.

Classify each opened source:

- `primary`: law, regulator, company filing, original dataset, original study, or official company disclosure;
- `authoritative-secondary`: reputable reporting or analysis with direct attributable evidence;
- `other`: discovery lead, weak secondary material, or non-authoritative page.

Classify its relation as `contradicts`, `supports`, `context`, or `no-relevance`. Set `final_evidence: true` only after opening and reading the original page. Track uncovered scope explicitly.

## 4. Stop and adjudicate

Stop at the earliest of:

- the frozen falsification criterion is met;
- every planned query is executed;
- the source or round budget is exhausted;
- access, conflict, or testability forces unresolved.

Use:

- `falsified` when at least one credible counterevidence source satisfies the criterion;
- `survived` only when credible counterevidence is exactly zero and either every planned query ran or the opened-source budget is exhausted;
- `unresolved` when the search cannot support either outcome.

Repeat attempt metrics exactly in `02-verdict.json`. In `verdict.md`, create one `### CLAIM-ID — status` section with these keys:

```text
- 计划查询数：N
- 实际查询数：N
- 成功打开源数：N
- 可信反证数：N
- 未覆盖范围：text
- 停止原因：text
```

## 5. Quarantine and validate

For every falsified claim, add an audit-only quarantine entry referencing contradictory final evidence. Do not add survived or unresolved claims. Run `validate`; fix all Critical findings without touching research. Then run the report probe and report validation on a copied report integration artifact.
