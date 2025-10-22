# FinCloud Docker Swarm Deployment Script
Write-Host "Deploying FinCloud to Docker Swarm..." -ForegroundColor Green

# Check if Docker Swarm is initialized
$swarmInfo = docker info --format "{{.Swarm.LocalNodeState}}" 2>$null
if ($swarmInfo -ne "active") {
    Write-Host "Initializing Docker Swarm..." -ForegroundColor Yellow
    docker swarm init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to initialize Docker Swarm" -ForegroundColor Red
        exit 1
    }
}

# Build images
Write-Host "Building Docker images..." -ForegroundColor Yellow
docker build -t fincloud-auth:local ./auth-service
docker build -t fincloud-finance:local ./finance-service
docker build -t fincloud-report:local ./report-service
docker build -t fincloud-frontend:local ./frontend

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build images" -ForegroundColor Red
    exit 1
}

# Deploy stack
Write-Host "Deploying stack..." -ForegroundColor Yellow
docker stack deploy -c docker-compose.swarm.yml fincloud

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to deploy stack" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Show status
Write-Host "Stack Status:" -ForegroundColor Green
docker stack services fincloud

Write-Host "Access URLs:" -ForegroundColor Green
Write-Host "Frontend: http://localhost" -ForegroundColor Cyan
Write-Host "Auth API: http://localhost/auth" -ForegroundColor Cyan
Write-Host "Finance API: http://localhost/finance" -ForegroundColor Cyan
Write-Host "Reports API: http://localhost/reports" -ForegroundColor Cyan

Write-Host "FinCloud deployed successfully!" -ForegroundColor Green