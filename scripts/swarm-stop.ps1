# FinCloud Docker Swarm Stop Script
Write-Host "🛑 Stopping FinCloud Docker Swarm..." -ForegroundColor Red

# Remove stack
Write-Host "Removing stack..." -ForegroundColor Yellow
docker stack rm fincloud

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to remove stack" -ForegroundColor Red
    exit 1
}

# Wait for services to stop
Write-Host "Waiting for services to stop..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Show remaining services
Write-Host "`n📊 Remaining Services:" -ForegroundColor Green
docker service ls

Write-Host "`n✅ FinCloud stopped successfully!" -ForegroundColor Green
