# Falsify contract

## Input

Production input is one project root containing the immutable research handoff:

```text
research/10-research-report.md
research/11-claim-register.json
research/12-sources.md
research/13-open-questions.md
research/14-validation-report.md
```

The immutability snapshot also covers all stage JSON files `research/03-*.json` through `research/08-*.json`. The exact protected path set is:

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
```

Do not alter any protected file. Claim hashes are lowercase SHA-256 of the exact UTF-8 `claim` string in `11-claim-register.json`, without trimming or Unicode normalization.

## Output

Write exactly the falsify overlay below; additional report-integration artifacts belong in a separate validation subdirectory.

```text
verdict.md
falsify/00-preregistration.json
falsify/01-attempts.json
falsify/02-verdict.json
falsify/03-quarantine.json
```

JSON is UTF-8, two-space indented, newline-terminated, and deterministically ordered by path, claim ID, attempt ID, and source URL. Within quarantine, sort entries by claim ID and counterevidence references by attempt ID, source URL, then title. Write atomically in production workflows.

## Hash chain

- `00-preregistration.json` records all protected input hashes.
- `01-attempts.json.preregistration_sha256` authenticates the exact preregistration bytes.
- `02-verdict.json` authenticates exact preregistration and attempts bytes.
- `03-quarantine.json.verdict_sha256` authenticates exact verdict bytes.
- The validator re-hashes protected inputs after adjudication; any change is Critical.

## Evidence

Search results discover candidates but are not evidence. A final-evidence source must be an opened original page with an original URL, non-empty title, successful fetch status, and explicit relationship to the claim. A credible counterevidence source is final evidence marked `contradicts` from a `primary` or `authoritative-secondary` source.

## Verdicts

Only `falsified`, `survived`, and `unresolved` are valid. Omitted claims are untested. Every verdict repeats the attempt log’s exhaustiveness metrics and stop reason. An unresolved verdict always has a stop reason. A survived verdict never means true, requires zero credible counterevidence, and is valid only after all planned queries run or the opened-source budget is exhausted.

## Quarantine

Quarantine is an audit index, not a file operation. It contains one entry per falsified claim, references contradictory final-evidence sources from the attempt log, uses `action: audit-reference-only`, and states `original_preserved: true`.

## Report handoff

Report receives only `verdict.md` and `falsify/02-verdict.json`. It must exclude falsified claim IDs and exact text from its body. It may show unresolved claims only in Open Questions. Falsify never edits `research/13-open-questions.md` to force this outcome.
