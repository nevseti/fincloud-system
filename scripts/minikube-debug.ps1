# Скрипт для отладки FinCloud в Minikube
Write-Host "🔍 Отладка FinCloud в Minikube..." -ForegroundColor Cyan

# Проверяем статус Minikube
Write-Host "📊 Статус Minikube:" -ForegroundColor Yellow
minikube status

# Проверяем Pod'ы
Write-Host "`n📦 Статус Pod'ов:" -ForegroundColor Yellow
kubectl get pods -n fincloud

# Проверяем сервисы
Write-Host "`n🌐 Статус сервисов:" -ForegroundColor Yellow
kubectl get services -n fincloud

# Проверяем развертывания
Write-Host "`n🚀 Статус развертываний:" -ForegroundColor Yellow
kubectl get deployments -n fincloud

# Показываем события
Write-Host "`n📋 Последние события:" -ForegroundColor Yellow
kubectl get events -n fincloud --sort-by='.lastTimestamp' | Select-Object -Last 10

# Проверяем логи проблемных Pod'ов
Write-Host "`n📝 Логи проблемных Pod'ов:" -ForegroundColor Yellow
$failedPods = kubectl get pods -n fincloud --field-selector=status.phase!=Running -o name
if ($failedPods) {
    foreach ($pod in $failedPods) {
        Write-Host "`n🔍 Логи $pod:" -ForegroundColor Red
        kubectl logs $pod -n fincloud --tail=20
    }
} else {
    Write-Host "✅ Все Pod'ы работают нормально!" -ForegroundColor Green
}

Write-Host "`n💡 Полезные команды для дальнейшей отладки:" -ForegroundColor Cyan
Write-Host "   kubectl describe pod <pod-name> -n fincloud" -ForegroundColor White
Write-Host "   kubectl logs -f <pod-name> -n fincloud" -ForegroundColor White
Write-Host "   kubectl exec -it <pod-name> -n fincloud -- /bin/bash" -ForegroundColor White

