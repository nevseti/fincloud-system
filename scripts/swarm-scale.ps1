# FinCloud Docker Swarm Scale Script
param(
    [Parameter(Mandatory=$true)]
    [string]$Service,
    [Parameter(Mandatory=$true)]
    [int]$Replicas
)

Write-Host "📈 Scaling FinCloud service: $Service to $Replicas replicas" -ForegroundColor Green

# Scale service
docker service scale "fincloud_$Service"=$Replicas

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to scale service" -ForegroundColor Red
    exit 1
}

# Show updated status
Write-Host "`n📊 Updated Service Status:" -ForegroundColor Yellow
docker service ls --filter name=fincloud_$Service

Write-Host "`n✅ Service scaled successfully!" -ForegroundColor Green
