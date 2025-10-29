@echo off
setlocal enabledelayedexpansion

:: Colors for Windows (using echo with special characters)
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RED=[91m"
set "NC=[0m"

echo %BLUE%
echo ╔══════════════════════════════════════════════╗
echo ║         K-Sphere Installation Script         ║
echo ║      Portable AI Knowledge Management        ║
echo ╚══════════════════════════════════════════════╝
echo %NC%

:: Check if Docker is installed
echo %YELLOW%Checking Docker installation...%NC%
docker --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Docker not found.%NC%
    echo.
    echo %BLUE%ℹ️  Please install Docker Desktop from:%NC%
    echo    https://www.docker.com/products/docker-desktop
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
) else (
    echo %GREEN%✅ Docker is installed%NC%
)

:: Check Docker Compose
echo %YELLOW%Checking Docker Compose...%NC%
docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo %RED%❌ Docker Compose not found.%NC%
        echo %BLUE%ℹ️  Please update Docker Desktop to the latest version.%NC%
        pause
        exit /b 1
    ) else (
        set COMPOSE_CMD=docker-compose
    )
) else (
    set COMPOSE_CMD=docker compose
)

:: Create data directories
echo %YELLOW%Creating data directories...%NC%
if not exist "data\uploads" mkdir data\uploads
if not exist "data\vectordb" mkdir data\vectordb
if not exist "data\logs" mkdir data\logs
echo %GREEN%✅ Data directories created%NC%

:: Check for GPU support (NVIDIA)
echo %YELLOW%Checking for GPU support...%NC%
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo %BLUE%ℹ️  No NVIDIA GPU detected. Running in CPU mode.%NC%
) else (
    echo %GREEN%✅ NVIDIA GPU detected%NC%
    echo.
    echo %BLUE%ℹ️  Make sure Docker Desktop has WSL2 backend enabled%NC%
    echo    and NVIDIA Container Toolkit is installed in WSL2.
    echo.
    set /p ENABLE_GPU="Do you want to enable GPU support? (y/n): "
    if /i "!ENABLE_GPU!"=="y" (
        :: Enable GPU in docker-compose.yml
        echo %YELLOW%Enabling GPU support in docker-compose.yml...%NC%
        powershell -Command "(gc docker-compose.yml) -replace '# (deploy:)', '$1' -replace '#   (resources:)', '  $1' -replace '#     (reservations:)', '    $1' -replace '#       (devices:)', '      $1' -replace '#         (- driver: nvidia)', '        $1' -replace '#           (count: all)', '          $1' -replace '#           (capabilities: \[gpu\])', '          $1' | Out-File -encoding ASCII docker-compose.yml.tmp"
        move /y docker-compose.yml.tmp docker-compose.yml >nul
        echo %GREEN%✅ GPU support enabled%NC%
    )
)

:: Build Docker images
echo.
echo %YELLOW%Building Docker images...%NC%
echo %BLUE%This may take 5-10 minutes on first run...%NC%
%COMPOSE_CMD% build

:: Start containers
echo.
echo %YELLOW%Starting K-Sphere containers...%NC%
%COMPOSE_CMD% up -d

:: Wait for services
echo %YELLOW%Waiting for services to start...%NC%
timeout /t 5 /nobreak >nul

:: Check if services are running
docker ps | findstr "k-sphere-backend" >nul
if errorlevel 1 (
    echo %RED%❌ Backend failed to start%NC%
    echo Check logs with: %COMPOSE_CMD% logs backend
) else (
    echo %GREEN%✅ Backend is running%NC%
)

docker ps | findstr "k-sphere-frontend" >nul
if errorlevel 1 (
    echo %RED%❌ Frontend failed to start%NC%
    echo Check logs with: %COMPOSE_CMD% logs frontend
) else (
    echo %GREEN%✅ Frontend is running%NC%
)

docker ps | findstr "k-sphere-ollama" >nul
if errorlevel 1 (
    echo %RED%❌ Ollama failed to start%NC%
    echo Check logs with: %COMPOSE_CMD% logs ollama
) else (
    echo %GREEN%✅ Ollama is running%NC%
)

:: Pull default AI models
echo.
echo %YELLOW%Pulling default AI models...%NC%
echo %BLUE%ℹ️  This will download ~2GB of data. Please wait...%NC%
docker exec k-sphere-ollama ollama pull llama3.2:3b
docker exec k-sphere-ollama ollama pull nomic-embed-text

:: Success message
echo.
echo %GREEN%╔══════════════════════════════════════════════╗%NC%
echo %GREEN%║   ✅ K-Sphere installed successfully!        ║%NC%
echo %GREEN%╚══════════════════════════════════════════════╝%NC%
echo.
echo %BLUE%📍 Access K-Sphere at:%NC%
echo    🌐 Main App:      %GREEN%http://localhost:3000%NC%
echo    🔧 Backend API:   %GREEN%http://localhost:8000%NC%
echo    📊 Vector DB Viz: %GREEN%http://localhost:8001/ui%NC%
echo.
echo %BLUE%📝 Useful commands:%NC%
echo    Start:   %COMPOSE_CMD% up -d
echo    Stop:    %COMPOSE_CMD% down
echo    Logs:    %COMPOSE_CMD% logs -f
echo    Status:  docker ps
echo.
echo %YELLOW%💡 Tip: All your data is stored in .\data\ directory%NC%
echo.
pause
