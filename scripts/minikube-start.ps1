# Скрипт для запуска FinCloud в Minikube
Write-Host "🚀 Запуск FinCloud в Minikube..." -ForegroundColor Green

# Проверяем, запущен ли Minikube
$minikubeStatus = minikube status --format json | ConvertFrom-Json
if ($minikubeStatus.Host -ne "Running") {
    Write-Host "📦 Запускаем Minikube..." -ForegroundColor Yellow
    minikube start
}

# Подключаемся к Docker daemon Minikube
Write-Host "🔗 Подключаемся к Docker daemon Minikube..." -ForegroundColor Yellow
minikube docker-env | Invoke-Expression

# Собираем образы
Write-Host "🏗️ Собираем Docker образы..." -ForegroundColor Yellow
docker build -t fincloud-auth:local ./auth-service
docker build -t fincloud-finance:local ./finance-service
docker build -t fincloud-report:local ./report-service
docker build -t fincloud-frontend:local ./frontend

# Применяем конфигурации K8s
Write-Host "📋 Применяем конфигурации Kubernetes..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres.yaml

# Ждем готовности PostgreSQL
Write-Host "⏳ Ждем готовности PostgreSQL..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=postgres -n fincloud --timeout=300s

# Запускаем сервисы
Write-Host "🚀 Запускаем сервисы..." -ForegroundColor Yellow
kubectl apply -f k8s/auth.yaml
kubectl apply -f k8s/finance.yaml
kubectl apply -f k8s/report.yaml
kubectl apply -f k8s/frontend.yaml

# Включаем Ingress
Write-Host "🌐 Настраиваем Ingress..." -ForegroundColor Yellow
minikube addons enable ingress

# Показываем статус
Write-Host "✅ Система запущена!" -ForegroundColor Green
Write-Host "📊 Статус Pod'ов:" -ForegroundColor Cyan
kubectl get pods -n fincloud

Write-Host "🌐 Для доступа к приложению:" -ForegroundColor Cyan
Write-Host "   minikube ip" -ForegroundColor White
Write-Host "   Добавьте IP в hosts файл как fincloud.local" -ForegroundColor White
Write-Host "   Или используйте: kubectl port-forward service/fincloud-frontend 8080:80 -n fincloud" -ForegroundColor White

