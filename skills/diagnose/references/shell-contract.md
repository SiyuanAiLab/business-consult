# Diagnose public-shell contract

This contract covers interaction state and research handoff only. It does not define a proprietary diagnostic method, question sequence, or decision framework.

## Runtime files

Diagnose owns exactly:

```text
diagnosis.md
diagnose/session.json
```

If either file exists, both are required. The `diagnose/` directory may contain only the regular file `session.json`.

## Session

`session.json` follows `session.schema.json` and preserves canonical key order. Interactions use consecutive turns and contain:

- one short judgment;
- one question with exactly one question mark;
- either one response summary or `null` while awaiting the user.

Question text must be unique. An in-progress session has exactly one unanswered final interaction, and `pending_question` equals that interaction's question. Earlier interactions must have responses.

## Completed handoff

A completed session has no pending question and contains:

```text
decision
scope
exclusions
research_question
evidence_needs
```

`exclusions` and `evidence_needs` are non-empty, unique, sorted string arrays. `diagnosis.md` repeats the same data in reader-facing sections and one machine-readable block.

The reader-facing handoff is a validated part of the contract, not commentary:

- `handoff.decision` appears verbatim in `## Decision`;
- `handoff.scope` appears verbatim in `## Scope`;
- every `handoff.exclusions` item appears verbatim in `## Exclusions`;
- `handoff.research_question` appears verbatim in `## Research question`;
- every `handoff.evidence_needs` item appears verbatim in `## Evidence needs`.

The validator rejects drift even when `session.handoff` and the machine-readable JSON block still match each other.

## Research acceptance

Only `validate_diagnose.py research-probe PROJECT_ROOT` can accept the handoff. In-progress, missing, inconsistent, multi-question, reply-skipping, and repeated-question sessions are rejected.
