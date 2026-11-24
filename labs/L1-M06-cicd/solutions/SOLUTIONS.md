# L1·M06 lab: solutions

Try each step before reading its solution.

## Steps 1, 2, 5 and 7: the pipeline

The finished pipeline is `l1-m06-cicd.yml` in this folder. To use it:

```bash
cp labs/L1-M06-cicd/solutions/l1-m06-cicd.yml .github/workflows/l1-m06-cicd.yml
git commit -am "M06 lab: complete the pipeline" && git push
```

- **Build once.** The `build` job tags the image with the commit SHA, pushes it, and passes the pushed **digest** to
  the later jobs. Signing, the SBOM and the deploy all use that digest, so the image that was signed is exactly the
  image that runs.
- **Keyless signing.** The `sign` job has `id-token: write`, so GitHub issues it an OIDC token. `cosign sign` exchanges
  that token for a short-lived certificate naming the workflow, signs the digest, and records the signature in Rekor.
  No key is stored anywhere. The job log prints the Rekor log index; look it up at <https://search.sigstore.dev>.
- **Two flags on cosign.** `--new-bundle-format=false --use-signing-config=false` keep cosign v3 on the classic
  signature format, the one Kyverno's ClusterPolicy verifies and a plain `registry:3` can serve (cosign v3's default
  Sigstore bundles are stored as OCI referrers, which neither reads).
- **SBOM.** Syft lists every package in the image (`-o table` prints it in the job log); `cosign attest` attaches the
  SPDX document to the image as a signed attestation, and the workflow also uploads it as a build artifact.
- **Deploy.** The `deploy` job applies `rollout/rollout.yaml` with the signed digest in place of the image, so the
  canary steps you commit and the image you built ship together; Argo Rollouts takes it from there.

Check a signature yourself:

```bash
cosign verify --allow-http-registry \
  --certificate-identity-regexp '^https://github.com/<you>/sre-mastery/.github/workflows/l1-m06-cicd.yml@' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  registry.lab:5000/sample-app@sha256:<digest>
```

## Step 3: admission

`kyverno/verify-signatures.yaml` makes Kyverno check every Pod in namespace `m06` that runs an image from
`registry.lab:5000`: the image must carry a keyless signature from your fork's lab workflow, recorded in Rekor.
The policy's `roots` is Sigstore's public certificate authority (Fulcio): keyless certificates are issued by it, and
naming it lets Kyverno verify them without fetching Sigstore's trust root at start-up.
The unsigned image in the README is rejected at admission. So is an image someone replaces in the registry
under a tag that was signed, because the new content has a new digest and no signature.

## Step 4: the canary

`rollout.yaml` in this folder has the finished steps: 5% → analysis → 25% → analysis → 100%. Each analysis runs both
templates for 10 measurements, 30 seconds apart: a 5-minute window. With 20 replicas, 5% is exactly one pod.
Copy it over `rollout/rollout.yaml`, commit and push: the pipeline applies it with the signed digest.

## Step 6: the broken version

On `break-me`, `/api/items` and `/api/checkout` return 500, so the canary's success rate falls to around 40%, far
below the 99% the template requires. Latency stays fine, so only the success-rate check fails: three failed
measurements (more than `failureLimit: 2`), about two minutes into the first analysis window. The AnalysisRun fails
and Argo Rollouts aborts: the canary scales to zero and all traffic stays on the stable version. In the load
generator's log, the `other=` count (the canary's 500s) drops back to 0.
`kubectl argo rollouts get rollout sample-app -n m06` shows the rollout as Degraded, with the abort message.
To go back: `kubectl argo rollouts undo sample-app -n m06`, or push a fixed commit.
