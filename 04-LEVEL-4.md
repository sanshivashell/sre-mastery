# Stage 4 — Level 4: Failure Engineering

> **The demand:** Make Checkout survive the failure of its dependencies without cascading — and prove it by breaking things on purpose.

This is where the payments dependency you built to be flaky finally earns its keep. Every task hardens Checkout against a real failure mode, and the stage ends with you causing those failures deliberately.

---

## Prerequisites (from Stage 3)
- Full observability (you must be able to *see* a cascade to contain it)
- Known breaking point from load testing
- Toggleable payments failure modes

## Tasks — one per L4 module (anchored in each module's lab)

1. **Failure in distributed systems** *(L4-M01 — Lab: Observe a Cascade, Then Contain It).* Deliberately induce a cascading failure (slow payments → threads pile up → Checkout stalls). Watch it in your Stage-3 dashboards, then contain it.
2. **Redundancy & failover** *(L4-M02 — Lab: Build Redundancy and Fail Over).* Run Checkout with redundancy across at least two zones and demonstrate automatic failover when one is lost.
3. **Timeouts, retries, backoff** *(L4-M03 — Lab: From Retry Storm to Discipline).* Add disciplined timeouts and exponential backoff with jitter to the payments call. Show a retry storm first, then show your discipline preventing it.
4. **Circuit breakers & bulkheads** *(L4-M04 — Lab: Trip a Breaker, Build a Bulkhead).* Wrap the payments dependency in a circuit breaker; isolate its resource pool with a bulkhead so a payments outage can't consume all of Checkout's capacity.
5. **Graceful degradation & load shedding** *(L4-M05 — Lab: Degrade and Shed Under Overload).* When payments is down, degrade (queue the order, show "confirming"), don't fail hard. Add admission control that sheds load past the breaking point instead of collapsing.
6. **Chaos engineering** *(L4-M06 — Lab: Your First Chaos Experiments).* Run your first contained chaos experiments against the hardening above — kill an instance, slow payments — and confirm the North-Star metric holds.
7. **Disaster recovery** *(L4-M07 — Lab: Build and Test a DR Plan).* Write and *test* a DR plan: back up the order/cart stores, and actually restore into a fresh environment. An untested DR plan doesn't count.

## The integration twist
Each defense must be **verified against the SLO from Stage 3**, not just "added." Trip the breaker and show `checkout_completions_per_minute` degrades gracefully rather than flatlining. The chaos experiments (task 6) must use the observability (Stage 3) to define steady state and the abort condition. Resilience you can't measure is resilience you can't claim.

## Deliverables
- Code: timeouts/backoff, circuit breaker, bulkhead, degradation, load shedding
- A multi-zone deployment with demonstrated failover
- A chaos-experiment log (hypothesis, injection, result) for at least 3 experiments
- A **tested** DR plan with a restore you actually performed

## Definition of done
- [ ] Payments fully down → Checkout degrades, doesn't cascade; SLO shows graceful, not catastrophic, impact
- [ ] Retry storm demonstrated, then eliminated with backoff+jitter
- [ ] Circuit breaker trips and recovers; bulkhead contains the blast
- [ ] Load past breaking point → shed, not collapse
- [ ] DR plan executed: restored Checkout from backup into a clean environment

## Assessment rubric
| Level | Looks like |
|-------|-----------|
| Novice | Patterns added but never tested; DR plan written but never run |
| Competent | Each defense demonstrated; chaos experiments run; DR restore performed |
| Mastery | Every defense proven against the SLO with graphs; chaos is hypothesis-driven with abort conditions; DR restore is timed and repeatable |
