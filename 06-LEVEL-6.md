# Stage 6 — Level 6: Delivery & Security

> **The demand:** Make shipping Checkout *safe*, its secrets and data protected, its supply chain trusted, and its recovery proven.

Stage 2 built a pipeline. Stage 6 makes that pipeline **safe** — gated by the error budget, protected against bad releases, secure by design, and recoverable when data goes wrong.

---

## Prerequisites (from Stages 2, 3, 5)
- CI/CD pipeline (Stage 2)
- Observability + SLOs (Stage 3)
- Error-budget policy (Stage 5) — this now gates deploys

## Tasks — one per L6 module (anchored in each module's lab)

1. **Release engineering & safe deployment** *(L6-M01 — Lab: Build a Safe Deployment Path).* Add progressive delivery to the pipeline: canary or blue-green with automated health checks on the North-Star metric, and automatic rollback. The error budget (Stage 5) can block a release.
2. **Configuration & secrets** *(L6-M02 — Lab: Govern Config, Contain a Secret).* Move all config to a governed source and all secrets to a proper secrets manager. Then run the drill: rotate/contain a leaked secret without downtime.
3. **Security for SREs** *(L6-M03 — Lab: Threat Model, Then Contain a Breach).* Threat-model Checkout (what would an attacker do to the payment path?), then simulate and contain a breach scenario.
4. **Infrastructure as code** *(L6-M04 — Lab: Codify, Reconcile, Change Safely).* Bring *all* infra under IaC with drift detection and safe change (plan/review/apply). Extends Stage-1 Terraform to the whole system, reconciled continuously.
5. **Data reliability** *(L6-M05 — Lab: Prove Recovery, Migrate Safely).* Prove the order/cart data can be recovered (backups + restore test, building on Stage-4 DR), and perform one safe schema migration with no data loss and no downtime.
6. **Dependency & supply-chain reliability** *(L6-M06 — Lab: Inventory, Harden, Survive).* Inventory Checkout's dependencies (incl. the container base images), harden the supply chain (pinning, scanning, SBOM), and show the system survives a poisoned/removed dependency.
7. **Reliability as an organization** *(L6-M07 — Lab: Assess Your Organisation).* Assess the org practices around Checkout: who owns reliability, how error budgets are honored, how on-call is staffed. Produce a maturity assessment.

## The integration twist
The safe-deployment path (task 1) must be **gated by the error budget from Stage 5** — if the budget is spent, releases stop. This couples delivery to reliability: you cannot ship your way through an SLO breach. And every safe-deploy must be **observable via Stage-3 signals**, with rollback triggered by the North-Star metric, not a human's gut.

## Deliverables
- Progressive-delivery pipeline with automated rollback
- Config in a governed store; secrets in a manager; a rotation drill log
- A threat model + breach-containment exercise write-up
- Full-system IaC with drift detection
- A performed schema migration + data-recovery test
- Dependency inventory, SBOM, and a survived-dependency-failure demo
- An organizational reliability maturity assessment

## Definition of done
- [ ] Bad release auto-rolls-back on North-Star metric regression
- [ ] Error budget can block a deploy
- [ ] No secrets in code or config; rotation drill passed
- [ ] Threat model exists; a breach scenario was contained
- [ ] All infra is IaC with drift detection
- [ ] A real schema migration performed with zero data loss
- [ ] Supply chain inventoried and hardened

## Assessment rubric
| Level | Looks like |
|-------|-----------|
| Novice | Canary exists but rollback is manual; secrets partly in config |
| Competent | Auto-rollback on metric; secrets managed; IaC + migration + threat model done |
| Mastery | Deploys gated by error budget; breach + dependency failure both survived and evidenced; migration was zero-downtime; org assessment is honest and actionable |
