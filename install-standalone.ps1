# K-Sphere One-Click Installer for Windows (PowerShell)
# This script downloads and sets up K-Sphere with zero configuration

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  K-Sphere One-Click Installer (Windows)   " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing Docker Desktop:" -ForegroundColor Yellow
    Write-Host "1. Start Docker Desktop" -ForegroundColor Yellow
    Write-Host "2. Wait for it to finish starting" -ForegroundColor Yellow
    Write-Host "3. Run this installer again" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if Docker is running
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is installed but not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✓ Docker is installed and running" -ForegroundColor Green
Write-Host ""

# Set installation directory
$INSTALL_DIR = "$HOME\k-sphere"
Write-Host "Installation directory: $INSTALL_DIR" -ForegroundColor Cyan
Write-Host ""

# Create installation directory
if (Test-Path $INSTALL_DIR) {
    Write-Host "Directory already exists. Cleaning up..." -ForegroundColor Yellow
    Remove-Item -Path $INSTALL_DIR -Recurse -Force
}
New-Item -ItemType Directory -Path $INSTALL_DIR | Out-Null

# Download K-Sphere
Write-Host "Downloading K-Sphere..." -ForegroundColor Yellow
$DOWNLOAD_URL = "https://github.com/YOUR_USERNAME/k-sphere/archive/refs/heads/main.zip"
$ZIP_FILE = "$INSTALL_DIR\k-sphere.zip"

try {
    Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $ZIP_FILE
    Write-Host "✓ Download complete" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to download K-Sphere" -ForegroundColor Red
    Write-Host "Please check your internet connection and try again." -ForegroundColor Yellow
    pause
    exit 1
}

# Extract archive
Write-Host "Extracting files..." -ForegroundColor Yellow
Expand-Archive -Path $ZIP_FILE -DestinationPath $INSTALL_DIR -Force
Remove-Item $ZIP_FILE

# Find the extracted directory (GitHub adds -main suffix)
$extractedDir = Get-ChildItem -Path $INSTALL_DIR -Directory | Select-Object -First 1
if ($extractedDir) {
    Get-ChildItem -Path $extractedDir.FullName | Move-Item -Destination $INSTALL_DIR
    Remove-Item $extractedDir.FullName -Recurse
}
Write-Host "✓ Files extracted" -ForegroundColor Green
Write-Host ""

# Navigate to installation directory
Set-Location $INSTALL_DIR

# Create .env files
Write-Host "Creating configuration files..." -ForegroundColor Yellow

# Backend .env
$backendEnv = @"
# Backend Configuration
ENVIRONMENT=production
OLLAMA_HOST=http://ollama:11434
FRONTEND_URL=http://localhost:3000
"@
Set-Content -Path "k-sphere-backend\.env" -Value $backendEnv

# Frontend .env.local
$frontendEnv = @"
# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
"@
Set-Content -Path "k-sphere-frontend\.env.local" -Value $frontendEnv

Write-Host "✓ Configuration files created" -ForegroundColor Green
Write-Host ""

# Start Docker Compose
Write-Host "Starting K-Sphere services..." -ForegroundColor Yellow
Write-Host "This will take a few minutes on first run..." -ForegroundColor Yellow
Write-Host ""

docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start services" -ForegroundColor Red
    Write-Host "Check the logs with: docker-compose logs" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "✓ Services started successfully!" -ForegroundColor Green
Write-Host ""

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
$maxAttempts = 60
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Backend is ready!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }
}

Write-Host ""
Write-Host ""

# Download Ollama model
Write-Host "Downloading AI model (llama3.2:1b)..." -ForegroundColor Yellow
Write-Host "This is a one-time download (1-2 GB)..." -ForegroundColor Yellow
Write-Host ""

docker-compose exec -T ollama ollama pull llama3.2:1b

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Model downloaded successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Warning: Model download may have failed" -ForegroundColor Yellow
    Write-Host "You can download it later from the settings page" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  K-Sphere is now running!                 " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access K-Sphere at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  Stop K-Sphere:    docker-compose stop" -ForegroundColor White
Write-Host "  Start K-Sphere:   docker-compose start" -ForegroundColor White
Write-Host "  View logs:        docker-compose logs -f" -ForegroundColor White
Write-Host "  Uninstall:        docker-compose down -v" -ForegroundColor White
Write-Host ""
Write-Host "Installation directory: $INSTALL_DIR" -ForegroundColor Cyan
Write-Host ""

# Open browser
Write-Host "Opening K-Sphere in your browser..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Installation complete! Enjoy using K-Sphere!" -ForegroundColor Green
Write-Host ""
pause
