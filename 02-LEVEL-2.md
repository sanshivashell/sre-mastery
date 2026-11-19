# Stage 2 — Level 2: Automation & CI

> **The demand:** Make Checkout build, test, and deploy itself through a pipeline — no manual steps.

> ⚠️ **Verify against your L2 modules.** No L2 decks/PDFs are present in this workspace (they're in the book series). This stage is written from the standard L2 theme (automation, scripting, CI/CD, containerization). **Confirm the exact L2 module list and tools and adjust** — a Cowork lookup of the L2 decks will pin the specifics.

---

## Prerequisites (from Stage 1)
- Checkout runs locally with one command
- Base environment exists as IaC
- Repo with a branching convention

## Tasks (mapped to L2 themes)

1. **Containerize.** Package Checkout and its mock payments into containers so the artifact that runs in CI is the artifact that runs everywhere. Kill "works on my machine" for good.
2. **Automated build & test.** A CI pipeline that, on every push, builds the container, runs unit/integration tests, and fails the build if anything is red. No green build, no merge.
3. **Automated deploy.** Extend the pipeline to deploy to the Stage-1 IaC environment automatically on merge to main. Deployment is a pipeline event, never a human running commands.
4. **Environment parity.** Ensure the pipeline deploys the *same* artifact to a staging-like environment first. (You'll lean on this hard in Stage 6's safe-deploy work.)

## The integration twist
The pipeline must deploy **the exact IaC environment from Stage 1** — CI and IaC are now coupled. If someone changes the infrastructure, it flows through the same pipeline; if someone changes the code, it lands in the same environment. One path to production, from here on.

## Deliverables
- Dockerfiles / container definitions for Checkout + payments
- CI pipeline config (build → test → deploy)
- A staging environment the pipeline targets before prod
- Short note: what your pipeline gates on, and why

## Definition of done
- [ ] Push → CI builds the container and runs tests automatically
- [ ] Red tests block the merge
- [ ] Merge to main → automatic deploy to the IaC environment
- [ ] The artifact tested in CI is byte-for-byte the artifact deployed

## Assessment rubric
| Level | Looks like |
|-------|-----------|
| Novice | CI runs tests but deploy is still manual |
| Competent | Full build→test→deploy pipeline; same artifact throughout |
| Mastery | Code *and* infra flow through one gated pipeline; staging parity in place; the pipeline is itself defined as code |
