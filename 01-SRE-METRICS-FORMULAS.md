# SRE Metrics & Formulas — Cheatsheet

> A practitioner reference for the calculations an SRE reaches for daily. Every formula has its
> units, a worked example, and the gotcha that trips people up. Companion code:
> `sre_calc.py` (working Python for all of these).

---

## 1. The reliability "MTT*" family

| Metric | Means | Formula | Unit |
|--------|-------|---------|------|
| **MTBF** | Mean Time **Between** Failures | `total uptime / number of failures` | time |
| **MTTF** | Mean Time **To** Failure (non-repairable) | `total operating time / number of units` | time |
| **MTTR** | Mean Time **To** **Repair/Recover** | `total downtime / number of incidents` | time |
| **MTTD** | Mean Time **To** **Detect** | `Σ(detect_time − start_time) / incidents` | time |
| **MTTA** | Mean Time **To** **Acknowledge** | `Σ(ack_time − alert_time) / incidents` | time |
| **MTTF + MTTR = MTBF** | (repairable systems) | the cycle: run, fail, fix, repeat | — |

**Worked example.** Over 90 days a service had 3 incidents; total downtime 90 min.
- MTTR = 90 min / 3 = **30 min per incident**
- Uptime = (90 d × 24 × 60) − 90 = 129,510 min; MTBF = 129,510 / 3 = **43,170 min ≈ 30 days**

**Gotcha.** MTTR is an *average* — one 4-hour outage and two 5-minute blips average to a misleading "1h 30m." Always look at the distribution (p50/p90), not just the mean. Averages hide your worst incidents.

**MTTR breakdown (useful for finding where time goes):**
```
incident timeline:
  start ──▶ detect ──▶ acknowledge ──▶ mitigate ──▶ resolve
         MTTD        MTTA           (repair)      MTTR (start→resolve)
```
Shrinking MTTR usually means shrinking **MTTD** first — you cannot fix what you have not detected.

---

## 2. Availability & downtime

**Availability** = fraction of time the service met its SLI.
```
Availability = uptime / (uptime + downtime)
            = MTBF / (MTBF + MTTR)          # for repairable systems
```

**The "nines" table — allowed downtime per period:**

| Availability | Per day | Per week | Per month (30d) | Per year |
|--------------|---------|----------|-----------------|----------|
| 90% (1 nine) | 2.4 h | 16.8 h | 72 h | 36.5 d |
| 99% (2 nines) | 14.4 min | 1.68 h | 7.2 h | 3.65 d |
| 99.9% (3 nines) | 1.44 min | 10.1 min | 43.2 min | 8.77 h |
| 99.95% | 43.2 s | 5.04 min | 21.6 min | 4.38 h |
| 99.99% (4 nines) | 8.64 s | 1.01 min | 4.32 min | 52.6 min |
| 99.999% (5 nines) | 0.86 s | 6.05 s | 25.9 s | 5.26 min |

**Worked example.** A 99.9% monthly SLO ⇒ **43.2 minutes** of allowed downtime per 30 days.
`43,200 min × (1 − 0.999) = 43.2 min`.

**Gotcha — availability is not additive across dependencies.** Two services each at 99.9%, called in series, give `0.999 × 0.999 = 99.8%`, *worse* than either. Redundant (parallel) copies multiply the *failure* probabilities: `1 − (1−0.999)² = 99.9999%`. Series hurts, parallel helps.

```
series (both must work):   A_total = A1 × A2 × … × An
parallel (any one works):  A_total = 1 − Π(1 − Ai)
```

---

## 3. Error budgets

The error budget is the **allowed unreliability** — the room to fail without breaching the SLO.
```
Error budget (fraction) = 1 − SLO
Error budget (time)     = period × (1 − SLO)
Error budget (requests) = total_requests × (1 − SLO)
```

**Worked example (99.9% SLO, 30-day window, 1M requests):**
- Budget as time: `43,200 min × 0.001 = 43.2 min` of downtime
- Budget as requests: `1,000,000 × 0.001 = 1,000` failed requests

**Budget remaining** (what dashboards should show):
```
budget_consumed_fraction = actual_errors / allowed_errors
budget_remaining         = 1 − budget_consumed_fraction     # as a %
hours_to_exhaustion      = budget_remaining_errors / current_error_rate_per_hour
```

**Gotcha.** An error budget is a *decision tool*, not a vanity metric. The whole point is the **policy**: "budget spent ⇒ freeze feature releases, focus on reliability." A budget with no policy attached changes nothing.

---

## 4. Burn rate (the modern SLO alert)

**Burn rate** = how fast you are consuming the error budget relative to the sustainable rate.
```
burn_rate = observed_error_rate / (1 − SLO)
```
- `burn_rate = 1`  → consuming exactly at the sustainable pace (budget lasts the whole window)
- `burn_rate = 14.4` → you will exhaust the **monthly** budget in ~2 days
- `burn_rate = 6`  → exhaust in ~5 days

**Time to exhaust the budget:**
```
time_to_exhaust = window_length / burn_rate
# e.g. 30-day budget at burn_rate 14.4  →  30/14.4 ≈ 2.08 days
```

**Google's multi-window, multi-burn-rate policy (from the SRE Workbook):**

| Severity | Burn rate | Long window | Short window | Budget gone in |
|----------|-----------|-------------|--------------|----------------|
| **Page** (fast burn) | 14.4× | 1 h | 5 min | ~2 days |
| **Page** | 6× | 6 h | 30 min | ~5 days |
| **Ticket** (slow burn) | 3× | 24 h | 2 h | ~10 days |
| **Ticket** | 1× | 72 h | 6 h | full window |

**Why two windows?** The *long* window decides severity; the *short* window makes the alert
**stop firing quickly** once the burn stops, so you don't get paged for an issue that already resolved.

---

## 5. Latency & percentiles

**Never report averages for latency** — they hide the tail that hurts users.
```
p50 (median)  — typical experience
p90 / p95     — the SLO line for most services
p99 / p99.9   — the tail; where the angriest users live
```

**Gotcha — percentiles don't average or add.** You cannot average two servers' p99s to get the fleet p99, and you cannot add a service's p99s along a call chain. To get a fleet percentile, aggregate the **histogram buckets** first, then compute the quantile (see the PromQL cheatsheet). For a chain, the end-to-end p99 is *worse* than any single hop's p99, because the slow requests aren't the same ones each hop — this is **tail amplification**: with N independent hops each serving p99 in T, the chance all N are fast is `0.99^N`, so fan-out makes tails explode.

---

## 6. Queueing & capacity (the utilization wall)

**Little's Law** — the most useful queueing identity:
```
L = λ × W
  L = average number of items in the system
  λ = arrival rate (items / sec)
  W = average time an item spends in the system (sec)
```
**Worked example.** 500 req/s, each taking 0.2 s ⇒ `L = 500 × 0.2 = 100` requests in flight on average. Size your connection/thread pools for that, plus headroom.

**The utilization curve (why you never run hot):** as utilization ρ → 1, waiting time blows up.
```
wait_time ∝ 1 / (1 − ρ)
```
| Utilization ρ | Relative wait |
|---------------|---------------|
| 50% | 2× |
| 80% | 5× |
| 90% | 10× |
| 95% | 20× |
| 99% | 100× |

**Gotcha.** "The servers are only 60% busy" is often *not* waste — 60% may be exactly the utilization ceiling your latency SLO permits. Capacity = enough to hold the SLO **at peak**, not enough to handle average load.

**Universal Scalability Law (USL)** — why adding nodes eventually *hurts*:
```
C(N) = N / (1 + α(N−1) + β·N(N−1))
  α = contention (serialization / queueing)
  β = coherency (cost of keeping nodes consistent) — grows quadratically
peak node count:  N* = sqrt((1 − α) / β)
```
Past `N*`, more nodes *reduce* throughput. High β (strong consistency, chatty coordination) ⇒ low ceiling.

---

## 7. Capacity provisioning quick math

```
required_capacity = peak_load / target_utilization
replicas          = ceil(required_capacity / per_replica_capacity)
with_failure_headroom (N+1) = replicas + (replicas / num_failure_domains)
```
**Worked example.** Peak 10,000 req/s; a replica safely serves 1,000 req/s at the 70% SLO ceiling ⇒ `10,000 / 0.7 / 1,000 = 14.3 → 15 replicas`. Across 3 zones, add one zone's worth (5) for N+1 ⇒ **20 replicas** so losing a zone still holds the SLO.

---

## 8. Toil & operational load

```
toil_fraction = time_on_toil / total_time
```
Google's guidance: keep toil **< 50%** of an SRE's time; the rest goes to engineering that reduces future toil. Track it, because toil silently grows to fill the time available.

**Automation payback:**
```
payback_period = time_to_automate / time_saved_per_occurrence / occurrences_per_period
```
Automate when the task is frequent *and* the payback lands inside the time you'll keep doing it.

---

## Quick reference — the numbers worth memorizing

- **99.9% = 43.2 min/month** of downtime. **99.99% = 4.32 min/month.** (Each nine ≈ 10× less.)
- **Burn rate 14.4 = monthly budget gone in 2 days** (the classic page threshold).
- **Availability multiplies in series** (dependencies make you *less* available).
- **Wait time ∝ 1/(1−ρ)** — plan capacity from the latency SLO, not from 100% CPU.
- **Toil < 50%.** Percentiles **don't add**. MTTR is an **average** — watch the distribution.
