# SRE Reference Pack

> A practitioner's quick-reference companion to the SRE Mastery curriculum — the formulas,
> calculations, queries, and code snippets an SRE reaches for while learning and on the job.
> Every formula is worked; every code file runs and self-tests.

---

## What's here

| File | What it is | Use it when |
|------|-----------|-------------|
| **01-SRE-METRICS-FORMULAS.md** | The math: MTTR/MTBF, availability & the "nines," error budgets, burn rate, percentiles, Little's Law, USL, capacity, toil | You need a formula, a worked example, or the gotcha behind a metric |
| **sre_calc.py** | Working Python for every formula above — import it or run it | You want to *compute* a number, not just read the formula |
| **02-PROMQL-CHEATSHEET.md** | Copy-paste PromQL: golden signals, SLIs, burn-rate alerts, saturation, health | You're writing a dashboard or an alert rule |
| **resilience_patterns.py** | Tested code: retry+backoff, circuit breaker, bulkhead, token bucket, load shedder, timeout | You're hardening a service against dependency failure |

---

## Quick start

```bash
# See every formula computed with worked examples:
python3 sre_calc.py

# See every resilience pattern run:
python3 resilience_patterns.py
```

Both files are standard-library only — no `pip install` needed.

```python
# Use the calculators in your own work:
from sre_calc import allowed_downtime, burn_rate, required_replicas

allowed_downtime(99.9, "month")      # → 43.2  (minutes/month for 99.9%)
burn_rate(0.0144, 99.9)              # → 14.4  (the classic "page" threshold)
required_replicas(10_000, 1_000)     # → 15    (peak/ceiling, rounded up)
```

```python
# Wrap a flaky dependency in your service:
from resilience_patterns import CircuitBreaker, retry_with_backoff

breaker = CircuitBreaker(fail_threshold=5, reset_timeout=30)
result = breaker.call(lambda: retry_with_backoff(call_payments))
```

---

## The numbers worth memorizing

- **99.9% = 43.2 min/month** downtime. Each extra nine ≈ **10× less**. (99.99% = 4.32 min.)
- **Burn rate 14.4 ⇒ monthly budget gone in ~2 days** — page. **6× ⇒ ~5 days** — ticket.
- **Availability multiplies in series** — dependencies make you *less* available.
- **Wait time ∝ 1/(1−ρ)** — size capacity from the latency SLO, not from 100% CPU.
- **Percentiles don't add or average.** **MTTR is a mean** — watch the distribution. **Toil < 50%.**
- **Every remote call needs a timeout.** No timeout is the #1 cause of cascading failure.

---

## How this maps to the curriculum

- **Metrics & formulas** → Levels 3 & 5 (observability, SLOs, capacity)
- **PromQL** → Levels 3 & 5 (instrumentation, alerting)
- **Resilience patterns** → Level 4 (failure engineering), reused in Levels 8 & 10
- **Little's Law & USL** → Levels 5 & 9 (capacity modeling, scaling limits)

Pair this pack with the **capstone project** (`../00-CAPSTONE-MASTER.md`): the capstone tells you
*what* to build stage by stage; this pack gives you the *formulas and code* to build it with.

---

*Formulas verified against standard SRE practice; PromQL verified against current Prometheus
(2025–2026). Both Python modules self-test on run.*
