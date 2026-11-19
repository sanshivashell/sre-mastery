# Stage 1 — Level 1: Foundations

> **The demand:** Make Checkout runnable, version-controlled, and reproducible by anyone, from nothing.

> ⚠️ **Verify against your L1 modules.** The L1 decks/PDFs live in the DevOps Veda book series, not this workspace. This stage is written from the L1 theme and the one L1 module present here (**L1-M08 — Terraform / IaC**). Confirm the exact tools, shell conventions, and module list against your real L1 content and adjust task wording to match.

---

## Prerequisites
None — this is where the system is born.

## Tasks (mapped to L1 themes)

Because L1 is the foundations level (Linux, shell, version control, packaging, and — confirmed present — Infrastructure as Code with Terraform), the stage-1 tasks stand up the raw system and its reproducible base.

1. **Scaffold the service.** Create the Checkout service with its minimum endpoints (`/cart`, `/checkout`, `/order`) and a mock **payments dependency** you fully control (so you can make it fail later). Keep it small.
2. **Shell & runbook hygiene.** Write the `run.sh` / `Makefile` that builds and starts the whole thing locally with one command. Every future stage depends on "one command brings it up."
3. **Version control from commit zero.** Initialize the repo, a sane `.gitignore`, a `README` that a stranger can follow, and a branching convention. Nothing in this capstone is ever un-versioned.
4. **Infrastructure as Code (L1-M08).** Write the Terraform (or your IaC tool) that provisions the base environment the service will run in — network, compute, and the stores Checkout needs (cart store, order store). The environment must be created and destroyed entirely from code.

## The integration twist
Everything you create here must be reproducible **from a clean machine with only the repo**. If a teammate cannot go from `git clone` to a running Checkout using only what is committed, Stage 1 is not done — and every later stage inherits that reproducibility requirement.

## Deliverables
- The Checkout service repo (code + mock payments)
- `run.sh`/`Makefile` — one-command local bring-up
- Terraform/IaC for the base environment
- `README.md` — clone-to-running instructions

## Definition of done
- [ ] `git clone` → one command → Checkout serving requests locally
- [ ] `terraform apply` → base environment exists; `terraform destroy` → it's gone
- [ ] The mock payments dependency can be toggled healthy/slow/down (you'll need this from Stage 3 on)
- [ ] A stranger could follow the README with no other help

## Assessment rubric
| Level | Looks like |
|-------|-----------|
| Novice | Runs on the author's machine; setup steps missing or manual |
| Competent | Clean clone-to-run; IaC provisions the environment reproducibly |
| Mastery | Fully reproducible incl. teardown; payments failure modes already switchable; README is genuinely followable by a newcomer |
