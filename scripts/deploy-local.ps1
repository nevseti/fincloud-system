# Простой скрипт для деплоя в Minikube
Write-Host "🚀 Deploying FinCloud to Minikube..." -ForegroundColor Green
Write-Host "📝 This script deploys your FinCloud system to Minikube" -ForegroundColor Cyan

# Проверяем Minikube
if (!(minikube status | Select-String "Running")) {
    Write-Host "📦 Starting Minikube..." -ForegroundColor Yellow
    minikube start
}

# Подключаемся к Docker daemon
Write-Host "🔗 Connecting to Minikube Docker..." -ForegroundColor Yellow
minikube docker-env | Invoke-Expression

# Собираем образы
Write-Host "🏗️ Building Docker images..." -ForegroundColor Yellow
docker build -t fincloud-auth:local ./auth-service
docker build -t fincloud-finance:local ./finance-service
docker build -t fincloud-report:local ./report-service
docker build -t fincloud-frontend:local ./frontend

# Деплоим
Write-Host "📋 Deploying to Kubernetes..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres -n fincloud --timeout=300s
kubectl apply -f k8s/auth.yaml
kubectl apply -f k8s/finance.yaml
kubectl apply -f k8s/report.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml

# Проверяем статус
Write-Host "📊 Checking deployment status..." -ForegroundColor Yellow
kubectl get pods -n fincloud
kubectl get services -n fincloud

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Access your app at: http://localhost:8080" -ForegroundColor Cyan
