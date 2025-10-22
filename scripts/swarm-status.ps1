# FinCloud Docker Swarm Status Script
Write-Host "📊 FinCloud Docker Swarm Status" -ForegroundColor Green

# Check if stack exists
$stackExists = docker stack ls --format "{{.Name}}" | Select-String "fincloud"
if (-not $stackExists) {
    Write-Host "❌ FinCloud stack is not deployed" -ForegroundColor Red
    exit 1
}

# Show stack services
Write-Host "`n🐳 Stack Services:" -ForegroundColor Yellow
docker stack services fincloud

# Show service details
Write-Host "`n📋 Service Details:" -ForegroundColor Yellow
docker service ls --format "table {{.Name}}\t{{.Mode}}\t{{.Replicas}}\t{{.Image}}\t{{.Ports}}"

# Show running containers
Write-Host "`n🏃 Running Containers:" -ForegroundColor Yellow
docker service ps fincloud_postgres --no-trunc
docker service ps fincloud_auth-service --no-trunc
docker service ps fincloud_finance-service --no-trunc
docker service ps fincloud_report-service --no-trunc
docker service ps fincloud_frontend --no-trunc
docker service ps fincloud_nginx --no-trunc

# Show logs for each service
Write-Host "`n📝 Recent Logs:" -ForegroundColor Yellow
Write-Host "--- Auth Service ---" -ForegroundColor Cyan
docker service logs fincloud_auth-service --tail 5

Write-Host "`n--- Finance Service ---" -ForegroundColor Cyan
docker service logs fincloud_finance-service --tail 5

Write-Host "`n--- Report Service ---" -ForegroundColor Cyan
docker service logs fincloud_report-service --tail 5

Write-Host "`n--- Frontend ---" -ForegroundColor Cyan
docker service logs fincloud_frontend --tail 5

Write-Host "`n--- Nginx ---" -ForegroundColor Cyan
docker service logs fincloud_nginx --tail 5

Write-Host "`n✅ Status check completed!" -ForegroundColor Green
