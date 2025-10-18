# Скрипт для остановки FinCloud в Minikube
Write-Host "🛑 Остановка FinCloud в Minikube..." -ForegroundColor Red

# Удаляем ресурсы
Write-Host "🗑️ Удаляем ресурсы Kubernetes..." -ForegroundColor Yellow
kubectl delete -f k8s/frontend.yaml
kubectl delete -f k8s/report.yaml
kubectl delete -f k8s/finance.yaml
kubectl delete -f k8s/auth.yaml
kubectl delete -f k8s/postgres.yaml
kubectl delete -f k8s/namespace.yaml

# Останавливаем Minikube
Write-Host "⏹️ Останавливаем Minikube..." -ForegroundColor Yellow
minikube stop

Write-Host "✅ Система остановлена!" -ForegroundColor Green

