# Простой скрипт для проверки FinCloud
Write-Host "🔍 Checking FinCloud status..." -ForegroundColor Cyan

# Проверяем Minikube
Write-Host "`n📊 Minikube status:" -ForegroundColor Yellow
minikube status

# Проверяем Pod'ы
Write-Host "`n📦 Pods status:" -ForegroundColor Yellow
kubectl get pods -n fincloud

# Проверяем сервисы
Write-Host "`n🌐 Services status:" -ForegroundColor Yellow
kubectl get services -n fincloud

# Проверяем доступность
Write-Host "`n🌍 Checking accessibility:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri http://localhost:8080 -Method GET -TimeoutSec 5
    Write-Host "✅ Frontend accessible at http://localhost:8080" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend not accessible. Run port-forward:" -ForegroundColor Red
    Write-Host "kubectl port-forward service/fincloud-frontend 8080:80 -n fincloud" -ForegroundColor Yellow
}

Write-Host "`n📋 Quick commands:" -ForegroundColor Cyan
Write-Host "• Deploy: .\scripts\deploy-local.ps1" -ForegroundColor White
Write-Host "• Stop: .\scripts\stop-local.ps1" -ForegroundColor White
Write-Host "• Check: .\scripts\check-local.ps1" -ForegroundColor White
