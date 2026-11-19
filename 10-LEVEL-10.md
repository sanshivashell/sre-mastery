# Stage 10 — Level 10: Resilience Science (The Final Synthesis)

> **The demand:** Treat Checkout as a socio-technical system whose safety is *enacted, not certified* — and apply the science of resilience to make it adapt under surprise.

The final stage. Checkout is fully built, operated, scaled, and pushed to its limits. Now you apply the frontier ideas — resilience engineering, safety science, the new view of human error, and chaos engineering — to the whole system, people included. This stage produces the **Reliability Portfolio** that is the capstone's final artifact.

---

## Prerequisites (from Stages 1–9)
- The complete Checkout system with SLOs, incidents, postmortems, capacity models, and a distributed-systems trade-off table
- Real game-day and chaos experience (Stages 4–5)

## Tasks — one per L10 module (anchored in each module's lab)

1. **Resilience engineering** *(L10-M01 — Lab: Map Your Adaptive Capacity).* Assess Checkout against the four cornerstones — respond, monitor, learn, anticipate — and its graceful extensibility. Where would it stretch under a surprise it wasn't designed for, and where would it snap?
2. **Safety science / STAMP-STPA** *(L10-M02 — Lab: STPA on Your System).* Draw Checkout's **safety control structure** (autoscaler, deploy pipeline, on-call, payments, inventory — controllers, control actions, feedback). Run an STPA pass: find one unsafe control action and the missing feedback behind it. Add the constraint.
3. **The new view of human error** *(L10-M03 — Lab: Rewrite the First Story).* Take a real incident from your Stage-5/6 game days, told as "human error," and rewrite it as a second story — reaching the blunt-end conditions (the tools, the pressures) that made the action locally rational. Ship the systemic fix.
4. **Chaos engineering** *(L10-M04 — Lab: Design a Chaos Experiment).* Design and run a *mature* chaos experiment on Checkout: business-metric steady state, hypothesis, real-world event, contained blast radius, automated abort. Ideally automate it to run continuously (Principle 4).
5. **Shaping the field** *(L10-M05 — Capstone: Your Reliability Charter).* Write Checkout's **Reliability Charter** — how you will keep enacting its safety continuously: the assess → analyze → experiment → learn loop applied to this specific system, the slack you'll protect, and the one reliability question you'll hold against every future change.

## The integration twist
This stage doesn't add features — it **re-sees the entire system** through the resilience lens and closes every loop from Stages 1–9. The STPA control structure includes the ML model (Stage 8) and the consensus cluster (Stage 9) as controllers. The chaos experiment respects the invariants (Stage 9) and the error budget (Stage 5). The second-story rewrite uses the observability (Stage 3) to reconstruct what the operator saw. Safety, here, is shown to be the continuous, active accomplishment of the whole system you built — not a property you can point at in any one stage.

## Deliverables — and the FINAL Reliability Portfolio

Assemble everything into the capstone's final artifact, the **Checkout Reliability Portfolio**:
- The running system + all IaC/configs (Stages 1–2, 6)
- The SLOs and dashboards proving them (Stages 3, 5)
- The safety control-structure diagram + STPA fragment (this stage)
- Two real blameless postmortems from game days (Stages 5, 10)
- The capacity model with the USL knee (Stages 5, 9)
- The distributed-systems trade-off table (Stage 9)
- The four-cornerstones adaptive-capacity assessment (this stage)
- A continuous chaos experiment (this stage)
- The one-page **Reliability Charter** (this stage)

## Definition of done
- [ ] Adaptive capacity assessed against the four cornerstones with honest gaps named
- [ ] A control structure drawn and one STPA-found constraint added
- [ ] One incident rewritten first-story → second-story with a shipped systemic fix
- [ ] One mature, contained chaos experiment run (business metric, abort) — ideally continuous
- [ ] The Reliability Charter written
- [ ] The full Reliability Portfolio assembled

## Assessment rubric
| Level | Looks like |
|-------|-----------|
| Novice | Treats L10 as more chaos tooling; portfolio is a file dump |
| Competent | Control structure + STPA + second story + mature experiment all done; portfolio coherent |
| Mastery | The whole system is visibly re-seen as socio-technical; safety is demonstrably *enacted* (continuous experiments, live feedback, restorative culture); the portfolio would convince a skeptical staff engineer that Checkout is genuinely resilient — and that *you* can make systems so |

---

## 🎓 Completing the capstone

When the Reliability Portfolio is done, you have taken one system from `git clone` to a resilient, observable, secure, well-governed socio-technical system that adapts under surprise — applying all 65 modules across all 10 levels to a single running service. That portfolio is the proof of the whole climb.

**Safety is something you do. Now go shape the field.**
