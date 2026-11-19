# Stage 7 — Level 7: Judgment & Leadership

> **The demand:** Stop only *building* Checkout's reliability and start *reasoning about it and leading it* — the shift from senior engineer to staff-level judgment.

L7 has 4 modules and is less about code than about decisions, influence, and scope. The capstone tasks are therefore written artifacts and exercises grounded in the *actual* Checkout system you've built — you reason about the real thing, not a hypothetical.

---

## Prerequisites (from Stages 1–6)
- A fully built, operated, secured Checkout with real SLOs, incidents, and a capacity plan
- Real postmortems and a maturity assessment to reason from

## Tasks — one per L7 module (anchored in each module's lab)

1. **Reliability judgment under uncertainty** *(L7-M01 — Lab: Reason Through the Hard Call).* Take a genuine hard call from your Checkout work — e.g. "the error budget is nearly spent but there's a security fix to ship" — and reason it through in writing: options, trade-offs, what you'd decide and why, and what would change your mind.
2. **Leading reliability beyond your walls** *(L7-M02 — Lab: Lead a Change Without Authority).* Write the case you'd make to a *team you don't control* (say, the payments team) to change something that hurts Checkout's reliability — using data, not authority. This is influence, evidenced.
3. **Large-system judgment & engagement** *(L7-M03 — Lab: Make a System Non-Abstract).* Do a "non-abstract large system design" pass on Checkout at 100× scale: estimate the resources, name what breaks first, and make the abstract concrete with real numbers (tie to your Stage-3 load data and Stage-5 capacity plan).
4. **Organizational change & reliability career** *(L7-M04 — Lab: Your Reliability Practice and Legacy).* Write the reliability practice you'd institutionalize around Checkout so it outlives you — the standards, rituals, and ownership that make the system stay reliable without heroics.

## The integration twist
Every task must reason about the **real Checkout you built**, using its real artifacts — the SLOs, the postmortems, the capacity numbers, the maturity assessment. This is the level where the system stops being code and becomes a case study *you* can speak to with authority, because you built and operated every layer of it. Staff-level judgment is earned by having done the work in Stages 1–6.

## Deliverables
- A written "hard call" decision memo (with the trade-offs made explicit)
- An influence case aimed at an external team, backed by Checkout's data
- A non-abstract scaling analysis of Checkout at 100×
- A reliability-practice charter for institutionalizing the work

## Definition of done
- [ ] The hard-call memo names real options and a defensible decision, not a platitude
- [ ] The influence case uses evidence from Checkout, not opinion
- [ ] The scaling analysis has real numbers and names the first bottleneck
- [ ] The practice charter would plausibly keep Checkout reliable after you leave

## Assessment rubric
| Level | Looks like |
|-------|-----------|
| Novice | Generic advice, not tied to the real system; decisions asserted, not reasoned |
| Competent | Decisions reasoned with trade-offs; influence backed by Checkout's data |
| Mastery | Judgment is genuinely staff-level: uncertainty acknowledged, second-order effects considered, and the analysis is one a leadership audience would trust |
