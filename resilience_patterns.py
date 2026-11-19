#!/usr/bin/env python3
"""
resilience_patterns.py — copy-paste-ready reliability patterns.

The defensive patterns an SRE adds to a service: timeout, retry with backoff+jitter,
circuit breaker, bulkhead, rate limiter (token bucket), and load shedding. Each is
minimal, dependency-free, and independently usable. Run for a self-test:
    python3 resilience_patterns.py
"""
from __future__ import annotations
import random
import time
import threading
from collections import deque

# ─────────────────────────────────────────────────────────────────────────
# 1. Retry with exponential backoff + jitter  (L4-M03)
# ─────────────────────────────────────────────────────────────────────────

def retry_with_backoff(fn, max_attempts=5, base=0.1, cap=10.0, jitter=True):
    """Call fn(); on exception retry with exponential backoff and full jitter.

    delay = random(0, min(cap, base * 2**attempt))   # "full jitter"
    Jitter is essential: without it, all clients retry in lockstep and create a
    synchronized retry storm that hammers a recovering dependency.
    """
    attempt = 0
    while True:
        try:
            return fn()
        except Exception:
            attempt += 1
            if attempt >= max_attempts:
                raise
            backoff = min(cap, base * (2 ** attempt))
            delay = random.uniform(0, backoff) if jitter else backoff
            time.sleep(delay)


# ─────────────────────────────────────────────────────────────────────────
# 2. Circuit breaker  (L4-M04)
# ─────────────────────────────────────────────────────────────────────────

class CircuitBreaker:
    """Stops calling a failing dependency so it can recover.

    States: CLOSED (normal) → OPEN (fail fast) → HALF_OPEN (test one) → CLOSED.
    Trips to OPEN after `fail_threshold` consecutive failures; after `reset_timeout`
    it allows one trial call (HALF_OPEN). Success closes it; failure re-opens it.
    """
    CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"

    def __init__(self, fail_threshold=5, reset_timeout=30.0):
        self.fail_threshold = fail_threshold
        self.reset_timeout = reset_timeout
        self.state = self.CLOSED
        self.failures = 0
        self.opened_at = 0.0
        self._lock = threading.Lock()

    def call(self, fn):
        with self._lock:
            if self.state == self.OPEN:
                if time.monotonic() - self.opened_at >= self.reset_timeout:
                    self.state = self.HALF_OPEN
                else:
                    raise RuntimeError("circuit open — failing fast")
        try:
            result = fn()
        except Exception:
            self._on_failure()
            raise
        self._on_success()
        return result

    def _on_success(self):
        with self._lock:
            self.failures = 0
            self.state = self.CLOSED

    def _on_failure(self):
        with self._lock:
            self.failures += 1
            if self.failures >= self.fail_threshold or self.state == self.HALF_OPEN:
                self.state = self.OPEN
                self.opened_at = time.monotonic()


# ─────────────────────────────────────────────────────────────────────────
# 3. Bulkhead — isolate a resource pool  (L4-M04)
# ─────────────────────────────────────────────────────────────────────────

class Bulkhead:
    """Caps concurrent calls to one dependency so it can't consume all capacity.

    Like watertight compartments in a ship: a flood in one (a slow dependency)
    can't sink the whole vessel (exhaust every thread in your service).
    """
    def __init__(self, max_concurrent=10):
        self._sem = threading.Semaphore(max_concurrent)

    def call(self, fn, block=False, timeout=None):
        acquired = self._sem.acquire(blocking=block, timeout=timeout)
        if not acquired:
            raise RuntimeError("bulkhead full — rejecting to protect the service")
        try:
            return fn()
        finally:
            self._sem.release()


# ─────────────────────────────────────────────────────────────────────────
# 4. Token-bucket rate limiter  (L4-M05)
# ─────────────────────────────────────────────────────────────────────────

class TokenBucket:
    """Allow up to `rate` sustained ops/sec with bursts up to `capacity`.

    Tokens refill at `rate`/sec; each call costs one token. Empty bucket ⇒ reject.
    """
    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last = time.monotonic()
        self._lock = threading.Lock()

    def allow(self, cost=1):
        with self._lock:
            now = time.monotonic()
            self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens >= cost:
                self.tokens -= cost
                return True
            return False


# ─────────────────────────────────────────────────────────────────────────
# 5. Load shedding by concurrency  (L4-M05)
# ─────────────────────────────────────────────────────────────────────────

class LoadShedder:
    """Reject work once in-flight exceeds a limit — shed, don't collapse.

    Accepting everything past capacity drives the 1/(1-ρ) latency blow-up and takes
    the whole service down. Shedding trades partial availability for survival.
    """
    def __init__(self, max_inflight=100):
        self.max_inflight = max_inflight
        self.inflight = 0
        self._lock = threading.Lock()

    def __enter__(self):
        with self._lock:
            if self.inflight >= self.max_inflight:
                raise RuntimeError("overloaded — shedding load (503)")
            self.inflight += 1
        return self

    def __exit__(self, *exc):
        with self._lock:
            self.inflight -= 1


# ─────────────────────────────────────────────────────────────────────────
# 6. Timeout wrapper  (L4-M03)
# ─────────────────────────────────────────────────────────────────────────

def call_with_timeout(fn, timeout):
    """Run fn() in a thread; raise TimeoutError if it exceeds `timeout` seconds.

    A missing timeout is the #1 cause of cascading failure: a slow dependency makes
    callers wait, their threads pile up, and the stall propagates backward. Every
    remote call needs a timeout.
    """
    result, error = [None], [None]

    def target():
        try:
            result[0] = fn()
        except Exception as e:  # noqa
            error[0] = e

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        raise TimeoutError(f"call exceeded {timeout}s")
    if error[0]:
        raise error[0]
    return result[0]


# ─────────────────────────────────────────────────────────────────────────
# Self-test
# ─────────────────────────────────────────────────────────────────────────

def _selftest():
    print("=== retry with backoff ===")
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("transient")
        return "ok"
    print(f"result after retries = {retry_with_backoff(flaky, base=0.001)} "
          f"(took {calls['n']} attempts)")

    print("\n=== circuit breaker ===")
    cb = CircuitBreaker(fail_threshold=3, reset_timeout=0.05)
    def always_fail():
        raise RuntimeError("down")
    for i in range(3):
        try: cb.call(always_fail)
        except Exception: pass
    print(f"state after 3 failures = {cb.state}")
    try:
        cb.call(lambda: "x")
    except RuntimeError as e:
        print(f"call while open       = rejected ({e})")
    time.sleep(0.06)
    print(f"recovers on success   = {cb.call(lambda: 'recovered')}, state={cb.state}")

    print("\n=== bulkhead ===")
    bh = Bulkhead(max_concurrent=2)
    print(f"call within limit     = {bh.call(lambda: 'served')}")

    print("\n=== token bucket ===")
    tb = TokenBucket(rate=10, capacity=3)
    results = [tb.allow() for _ in range(5)]
    print(f"5 rapid calls, cap 3  = {results}  (first 3 allowed)")

    print("\n=== load shedder ===")
    ls = LoadShedder(max_inflight=1)
    with ls:
        try:
            with ls:
                pass
        except RuntimeError as e:
            print(f"second concurrent call = shed ({e})")

    print("\n=== timeout ===")
    try:
        call_with_timeout(lambda: time.sleep(1), timeout=0.05)
    except TimeoutError as e:
        print(f"slow call             = {e}")
    print(f"fast call             = {call_with_timeout(lambda: 'quick', timeout=1)}")

    print("\nAll patterns executed OK.")


if __name__ == "__main__":
    _selftest()
