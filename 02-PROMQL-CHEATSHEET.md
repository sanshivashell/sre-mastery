# PromQL Cheatsheet for SREs

> Copy-paste-ready Prometheus queries for the things SREs actually monitor. Replace
> `http_requests_total` / `http_request_duration_seconds` with your metric names.
> Verified against current Prometheus practice (2025–2026).

---

## Metric-type rules of thumb (get this right first)

| Type | For | How to query |
|------|-----|--------------|
| **Counter** | things that only increase (requests, errors, bytes) | always wrap in `rate()` / `increase()` |
| **Gauge** | values that go up and down (memory, queue depth, temp) | query directly |
| **Histogram** | distributions (latency, sizes) | `histogram_quantile()` on `_bucket` |
| **Summary** | client-side quantiles | ⚠️ can't aggregate across instances — prefer Histogram |

**Rule:** never `rate()` a gauge; never query a counter raw. For any latency SLO, use a **histogram** (only histograms aggregate percentiles across instances).

---

## The Golden Signals

```promql
# TRAFFIC — requests per second (5-min rate)
sum(rate(http_requests_total[5m]))

# ERRORS — fraction of requests that are 5xx
sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
sum(rate(http_requests_total[5m]))

# LATENCY — p99 from a histogram (aggregate buckets by le FIRST)
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# SATURATION — CPU utilisation (1 - idle)
avg by (instance) (1 - rate(node_cpu_seconds_total{mode="idle"}[5m]))
```

**Gotcha (percentiles):** always `sum(...) by (le)` *inside* `histogram_quantile`. Computing the quantile per-instance and then averaging gives a wrong fleet percentile — percentiles don't average.

---

## SLIs (the numbers behind your SLO)

```promql
# AVAILABILITY SLI — success ratio over the SLO window (30d)
sum(rate(http_requests_total{status=~"2..|3.."}[30d]))
  /
sum(rate(http_requests_total[30d]))

# LATENCY SLI — % of requests under the 200ms threshold
# (needs le="0.2" to be an ACTUAL bucket boundary — see gotcha)
sum(rate(http_request_duration_seconds_bucket{le="0.2"}[30d]))
  /
sum(rate(http_request_duration_seconds_count[30d]))
```

**Gotcha (bucket boundaries):** your histogram must have your SLO threshold as an explicit
bucket (`le="0.2"` for a 200ms SLO). Without it, Prometheus interpolates and your latency
SLI is imprecise. Define buckets around your SLO thresholds when you instrument.

---

## Error budget & burn rate

```promql
# ERROR RATE (the SLI's complement)
sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
sum(rate(http_requests_total[5m]))

# BURN RATE — how fast you're eating the budget (99.9% SLO ⇒ budget = 0.001)
(
  sum(rate(http_requests_total{status=~"5.."}[1h]))
    /
  sum(rate(http_requests_total[1h]))
) / 0.001
```

**Multi-window, multi-burn-rate alerts (Google SRE Workbook).** Fire only when BOTH a long
and a short window exceed the threshold — the short window makes the alert clear quickly.

```yaml
groups:
- name: slo-burn-rate
  rules:
  # PAGE — fast burn: 14.4x, monthly budget gone in ~2 days
  - alert: ErrorBudgetFastBurn
    expr: |
      (
        sum(rate(http_requests_total{status=~"5.."}[1h]))
          / sum(rate(http_requests_total[1h]))
      ) / 0.001 > 14.4
      and
      (
        sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m]))
      ) / 0.001 > 14.4
    for: 2m
    labels: {severity: page}
    annotations:
      summary: "Fast error-budget burn — monthly budget exhausts in ~2 days"

  # TICKET — slow burn: 6x, budget gone in ~5 days
  - alert: ErrorBudgetSlowBurn
    expr: |
      (
        sum(rate(http_requests_total{status=~"5.."}[6h]))
          / sum(rate(http_requests_total[6h]))
      ) / 0.001 > 6
      and
      (
        sum(rate(http_requests_total{status=~"5.."}[30m]))
          / sum(rate(http_requests_total[30m]))
      ) / 0.001 > 6
    for: 15m
    labels: {severity: ticket}
    annotations:
      summary: "Slow error-budget burn — budget exhausts in ~5 days"
```

---

## Latency — more angles

```promql
# Multiple percentiles at once (dashboard latency profile)
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# p95 grouped by endpoint
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, handler)
)

# Average latency (quick, before histograms exist — less useful than percentiles)
rate(http_request_duration_seconds_sum[5m])
  /
rate(http_request_duration_seconds_count[5m])

# p95 now vs 24h ago (detect creeping latency)
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
  /
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m] offset 1d)) by (le))
```

---

## Saturation & resources

```promql
# Memory used above 90%
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) > 0.9

# Disk usage %
1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)

# Disk will fill within 4 hours (linear projection from last hour)
predict_linear(node_filesystem_avail_bytes[1h], 4 * 3600) < 0

# Top 10 memory-hungry pods
topk(10, container_memory_working_set_bytes{container!=""})

# Memory leak: growing > 1MB/s over 30m
deriv(process_resident_memory_bytes[30m]) > 1024 * 1024
```

---

## Health & availability checks

```promql
# Instance down
up == 0

# Kubernetes deployment degraded (available < desired)
kube_deployment_status_replicas_available / kube_deployment_spec_replicas < 1

# Pod restarting frequently (>0 restarts in last hour)
increase(kube_pod_container_status_restarts_total[1h]) > 0

# Traffic dropped below 70% of the same time last week (routing/upstream issue)
sum(rate(http_requests_total[5m]))
  <
0.7 * sum(rate(http_requests_total[5m] offset 1w))
```

---

## Function quick-reference

| Function | Use | Note |
|----------|-----|------|
| `rate(x[5m])` | per-second average rate of a counter | smooths; use for graphs/SLIs |
| `irate(x[5m])` | instantaneous rate (last 2 points) | spiky; use for fast-moving only |
| `increase(x[1h])` | total increase over window | `= rate × window`; for "how many" |
| `histogram_quantile(q, …)` | percentile from `_bucket` | aggregate `by (le)` first |
| `predict_linear(g[1h], s)` | linear projection `s` seconds ahead | only for ~linear trends (disk) |
| `deriv(g[30m])` | per-second derivative of a gauge | leak/trend detection |
| `topk(k, …)` / `bottomk` | k largest / smallest series | dashboards, noisy-neighbor hunts |
| `offset 1d` | shift the query back in time | week-over-week comparisons |
| `absent(x)` | 1 if the series is missing | alert when a metric stops reporting |

**Two universal gotchas:**
1. **Range vs instant.** `rate()` needs a **range** vector `[5m]`; comparisons/thresholds need an **instant** vector. Mixing them is the most common PromQL error.
2. **Window length.** Too short = noisy alerts; too long = slow to fire. Golden-signal graphs: `[5m]`. SLO windows: match the SLO period (`[30d]`). Burn-rate: pair a long + short window.
