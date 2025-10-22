# Простой скрипт для остановки FinCloud
Write-Host "🛑 Stopping FinCloud..." -ForegroundColor Red

# Удаляем ресурсы Kubernetes
Write-Host "🗑️ Removing Kubernetes resources..." -ForegroundColor Yellow
kubectl delete -f k8s/frontend.yaml -n fincloud 2>$null
kubectl delete -f k8s/report.yaml -n fincloud 2>$null
kubectl delete -f k8s/finance.yaml -n fincloud 2>$null
kubectl delete -f k8s/auth.yaml -n fincloud 2>$null
kubectl delete -f k8s/postgres.yaml -n fincloud 2>$null
kubectl delete -f k8s/namespace.yaml 2>$null

# Останавливаем Minikube
Write-Host "⏹️ Stopping Minikube..." -ForegroundColor Yellow
minikube stop

Write-Host "✅ FinCloud stopped!" -ForegroundColor Green
