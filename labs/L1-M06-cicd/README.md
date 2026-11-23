# L1·M06 lab: a pipeline with signed images and a canary rollout

The hands-on lab for **Level 1 · Module 6, CI/CD & Deployment Engineering**. You complete a GitHub Actions
pipeline that builds the sample app once, signs the image with keyless cosign, enforces the signature at admission
with Kyverno, and ships through an Argo Rollouts canary that rolls itself back when the SLIs go bad.

Everything runs on your own machine: a kind cluster, a local registry, and a self-hosted GitHub Actions runner that
connects your fork to both.

## What's in this folder

| Path | What it is |
|---|---|
| `app/` | The sample app (Go): three API routes, `/healthz`, Prometheus metrics. Multi-stage Dockerfile, distroless, non-root, base images pinned by digest |
| `setup.sh`, `teardown.sh` | Bring the lab up and take it down |
| `kind.yaml` | The kind cluster (one control plane, one worker) |
| `k8s/` | Prometheus, the app's Service, and a load generator |
| `rollout/` | The Argo Rollout (step 4 starts here) and the two analysis templates: success rate and p99 latency |
| `kyverno/verify-signatures.yaml` | The admission policy for step 3 |
| `solutions/` | Finished versions of the workflow, the rollout and the SBOM policy, plus `SOLUTIONS.md` |
| `../../.github/workflows/l1-m06-cicd.yml` | The starter pipeline you extend |

## Prerequisites

- Docker, with about 4 GB of memory free for the lab
- [kind](https://kind.sigs.k8s.io/) v0.33 or later, `kubectl`, and the
  [Argo Rollouts kubectl plugin](https://argo-rollouts.readthedocs.io/en/stable/installation/#kubectl-plugin-installation) v1.10
- [cosign](https://docs.sigstore.dev/cosign/system_config/installation/) v3 and [Syft](https://github.com/anchore/syft) v1.57 (the runner uses them)
- Your own fork of this repository, with GitHub Actions enabled
- This line in `/etc/hosts`, so your machine and the cluster use the same registry name:

  ```
  127.0.0.1 registry.lab
  ```

  If `docker push registry.lab:5000/...` is refused as insecure, add `registry.lab:5000` to Docker's
  `insecure-registries` (Docker Desktop: Settings → Docker Engine).

## Set up

```bash
git clone https://github.com/<you>/sre-mastery
cd sre-mastery/labs/L1-M06-cicd && ./setup.sh
# Brings up the kind cluster with Argo Rollouts, Kyverno, Prometheus and the sample app
```

### Connect a self-hosted runner

The pipeline pushes to the registry on your machine and deploys to your kind cluster, which GitHub's hosted runners
can't reach. So the jobs run on a self-hosted runner on your machine.

1. In your fork: **Settings → Actions → Runners → New self-hosted runner**. Follow the commands shown, and when
   `config.sh` asks for labels, add `sre-lab`. Start it with `./run.sh`.
2. **Settings → Secrets and variables → Actions → Variables**: add `SRE_LAB_RUNNER` = `true`. Without it the jobs are
   skipped, so pushes never wait on a runner that isn't there.
3. Keep your fork safe while a runner is attached. Under **Settings → Actions → General**, set "Approval for running
   fork pull request workflows" to require approval for all external contributors, so nobody else's code runs on your
   machine. Stop and remove the runner (`./config.sh remove`) when you finish the lab.

In `kyverno/verify-signatures.yaml`, change `sanshivashell` in the subject to your GitHub account or organisation,
so the policy accepts images signed by your fork's workflow.

## The steps

1. **Add a build stage.** Extend `.github/workflows/l1-m06-cicd.yml` with a job that builds the image tagged with the
   commit SHA and pushes it to `registry.lab:5000`.
2. **Sign the image.** Add a cosign signing step with keyless signing through the GitHub OIDC identity provider
   (the job needs `permissions: id-token: write`). Find your signature's entry in Rekor at
   <https://search.sigstore.dev>.
3. **Configure admission.** `kubectl apply -f kyverno/verify-signatures.yaml`, then try to deploy an unsigned image
   and confirm Kyverno rejects it:

   ```bash
   docker build -t registry.lab:5000/sample-app:unsigned app && docker push registry.lab:5000/sample-app:unsigned
   kubectl -n m06 create deployment unsigned --image=registry.lab:5000/sample-app:unsigned
   ```

4. **Configure the canary.** In `rollout/rollout.yaml`, set the steps to 5% → 25% → 100% with a 5-minute analysis
   window after 5% and after 25%, using the `success-rate` and `p99-latency` templates. Apply it.
5. **Deploy a healthy version.** Add a deploy job that sets the Rollout's image to the signed digest. Push a commit
   that changes the app, watch the pipeline build, sign and deploy, and watch the Rollout move through every weight:

   ```bash
   kubectl argo rollouts get rollout sample-app -n m06 --watch
   ```

6. **Deploy a broken version.** The `break-me` branch makes two of the three API routes return 500. Bring your pipeline
   into it and push:

   ```bash
   git checkout break-me && git merge main && git push origin break-me
   ```

   Confirm the canary rolls back on its own during the first analysis window.
7. **Extend.** Generate an SBOM with Syft, attach it to the image as a signed attestation, and require it at admission
   (`solutions/verify-sbom.yaml`).

Stuck? `solutions/SOLUTIONS.md` walks through each step. Try each step yourself first.

## Watching it

| What | Command | Then open |
|---|---|---|
| The Rollout | `kubectl argo rollouts dashboard` | <http://localhost:3100> |
| Prometheus | `kubectl -n monitoring port-forward svc/prometheus 9090:9090` | <http://localhost:9090> |
| Traffic | `kubectl -n m06 logs -f deploy/loadgen` | |

The canary's success rate, the query the analysis runs, in Prometheus:

```promql
sum(rate(http_requests_total{service="sample-app",status!~"5.."}[5m])) by (rollouts_pod_template_hash)
/ sum(rate(http_requests_total{service="sample-app"}[5m])) by (rollouts_pod_template_hash)
```

## Clean up

```bash
./teardown.sh
```

Then remove the self-hosted runner from your fork.

## Versions used

kind v0.33.0 · Kubernetes from kind's default node image · Argo Rollouts v1.10.2 · Kyverno v1.19.2 ·
Prometheus v3.16.0 · cosign v3.1.4 · Syft v1.57.1 · registry 3.0.0 · Go 1.27
