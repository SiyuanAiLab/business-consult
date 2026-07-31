---
status: active
---

# Five-stage questioning chain

Use this chain during intake and reuse each answer downstream. Do not ask for information already present in `diagnosis.md`.

## Q0: Context alignment (before Q1, when the subject touches the operator's own business)

Ask:

- Whose decision does this research serve?
- Does the user want to supply an operating model, decision principles, constraints, or another business-context document?
- If readable context is supplied, align the question to it and record the file identifier plus the version or date provided by the user.
- Ask for the decision-maker's own decision criteria and constraints; do not substitute hidden or remembered criteria.
- If no business context is supplied, record `[Assumption] No business context supplied` and continue with the general decision questions.
- If the user explicitly supplies an unreadable path or mutually conflicting documents, stop and request usable or reconciled input.

Self-check: when context is supplied, the brief must identify the supplied file and its version or date. When context is absent, the exact `[Assumption]` above must appear and research must not stop solely because context was omitted.

## Q1: Unspoken insight

Ask:

- What decision will this research change?
- What uncomfortable fact might the current framing avoid?
- Who will act on the answer?

Self-check: replace the industry name with an unrelated industry. If the answer still works, rewrite it.

## Q2: Foundational assumptions

List the assumptions required for the opportunity to exist:

- demand
- willingness to pay
- workflow frequency
- access to data
- technical feasibility
- channel access

Self-check: each assumption must be capable of becoming false through one observable fact.

## Q3: Structural power

Ask who controls distribution, data, workflow, trust, switching cost, and supply. Distinguish direct competitors, substitutes, ecosystem actors, and benchmark operators.

Self-check: if every player appears to have a strong moat, the assessment is too generous.

## Q4: Investor destruction test

Ask five questions that could kill the thesis:

- What would make the market smaller than it appears?
- Which existing workflow is "good enough"?
- How can a platform bundle away the value?
- What evidence would show weak willingness to pay?
- What regulation or data constraint blocks deployment?

Self-check: a question that cannot change the recommendation is not destructive enough.

## Q5: Stress-test and repair

Score the current answer from 1 to 10 for specificity, evidence, contradiction handling, and decision relevance. Repair only scores of 7 or below.

Self-check: after two repairs, externalize the remaining gap as an Open Question; do not keep iterating.

## Required intake fields

Capture:

- `decision`
- `audience`
- `subject`
- `geography`
- `period`
- `depth`
- `known_competitors`
- `supplied_numbers`
- `exclusions`
- `delivery_language`

Echo `supplied_numbers` verbatim in the brief and the relevant stage file.
