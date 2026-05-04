# devops-app - Production-Grade DevOps Portfolio Project

A complete DevOps platform demonstrating CI/CD, GitOps, container orchestration, and observability.

## Architecture

\Developer pushes code
        |
        v
+----------------------------------+
|        GitHub Actions CI         |
|  test > lint > build > scan      |
|  > push ECR > update GitOps      |
+---------------+------------------+
                |
                v
+----------------------------------+
|        devops-gitops repo        |
|   Helm charts + values.yaml      |
+---------------+------------------+
                |  ArgoCD polls every 3 min
                v
+----------------------------------+
|        Kubernetes (EKS)          |
|  production namespace            |
|  +-- Deployment (2-10 replicas)  |
|  +-- Service (ClusterIP)         |
|  +-- HPA (CPU/memory based)      |
|  +-- ServiceMonitor              |
|  +-- PrometheusRule              |
+---------------+------------------+
                |  scrapes /metrics
                v
+----------------------------------+
|       Observability Stack        |
|  Prometheus > Grafana dashboards |
|  AlertManager > alert rules      |
+----------------------------------+
\
## Tech Stack

| Layer | Technology |
|---|---|
| Application | Python 3.11, FastAPI, prometheus-client |
| Containerisation | Docker (non-root, layer-cached) |
| Container Registry | AWS ECR (scan on push) |
| CI Pipeline | GitHub Actions |
| Security Scanning | Trivy (blocks on CRITICAL CVEs) |
| Infrastructure | AWS EKS, Terraform |
| Package Management | Helm |
| GitOps | ArgoCD (automated sync, self-heal) |
| Observability | Prometheus, Grafana, AlertManager |
| Autoscaling | Kubernetes HPA (CPU + memory) |

## How a Deployment Works

1. Developer pushes code to \main\ branch
2. GitHub Actions triggers:
   - Runs pytest tests and ruff linter
   - Builds Docker image tagged with git SHA
   - Scans with Trivy - blocks on CRITICAL CVEs
   - Pushes to AWS ECR
   - Updates image tag in devops-gitops values.yaml
3. ArgoCD detects values.yaml change within 3 minutes
4. ArgoCD applies Helm chart to production namespace on EKS
5. Kubernetes performs rolling update - zero downtime
6. Prometheus scrapes new pods via ServiceMonitor within 15s
7. Grafana dashboards reflect live metrics

## Rolling Back

\\ash
git revert HEAD
git push
# ArgoCD detects revert and redeploys previous image automatically
\
## Repository Structure

\devops-app/                         (this repo - application code)
+-- .github/
|   +-- workflows/
|   |   +-- ci.yml                  (GitHub Actions pipeline)
|   +-- argocd/
|       +-- application.yaml        (ArgoCD app definition)
+-- app/
|   +-- main.py                     (FastAPI app with /metrics)
|   +-- routes/
|       +-- health.py               (/health and /ready endpoints)
+-- tests/                          (pytest test suite)
+-- k8s/                            (local dev manifests only)
+-- scripts/
|   +-- refresh-ecr-secret.ps1      (ECR token refresh helper)
+-- Dockerfile                      (non-root, layer-cached)
+-- requirements.txt

devops-gitops/                      (separate repo - GitOps source of truth)
+-- charts/
    +-- devops-app/
        +-- Chart.yaml
        +-- values.yaml             (CI updates image.tag on every deploy)
        +-- templates/
            +-- deployment.yaml
            +-- service.yaml
            +-- hpa.yaml
            +-- servicemonitor.yaml
            +-- prometheusrule.yaml
\
## Running Locally

Prerequisites: Docker Desktop with Kubernetes, kubectl, helm, AWS CLI

\\powershell
# 1. Refresh ECR pull secret after every restart
./scripts/refresh-ecr-secret.ps1

# 2. Start port-forwards (separate terminals)
kubectl port-forward svc/argocd-server -n argocd 8090:443
kubectl port-forward svc/devops-app -n production 8081:80
kubectl port-forward svc/kube-prom-stack-grafana -n monitoring 3000:80
kubectl port-forward svc/kube-prom-stack-kube-prome-prometheus -n monitoring 9090:9090

# 3. Test
Invoke-RestMethod http://localhost:8081/health
\
## Access Points

| Service | URL | Credentials |
|---|---|---|
| Application | http://localhost:8081 | - |
| ArgoCD UI | https://localhost:8090 | admin / kubectl get secret |
| Grafana | http://localhost:3000 | admin / admin123 |
| Prometheus | http://localhost:9090 | - |

## Observability

Grafana Dashboards:
- devops-app overview: requests/sec by pod, p95 latency, available replicas
- Kubernetes cluster overview (ID: 15760)
- Node exporter (ID: 1860)

Alert Rules:

| Alert | Condition | Severity |
|---|---|---|
| AppPodsDown | Available replicas < 2 for 1 min | Critical |
| HighRequestLatency | p95 latency > 500ms for 2 min | Warning |

## Security

- Docker image runs as non-root user (appuser)
- Trivy scans every image - CRITICAL CVEs block deployment
- AWS ECR scan on push enabled
- GitHub Actions pinned to specific versions after March 2026 supply chain incident
- ECR auth via docker-registry secret locally / IRSA for production EKS

## Key Design Decisions

**Why two repos?**
Clean separation between app code and deployment config. The gitops repo is the single source of truth - nothing deploys except through Git.

**Why ArgoCD over kubectl apply in CI?**
Self-healing, audit trail, and instant rollback by reverting a git commit.

**Why SHA-based image tags?**
Using latest makes deployments non-deterministic. SHA tags make every deploy traceable to a specific commit.

**Why Trivy exit-code 1?**
Turns scanner into a hard security gate. No CRITICAL vulnerability can reach production.

## Cost Estimate (AWS)

| Resource | Cost |
|---|---|
| EKS cluster | ~\.10/hour |
| 2x t3.medium nodes | ~\.083/hour |
| ECR storage | ~\.01/GB/month |
| Total running | ~\.50/day |

Tip: Run terraform destroy when not demoing. Rebuilding takes 15 minutes.

## What I Learned

- GitOps pattern and why Git as source of truth eliminates config drift
- How Prometheus ServiceMonitor CRDs wire scrape targets automatically
- Why ECR tokens expire and how IRSA solves this on EKS
- Supply chain attack awareness and why pinning Action versions matters
- Rolling update mechanics and how readiness probes gate traffic
