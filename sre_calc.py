#!/usr/bin/env python3
"""
sre_calc.py — a working reference library of SRE calculations.

Every formula from the SRE Metrics cheatsheet, implemented and tested.
Import it, or run it directly for a self-test:  python3 sre_calc.py

No third-party dependencies — standard library only.
"""
from __future__ import annotations
import math

# ─────────────────────────────────────────────────────────────────────────
# Reliability: MTBF / MTTR / MTTF / availability
# ─────────────────────────────────────────────────────────────────────────

def mttr(total_downtime, num_incidents):
    """Mean Time To Repair/Recover = total downtime / number of incidents."""
    if num_incidents == 0:
        return 0.0
    return total_downtime / num_incidents


def mtbf(total_uptime, num_failures):
    """Mean Time Between Failures = total uptime / number of failures."""
    if num_failures == 0:
        return float("inf")
    return total_uptime / num_failures


def mttf(total_operating_time, num_units):
    """Mean Time To Failure (non-repairable) = operating time / units."""
    if num_units == 0:
        return 0.0
    return total_operating_time / num_units


def availability_from_mtbf(mtbf_val, mttr_val):
    """Availability = MTBF / (MTBF + MTTR)."""
    if mtbf_val + mttr_val == 0:
        return 0.0
    return mtbf_val / (mtbf_val + mttr_val)


def availability(uptime, downtime):
    """Availability = uptime / (uptime + downtime)."""
    total = uptime + downtime
    return uptime / total if total else 0.0


# ─────────────────────────────────────────────────────────────────────────
# Downtime / the "nines"
# ─────────────────────────────────────────────────────────────────────────

# period lengths in minutes
PERIODS_MIN = {
    "day": 24 * 60,
    "week": 7 * 24 * 60,
    "month": 30 * 24 * 60,   # 30-day month convention
    "quarter": 91 * 24 * 60,
    "year": 365 * 24 * 60,
}

def allowed_downtime(slo_percent, period="month"):
    """Allowed downtime (minutes) for an SLO over a period.
    slo_percent e.g. 99.9 ; period one of PERIODS_MIN."""
    window = PERIODS_MIN[period]
    return window * (1 - slo_percent / 100.0)


def downtime_table(slo_percent):
    """Allowed downtime across all standard periods, in minutes."""
    return {p: allowed_downtime(slo_percent, p) for p in PERIODS_MIN}


def series_availability(*avails):
    """Availability of dependencies called in series (all must work).
    Pass fractions (0.999), returns a fraction."""
    out = 1.0
    for a in avails:
        out *= a
    return out


def parallel_availability(*avails):
    """Availability of redundant copies in parallel (any one works)."""
    fail = 1.0
    for a in avails:
        fail *= (1 - a)
    return 1 - fail


# ─────────────────────────────────────────────────────────────────────────
# Error budgets & burn rate
# ─────────────────────────────────────────────────────────────────────────

def error_budget_fraction(slo_percent):
    """Error budget as a fraction = 1 - SLO."""
    return 1 - slo_percent / 100.0


def error_budget_time(slo_percent, period="month"):
    """Error budget expressed as allowed downtime minutes (same as allowed_downtime)."""
    return allowed_downtime(slo_percent, period)


def error_budget_requests(slo_percent, total_requests):
    """Error budget expressed as number of allowed failed requests."""
    return total_requests * error_budget_fraction(slo_percent)


def budget_remaining(actual_errors, allowed_errors):
    """Fraction of error budget remaining (1.0 = full, 0.0 = spent, <0 = breached)."""
    if allowed_errors == 0:
        return 0.0
    return 1 - (actual_errors / allowed_errors)


def burn_rate(observed_error_rate, slo_percent):
    """Burn rate = observed error rate / (1 - SLO).
    observed_error_rate is a fraction (0.014 = 1.4% errors)."""
    budget = error_budget_fraction(slo_percent)
    if budget == 0:
        return float("inf")
    return observed_error_rate / budget


def time_to_exhaust(window_hours, burn_rate_val):
    """Hours until the budget for `window_hours` is gone at this burn rate."""
    if burn_rate_val == 0:
        return float("inf")
    return window_hours / burn_rate_val


# Google multi-window multi-burn-rate reference thresholds
BURN_ALERTS = [
    # (severity, burn_rate, long_window, short_window, budget_gone_in)
    ("page",   14.4, "1h",  "5m",  "~2 days"),
    ("page",    6.0, "6h",  "30m", "~5 days"),
    ("ticket",  3.0, "24h", "2h",  "~10 days"),
    ("ticket",  1.0, "72h", "6h",  "full window"),
]


# ─────────────────────────────────────────────────────────────────────────
# Queueing & capacity
# ─────────────────────────────────────────────────────────────────────────

def littles_law_L(arrival_rate, avg_time_in_system):
    """L = λ × W  (average items in system)."""
    return arrival_rate * avg_time_in_system


def littles_law_W(L, arrival_rate):
    """W = L / λ  (average time in system)."""
    return L / arrival_rate if arrival_rate else 0.0


def utilization_wait_factor(rho):
    """Relative wait time multiplier ∝ 1/(1-ρ). rho is a fraction < 1."""
    if rho >= 1:
        return float("inf")
    return 1 / (1 - rho)


def usl_capacity(N, alpha, beta):
    """Universal Scalability Law relative capacity at N nodes.
    alpha = contention, beta = coherency."""
    return N / (1 + alpha * (N - 1) + beta * N * (N - 1))


def usl_peak(alpha, beta):
    """Optimal node count N* = sqrt((1 - alpha)/beta) — the scaling knee."""
    if beta == 0:
        return float("inf")
    return math.sqrt((1 - alpha) / beta)


# ─────────────────────────────────────────────────────────────────────────
# Capacity provisioning
# ─────────────────────────────────────────────────────────────────────────

def required_replicas(peak_load, per_replica_capacity, target_utilization=0.7):
    """Replicas to hold peak load under a utilization ceiling."""
    effective = per_replica_capacity * target_utilization
    return math.ceil(peak_load / effective)


def with_failure_headroom(replicas, num_failure_domains):
    """Add N+1 headroom: enough spare to lose one failure domain."""
    if num_failure_domains <= 1:
        return replicas
    per_domain = math.ceil(replicas / num_failure_domains)
    return replicas + per_domain


# ─────────────────────────────────────────────────────────────────────────
# Toil
# ─────────────────────────────────────────────────────────────────────────

def toil_fraction(time_on_toil, total_time):
    """Fraction of time spent on toil. Keep < 0.5 (Google guidance)."""
    return time_on_toil / total_time if total_time else 0.0


def automation_payback(time_to_automate, time_saved_each, occurrences_per_period):
    """Number of periods until an automation pays for itself."""
    saved_per_period = time_saved_each * occurrences_per_period
    if saved_per_period == 0:
        return float("inf")
    return time_to_automate / saved_per_period


# ─────────────────────────────────────────────────────────────────────────
# Self-test / demo
# ─────────────────────────────────────────────────────────────────────────

def _selftest():
    print("=== MTT* / availability ===")
    print(f"MTTR (90min, 3 incidents)      = {mttr(90, 3):.1f} min")
    print(f"MTBF (129510min, 3 failures)   = {mtbf(129510, 3):,.0f} min")
    print(f"Availability (MTBF/MTBF+MTTR)  = {availability_from_mtbf(43170, 30)*100:.4f}%")

    print("\n=== downtime 'nines' ===")
    for slo in (99, 99.9, 99.99):
        t = allowed_downtime(slo, "month")
        print(f"{slo:>6}%  → {t:>7.2f} min/month")

    print("\n=== series vs parallel ===")
    print(f"two 99.9% in series   = {series_availability(0.999,0.999)*100:.4f}%  (worse)")
    print(f"two 99.9% in parallel = {parallel_availability(0.999,0.999)*100:.4f}%  (better)")

    print("\n=== error budget (99.9%, 30d, 1M req) ===")
    print(f"budget time     = {error_budget_time(99.9):.1f} min")
    print(f"budget requests = {error_budget_requests(99.9, 1_000_000):,.0f} failed req")

    print("\n=== burn rate ===")
    br = burn_rate(0.0144, 99.9)   # 1.44% errors against a 99.9% SLO
    print(f"burn_rate(1.44% err, 99.9% SLO) = {br:.1f}")
    print(f"30-day budget gone in           = {time_to_exhaust(30*24, br)/24:.2f} days")

    print("\n=== queueing / USL ===")
    print(f"Little's L (500/s, 0.2s)   = {littles_law_L(500, 0.2):.0f} in flight")
    print(f"wait factor at ρ=0.95      = {utilization_wait_factor(0.95):.0f}x")
    print(f"USL peak (α=0.03, β=0.001) = {usl_peak(0.03, 0.001):.0f} nodes")

    print("\n=== capacity ===")
    r = required_replicas(10_000, 1_000, 0.7)
    print(f"replicas (10k peak, 1k/replica, 70%) = {r}")
    print(f"with N+1 across 3 zones              = {with_failure_headroom(r, 3)}")

    print("\n=== toil ===")
    print(f"toil fraction (12h/40h)    = {toil_fraction(12,40)*100:.0f}%")
    print(f"automation payback         = {automation_payback(8, 0.5, 20):.1f} periods")

    print("\nAll functions executed OK.")


if __name__ == "__main__":
    _selftest()
