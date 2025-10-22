Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "=== FinCloud: fresh local start ===" -ForegroundColor Green

# 1) Stop previous cluster (ignore errors)
try {
    Write-Host "Stopping previous Minikube (if any)..." -ForegroundColor Yellow
    minikube stop | Out-Null
} catch {}

# 2) Start Minikube (use mirror if needed)
$useMirror = $env:FINCLOUD_USE_MIRROR -eq '1'
if ($useMirror) {
    Write-Host "Starting Minikube with image mirror..." -ForegroundColor Yellow
    minikube start --image-repository=registry.cn-hangzhou.aliyuncs.com/google_containers
} else {
    Write-Host "Starting Minikube..." -ForegroundColor Yellow
    minikube start
}

# 3) Point PowerShell to Minikube Docker daemon
Write-Host "Configuring Docker to use Minikube daemon..." -ForegroundColor Yellow
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# 4) Build local images
Write-Host "Building local Docker images..." -ForegroundColor Yellow
docker build -t fincloud-auth:local ./auth-service
docker build -t fincloud-finance:local ./finance-service
docker build -t fincloud-report:local ./report-service
docker build -t fincloud-frontend:local ./frontend

# 5) Ensure images available inside cluster (defensive)
Write-Host "Loading images into Minikube cache..." -ForegroundColor Yellow
minikube image load fincloud-auth:local
minikube image load fincloud-finance:local
minikube image load fincloud-report:local
minikube image load fincloud-frontend:local

# 6) Apply Kubernetes manifests
Write-Host "Applying Kubernetes manifests..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres.yaml
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=postgres -n fincloud --timeout=300s
kubectl apply -f k8s/auth.yaml
kubectl apply -f k8s/finance.yaml
kubectl apply -f k8s/report.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml

# 7) Enable ingress
Write-Host "Ensuring ingress addon is enabled..." -ForegroundColor Yellow
minikube addons enable ingress | Out-Null

# 8) Show status
Write-Host "\nPods:" -ForegroundColor Cyan
kubectl get pods -n fincloud
Write-Host "\nServices:" -ForegroundColor Cyan
kubectl get svc -n fincloud
Write-Host "\nIngress:" -ForegroundColor Cyan
kubectl get ingress -n fincloud

Write-Host "\nFrontend access:" -ForegroundColor Cyan
Write-Host " - Option 1: port-forward -> kubectl port-forward svc/fincloud-frontend 8080:80 -n fincloud" -ForegroundColor White
Write-Host " - Option 2: ingress -> run 'minikube tunnel' in a separate window" -ForegroundColor White

Write-Host "=== FinCloud: ready ===" -ForegroundColor Green



