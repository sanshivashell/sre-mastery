# SRE Mastery — The Capstone Project

## "Checkout" — one system, ten levels

> **Author:** Sandesh Rajbhopa · SRE Mastery
> **Format:** One continuous project. You build a single system once, then harden, scale, and mature it across ten stages — one per level. Each stage's tasks map directly to that level's modules and their labs.

---

## Why one system, not ten projects

Real SRE competence is *integrative*. You do not learn observability, then failure engineering, then release safety as separate skills — you learn to hold them all against **the same running system** at once. This capstone is built the way the job is: you stand up one service early and never stop being responsible for it. Every level adds a new demand on the system you already run, and the hard part — the part that builds mastery — is that later demands must respect everything you built earlier.

By the end you will have taken a single service from "it runs on my laptop" to "a resilient, observable, secure, well-governed socio-technical system that adapts under surprise" — and you will have the artifacts to prove it.

---

## The system: **Checkout**

A fictional e-commerce **checkout service** — the same running example used throughout the course (see the L5–L6 labs, which already center on "the Checkout Service"). Keep it deliberately small in features so the *reliability* work, not the product work, is the point.

**Minimum feature set (build once, early):**
- `POST /cart` — add an item to a cart
- `GET /cart/{id}` — read a cart
- `POST /checkout` — place an order (touches: cart store, inventory check, payment dependency, order store)
- `GET /order/{id}` — read an order status
- A **payments dependency** (mock/3rd-party) — deliberately the flaky, slow, sometimes-down thing you will spend the whole course defending against
- An **inventory** component with a "never oversell" invariant

**Tech stance:** language-agnostic. Use whatever the course used (the labs imply Python/Bash/Terraform, Prometheus/OpenTelemetry, containers/Kubernetes). The briefs specify *what* to build and *what to prove*, not which vendor — so the capstone survives tooling changes.

---

## The North-Star metric

Pick **one business steady-state metric** and carry it through every level: **`checkout_completions_per_minute`** (successful orders placed). Every SLO, every experiment, every capacity plan, every incident is judged against whether the customer can complete a purchase. This is the thread that ties L3's instrumentation to L10's chaos experiments.

---

## The ten stages

| Stage | Level | What you make the system become | Anchored in |
|-------|-------|-------------------------------|-------------|
| 1 | **L1 — Foundations** | Runnable, version-controlled, reproducible | L1 modules (incl. Terraform/IaC) † |
| 2 | **L2 — Automation & CI** | Built, tested, and deployed by a pipeline | L2 modules † |
| 3 | **L3 — Observability** | Instrumented: logs, traces, metrics, SLOs | L3 M02–M07 |
| 4 | **L4 — Failure Engineering** | Survives dependency failure without cascading | L4 M01–M07 |
| 5 | **L5 — SRE Practice** | Operated: SLOs, on-call, postmortems, capacity | L5 M01–M07 |
| 6 | **L6 — Delivery & Security** | Shipped safely, secured, governed, recoverable | L6 M01–M07 |
| 7 | **L7 — Judgment & Leadership** | Reasoned about and led, not just built | L7 M01–M04 |
| 8 | **L8 — AI Reliability** | Gains an ML feature that is *itself* made reliable | L8 M01–M06 |
| 9 | **L9 — Distributed Limits** | Scaled until it hits — and respects — hard limits | L9 M01–M06 |
| 10 | **L10 — Resilience Science** | Adapts under surprise; safety is enacted, not certified | L10 M01–M05 |

† **L1–L2 note:** Those module decks/PDFs live in the delivered DevOps Veda book series, not in this workspace. Stages 1–2 are written from the level themes and the L1 Terraform/IaC module that is present. **Verify these two stages against your actual L1–L2 module content** (a quick Cowork lookup of those decks will confirm the exact tools and terminology) and adjust the task wording to match.

---

## How each stage brief is structured

Every per-level brief (`01-LEVEL-1.md` … `10-LEVEL-10.md`) follows the same shape:

1. **The demand** — one sentence: what this level requires the system to become.
2. **Prerequisites** — what must already be true from earlier stages.
3. **Tasks, mapped per module** — each of the level's modules contributes one concrete task, tied to that module's lab where one exists.
4. **The integration twist** — the part that forces you to respect earlier stages (this is where the learning is).
5. **Deliverables** — the artifacts to produce (code, configs, docs, a short write-up).
6. **Definition of done** — objective, checkable criteria.
7. **Assessment rubric** — how to grade it (novice / competent / mastery).

---

## Grading philosophy (from L10)

The capstone is graded the way the curriculum teaches you to think:

- **Systemic** — did you reason about the whole system, or patch a component?
- **Humble** — did you test your beliefs (experiments, load tests), or assert them?
- **Humane** — are your postmortems and runbooks blameless and usable by a tired human at 3am?
- **Empirical** — is every reliability claim backed by evidence (a graph, a game-day result, a load test), not a hope?

A stage is not "done" because the code runs. It is done when you can **defend** what you built: name the trade-off, show the evidence, and explain what would make it fail.

---

## Final capstone deliverable

After Stage 10, produce a **Reliability Portfolio** for Checkout:
- The running system and all its configs/IaC
- Its SLOs and the dashboards proving them
- A control-structure diagram (L10 M02) and an STPA fragment
- Two real postmortems from game days you ran
- A capacity model with the scaling curve and the identified knee (L9 M05)
- A one-page **Reliability Charter** (L10 M05) — how you will keep enacting its safety

This portfolio is the proof of the whole climb — the artifact you show to demonstrate you can make a real socio-technical system reliable, not just recite how.

---

*Per-level briefs follow in files `01-LEVEL-1.md` through `10-LEVEL-10.md`.*
