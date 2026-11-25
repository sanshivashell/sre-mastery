#!/usr/bin/env bash
# L1·M06 lab setup: brings up a kind cluster with Argo Rollouts, Kyverno, Prometheus and the sample app,
# plus the lab registry (registry.lab:5000) that the pipeline pushes to.
set -euo pipefail
cd "$(dirname "$0")"

CLUSTER=m06-lab
REGISTRY=registry.lab
REGISTRY_PORT=5000
ARGO_ROLLOUTS_VERSION=v1.10.2
KYVERNO_VERSION=v1.19.2

step() { printf '\n==> %s\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1 || { echo "missing tool: $1 (see README.md, Prerequisites)"; exit 1; }; }
for tool in docker kind kubectl kubectl-argo-rollouts curl; do need "$tool"; done
if ! grep -qE "^[^#]*[[:space:]]${REGISTRY}([[:space:]]|$)" /etc/hosts; then
  echo "add this line to /etc/hosts first:  127.0.0.1 ${REGISTRY}"; exit 1
fi

step "kind cluster ${CLUSTER}"
# kind's network, IPv4 only: on some hosts the IPv6 route to Docker Hub hangs, and the kubelet pulls one image at a
# time, so one stuck pull stalls every pod on the node (found in a real run, 2026-11-25).
docker network inspect kind >/dev/null 2>&1 || docker network create kind >/dev/null
if kind get clusters 2>/dev/null | grep -qx "$CLUSTER"; then echo "already running"
else kind create cluster --config kind.yaml; fi

step "lab registry ${REGISTRY}:${REGISTRY_PORT}"
if [ -z "$(docker ps -q -f name="^${REGISTRY}$")" ]; then
  docker rm -f "$REGISTRY" >/dev/null 2>&1 || true
  docker pull -q registry:3.0.0 >/dev/null
  docker run -d --restart=always --name "$REGISTRY" -p "127.0.0.1:${REGISTRY_PORT}:5000" registry:3.0.0 >/dev/null
fi
docker network connect --alias "$REGISTRY" kind "$REGISTRY" 2>/dev/null || true
for node in $(kind get nodes --name "$CLUSTER"); do       # containerd on each node pulls from the registry over HTTP
  docker exec "$node" mkdir -p "/etc/containerd/certs.d/${REGISTRY}:${REGISTRY_PORT}"
  printf '[host."http://%s:%s"]\n' "$REGISTRY" "$REGISTRY_PORT" | docker exec -i "$node" sh -c "cat > /etc/containerd/certs.d/${REGISTRY}:${REGISTRY_PORT}/hosts.toml"
done
REGISTRY_IP=$(docker inspect -f '{{(index .NetworkSettings.Networks "kind").IPAddress}}' "$REGISTRY")
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}' > /tmp/m06-Corefile
if ! grep -q "$REGISTRY" /tmp/m06-Corefile; then             # pods (Kyverno) resolve the registry by name too
  awk -v ip="$REGISTRY_IP" -v name="$REGISTRY" '{ print }
    /^[[:space:]]*ready$/ { match($0, /^[[:space:]]*/); i = substr($0, 1, RLENGTH)
      print i "hosts {"; print i "    " ip " " name; print i "    fallthrough"; print i "}" }' /tmp/m06-Corefile > /tmp/m06-Corefile.new
  kubectl -n kube-system create configmap coredns --from-file=Corefile=/tmp/m06-Corefile.new --dry-run=client -o yaml | kubectl replace -f - >/dev/null
  kubectl -n kube-system rollout restart deployment coredns >/dev/null
fi
rm -f /tmp/m06-Corefile /tmp/m06-Corefile.new

step "images: pulled once on this machine, then loaded into the cluster"
# The nodes never pull from the internet: a registry address that hangs (seen in a real run) would stall the
# kubelet, which pulls one image at a time. Each image is pulled here with retries and loaded with kind.
ARGO_YAML=$(curl -fsSL "https://github.com/argoproj/argo-rollouts/releases/download/${ARGO_ROLLOUTS_VERSION}/install.yaml")
KYVERNO_YAML=$(curl -fsSL "https://github.com/kyverno/kyverno/releases/download/${KYVERNO_VERSION}/install.yaml" \
  | sed 's/--allowInsecureRegistry=false/--allowInsecureRegistry=true/')
IMAGES=$(printf "%s\n%s\n" "$ARGO_YAML" "$KYVERNO_YAML" | cat - k8s/prometheus.yaml k8s/loadgen.yaml \
  | sed -nE 's/^[[:space:]-]*image:[[:space:]]*"?([^"[:space:]]+)"?.*/\1/p' | sort -u)
for image in $IMAGES; do
  for try in 1 2 3 4 5; do docker pull -q "$image" >/dev/null 2>&1 && break; echo "  retrying $image"; sleep 5; done
done
# One platform only: loading multi-platform images into kind fails ("content digest … not found").
ARCHIVE=$(mktemp -t m06-images.XXXXXX)
docker save --platform "linux/$(docker version -f '{{.Server.Arch}}')" -o "$ARCHIVE" $IMAGES
kind load image-archive --name "$CLUSTER" "$ARCHIVE" >/dev/null
rm -f "$ARCHIVE"
echo "$(echo "$IMAGES" | wc -l | tr -d ' ') images loaded"

step "Argo Rollouts ${ARGO_ROLLOUTS_VERSION}"
kubectl create namespace argo-rollouts --dry-run=client -o yaml | kubectl apply -f - >/dev/null
echo "$ARGO_YAML" | kubectl apply --server-side -n argo-rollouts -f - >/dev/null

step "Kyverno ${KYVERNO_VERSION}"
# The lab registry speaks plain HTTP, so Kyverno must be allowed to read it (set above, in KYVERNO_YAML).
echo "$KYVERNO_YAML" | kubectl apply --server-side -f - >/dev/null

step "Prometheus"
kubectl apply -f k8s/prometheus.yaml >/dev/null

step "sample app (first version, built here)"
docker build -q --build-arg VERSION=setup -t "${REGISTRY}:${REGISTRY_PORT}/sample-app:setup" app >/dev/null
docker push -q "${REGISTRY}:${REGISTRY_PORT}/sample-app:setup" >/dev/null
kubectl create namespace m06 --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl apply -f k8s/service.yaml -f rollout/analysis-success-rate.yaml -f rollout/analysis-p99-latency.yaml -f rollout/rollout.yaml >/dev/null
kubectl apply -f k8s/loadgen.yaml >/dev/null

step "waiting for everything to be ready"
kubectl -n argo-rollouts rollout status deploy/argo-rollouts --timeout=180s
kubectl -n kyverno rollout status deploy/kyverno-admission-controller --timeout=300s
kubectl -n monitoring rollout status deploy/prometheus --timeout=180s
kubectl -n m06 rollout status deploy/loadgen --timeout=120s
kubectl argo rollouts status sample-app -n m06 --timeout 300s

cat <<DONE

Lab ready.
  Rollout:     kubectl argo rollouts get rollout sample-app -n m06 --watch
  Dashboard:   kubectl argo rollouts dashboard            (http://localhost:3100)
  Prometheus:  kubectl -n monitoring port-forward svc/prometheus 9090:9090
  Traffic:     kubectl -n m06 logs -f deploy/loadgen
Next: README.md, step 1.
DONE
