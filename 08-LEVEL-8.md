# Stage 8 — Level 8: AI Reliability

> **The demand:** Give Checkout an ML feature — and then make *that* feature reliable, which is a different and harder problem than making deterministic code reliable.

Now Checkout gains a **fraud-scoring model** (or a recommendation model) on the checkout path. Everything you learned about reliability now meets a component that is probabilistic, drifts, and can fail silently. This is where L1–L7's reliability discipline gets stress-tested against nondeterminism.

---

## Prerequisites (from Stages 1–7)
- The full reliable Checkout, with SLOs, safe deploys, and observability
- A place on the checkout path to insert a model (e.g. fraud check before payment)

## Tasks — one per L8 module (anchored in each module's lab)

1. **Reliability of nondeterministic systems** *(L8-M01 — Lab: Make a Probabilistic System Reliable).* Add the fraud-scoring model to `POST /checkout`. Define what "reliable" even means for a probabilistic component, and set its behavior under uncertainty (thresholds, fallback when unsure).
2. **Data pipeline reliability** *(L8-M02 — Lab: Make a Data Pipeline Reliable).* Build the pipeline that feeds the model (features from cart/order data) and make *it* reliable — validated, monitored, and recoverable. A model is only as reliable as its data.
3. **Training/serving skew** *(L8-M03 — Lab: Hunt and Design Away the Skew).* Deliberately introduce, detect, and then design away a training/serving skew (the model sees different features in prod than in training). Prove you closed the gap.
4. **Evals & model quality SLOs** *(L8-M04 — Lab: Build an Eval That Gates).* Build an eval suite for the fraud model and wire it into the Stage-6 pipeline as a **gate** — a model that fails its quality SLO cannot ship, exactly like failing tests block code.
5. **LLMOps & agent reliability** *(L8-M05 — Lab: Make an Agent Safe by Construction).* Add a small agentic/LLM feature (e.g. a support agent that can look up an order) and make it **safe by construction** — bounded actions, no destructive operations, human confirmation for side effects.
6. **AI-reliable organization** *(L8-M06 — Lab: Make an Organization AI-Reliable).* Assess and document how the org must change to own an ML component reliably — who owns the model, how drift is watched, how evals gate releases.

## The integration twist
The model must live inside **all the reliability machinery you already built**: it's observable via Stage-3 OTel, defended by Stage-4 patterns (a slow model must not stall checkout — circuit-break it, fall back to a rule), deployed via Stage-6 safe delivery (now gated by *both* the error budget *and* the eval suite), and its incidents get Stage-5 blameless postmortems. The AI feature is not special — it's one more part of the socio-technical system, held to the same standards, plus the new ones nondeterminism demands.

## Deliverables
- The fraud model integrated on the checkout path, with a fallback
- A reliable, monitored feature/data pipeline
- A skew detection + fix write-up
- An eval suite wired as a release gate
- A safe-by-construction agent feature
- An AI-reliability org assessment

## Definition of done
- [ ] Model down/slow → checkout still completes (circuit-breaker + rule fallback)
- [ ] The feature pipeline is validated, monitored, and recoverable
- [ ] A training/serving skew was found and eliminated, with evidence
- [ ] A failing eval blocks a model deploy
- [ ] The agent cannot take a destructive action without confirmation
- [ ] Model quality is an SLO, tracked like any other

## Assessment rubric
| Level | Looks like |
|-------|-----------|
| Novice | Model added but bolted on; no fallback; "accuracy" reported once, not tracked |
| Competent | Model defended by existing patterns; eval gate + skew fix done; agent bounded |
| Mastery | The probabilistic component is held to the same reliability bar as the deterministic system; drift and skew are monitored continuously; eval gates are meaningful and the agent is provably safe |
