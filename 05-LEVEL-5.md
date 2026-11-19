# Stage 5 — Level 5: SRE Practice

> **The demand:** Stop *building* Checkout and start *operating* it like an SRE — SLOs, on-call, postmortems, capacity, and the war on toil.

Stages 1–4 made Checkout exist, be visible, and survive failure. Stage 5 is about running it as a discipline over time. The L5 labs already center on "the Checkout Service" — this stage is their natural home.

---

## Prerequisites (from Stages 3–4)
- SLO + error budget (Stage 3) and resilience patterns (Stage 4)
- A load-tested breaking point
- Chaos tooling in place

## Tasks — one per L5 module (anchored in each module's lab)

1. **SLIs, SLOs, error budgets** *(L5-M01 — Lab: Define an SLO for the Checkout Service).* Formalize the SLI/SLO/error-budget set for Checkout beyond Stage 3's first cut: availability *and* latency SLOs, with an explicit error-budget policy (what happens when it's spent).
2. **Monitoring & alerting** *(L5-M02 — Lab: Instrument and Alert the Checkout).* Mature the alerting: multi-window burn-rate alerts on the error budget, tuned for signal. Prove the alerts catch real budget burn and stay quiet otherwise.
3. **On-call & incident response** *(L5-M03 — Lab: Run a Game Day).* Run a real **game day**: inject a failure (use Stage-4 chaos), respond as on-call, and evaluate detection, diagnosis, and coordination — not just whether the system recovered.
4. **Blameless postmortems** *(L5-M04 — Lab: Write a Postmortem).* Write a blameless postmortem for the game-day incident. Second story, contributing factors, systemic actions — no names, no blame.
5. **Capacity planning & scalability** *(L5-M05 — Lab: Find the Knee, Build a Plan).* Using Stage-3's load data, find the knee of the latency curve and build a capacity plan: how many replicas for forecast peak + failure headroom (N+1).
6. **Performance engineering** *(L5-M06 — Lab: Profile and Optimize Checkout).* Profile Checkout under load, find the real bottleneck, optimize it, and prove the improvement moved the SLO or the capacity number.
7. **Toil & operational maturity** *(L5-M07 — Lab: Measure Toil, Then Remove Some).* Measure the manual/repetitive work in operating Checkout, then automate a chunk of it away. Show the toil reduction.

## The integration twist
The **error-budget policy** now governs everything downstream: it will decide (in Stage 6) whether you're allowed to ship. The game day (task 3) must exercise the **on-call human**, not just the machine — this is the first appearance of the socio-technical system that L10 will make central. And the capacity plan must include the **failure headroom** proven necessary in Stage 4's failover work.

## Deliverables
- The full SLI/SLO/error-budget spec + policy
- Burn-rate alert definitions
- A game-day plan and its execution log
- A blameless postmortem
- A capacity plan (knee, replicas, headroom)
- A profiling report showing a real optimization
- A toil measurement + one automation that reduced it

## Definition of done
- [ ] Availability + latency SLOs with an enforced error-budget policy
- [ ] Burn-rate alerts proven to catch budget burn
- [ ] One game day run with humans in the loop
- [ ] One blameless postmortem written to standard
- [ ] Capacity plan with headroom, grounded in the load data
- [ ] One measured, automated reduction in toil

## Assessment rubric
| Level | Looks like |
|-------|-----------|
| Novice | SLOs exist but no budget policy; postmortem assigns blame |
| Competent | Budget policy enforced; game day + blameless postmortem done; capacity plan grounded in data |
| Mastery | Burn-rate alerting is noise-free; the game day tested people and revealed a real gap; the postmortem produced systemic fixes; toil is measured, not guessed |
