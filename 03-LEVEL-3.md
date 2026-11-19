# Stage 3 — Level 3: Observability

> **The demand:** Make Checkout *legible* — you can see what it is doing, in logs, traces, and metrics, and you have your first SLO.

This is the stage where the North-Star metric, `checkout_completions_per_minute`, becomes a real, measured signal. Everything from here to Level 10 depends on the feedback you build now.

---

## Prerequisites (from Stages 1–2)
- Checkout deployed by the pipeline to a real environment
- The payments dependency you can toggle healthy/slow/down

## Tasks — one per L3 module (anchored in each module's lab)

1. **Structured logging** *(L3-M02 — Lab: Instrument, Ship, Query, Correlate).* Emit structured logs across Checkout, ship them to a store, and be able to query and **correlate** a single checkout across cart → inventory → payment → order.
2. **Distributed tracing** *(L3-M03 — Lab: Trace Across Two Services).* Instrument a trace that follows one `POST /checkout` across at least two services (Checkout → payments). Find where the latency actually goes.
3. **OpenTelemetry** *(L3-M04 — Lab: One Pipeline, Three Signals).* Unify logs, metrics, and traces through a single OTel pipeline so all three signals share context (trace IDs in logs, exemplars on metrics).
4. **SLOs & error budgets** *(L3-M05 — Lab: Define and Track an SLO).* Define your first SLO on the North-Star metric (e.g. "99% of checkouts complete in < 2s") and track its error budget.
5. **Alerting & on-call** *(L3-M06 — Lab: Alerts and an Incident).* Write SLO-based alerts (symptom, not cause) and run one simulated incident end-to-end from alert to resolution.
6. **Capacity & performance** *(L3-M07 — Lab: Breaking Point & Capacity).* Load-test Checkout to its breaking point; record where latency departs from the SLO. This number seeds every capacity conversation later.

## The integration twist
The instrumentation must be **built into the containers and pipeline from Stage 2**, not bolted on by hand. A freshly deployed Checkout is observable *on arrival* — logs shipping, traces flowing, metrics scraped, SLO tracked — with zero manual post-deploy steps. Observability is now part of the artifact.

## Deliverables
- Structured-logging + OTel instrumentation in the code
- Dashboards: the North-Star metric, latency, error rate
- One written SLO with its error-budget policy
- SLO-based alert definitions
- A load-test report with the breaking point identified

## Definition of done
- [ ] You can trace one checkout end-to-end and correlate its logs by trace ID
- [ ] `checkout_completions_per_minute` is a live dashboard
- [ ] An SLO exists and its error budget is tracked
- [ ] Alerts fire on SLO symptoms, and you've run one incident against them
- [ ] You know Checkout's breaking point from a real load test

## Assessment rubric
| Level | Looks like |
|-------|-----------|
| Novice | Metrics exist but disconnected; SLO is a number with no budget policy |
| Competent | Three signals correlated; SLO + budget tracked; symptom-based alerts |
| Mastery | Observability ships with the artifact; the SLO is on a business metric; the load test gives a defensible capacity number and the alerts are noise-free |
