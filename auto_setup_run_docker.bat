@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo Checking if Docker is installed and running...
docker --version
if %ERRORLEVEL% NEQ 0 (
    echo Docker is not installed or not running. Please install and start Docker Desktop!
    pause
    exit /b 1
)

echo Verifying project directory...
cd /d "%~dp0"
if not exist "docker-compose.yml" (
    echo docker-compose.yml not found. Please ensure you are in the correct project directory!
    pause
    exit /b 1
)

echo Configuring Docker registry mirrors...
if not exist "%USERPROFILE%\.docker\daemon.json" (
    echo Creating daemon.json with registry mirrors...
    mkdir "%USERPROFILE%\.docker" 2>nul
    echo { "registry-mirrors": ["https://docker.1ms.run", "https://docker.xuanyuan.me", "https://hub.rat.dev", "https://dislabaiot.xyz", "https://doublezonline.cloud", "https://xdark.top"] } > "%USERPROFILE%\.docker\daemon.json"
    echo Registry mirrors set to multiple sources. Restarting Docker...
    net stop com.docker.service
    net start com.docker.service
    timeout /t 5
) else (
    echo daemon.json already exists. Please ensure it contains valid registry mirrors!
)

echo Configuring environment variables...
if not exist "backend\.env.dev" (
    copy "backend\.env.dev.example" "backend\.env.dev"
    echo Copied backend\.env.dev.example to backend\.env.dev. Adding local Redis comment...
    echo.>> "backend\.env.dev"
    echo # For local setup: REDIS_URL=redis://localhost:6379/0>> "backend\.env.dev"
    echo.
    echo ************************************************************
    echo *                      WARNING                             *
    echo ************************************************************
    echo * To run MathModelAgent, you MUST configure the following: *
    echo * 1. Redis URL:                                            *
    echo *    - For Docker: REDIS_URL=redis://redis:6379/0          *
    echo *    - For local: REDIS_URL=redis://localhost:6379/0       *
    echo * 2. Model and API Key settings in backend\.env.dev:       *
    echo *    - COORDINATOR_MODEL and COORDINATOR_API_KEY           *
    echo *    - MODELER_MODEL and MODELER_API_KEY                   *
    echo *    - CODER_MODEL and CODER_API_KEY                       *
    echo *    - WRITER_MODEL and WRITER_API_KEY                     *
    echo *    - DEFAULT_MODEL and DEFAULT_API_KEY                   *
    echo * Refer to https://docs.litellm.ai/docs/ for model options.*
    echo *                                                          *
    echo * Please edit backend\.env.dev and rerun this script.      *
    echo ************************************************************
    echo.
) else (
    echo backend\.env.dev already exists. Please ensure it is correctly configured!
)
if not exist "frontend\.env.development" (
    copy "frontend\.env.example" "frontend\.env.development"
    echo Copied frontend\.env.example to frontend\.env.development. Please edit the configuration!
)

echo Stopping and removing existing containers if any...
docker-compose down
if %ERRORLEVEL% NEQ 0 (
    echo Failed to stop and remove existing containers. Please check Docker status!
    pause
    exit /b 1
)
echo Note: Data is persisted in volumes and will not be lost when containers are removed.

echo Checking if buildx is installed...
docker buildx version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo buildx is installed. Using buildx for optimized builds...
    set USE_BUILDX=true
) else (
    echo buildx is not installed. Using default build method...
    set USE_BUILDX=false
)

:: Ask the user whether to build with cache, default is to use cache
echo(
echo Do you want to build with cache? (y/n, default is y):
set /p BUILD_WITH_CACHE=
if /i "%BUILD_WITH_CACHE%"=="n" (
    set BUILD_OPTIONS=--no-cache
) else (
    set BUILD_OPTIONS=
)

echo Starting Docker Compose services...
set COMPOSE_PROJECT_TEMP_DIR=%USERNAME%\docker-temp
if %USE_BUILDX%==true (
    echo Building images with buildx...
    :: Build backend image with buildx
    docker buildx build --platform linux/amd64 -t mathmodelagent-backend:latest ./backend %BUILD_OPTIONS%
    :: Build frontend image with buildx
    docker buildx build --platform linux/amd64 -t mathmodelagent-frontend:latest ./frontend %BUILD_OPTIONS%
) else (
    echo Building images with docker-compose...
    docker-compose build %BUILD_OPTIONS%
)

docker-compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo Failed to start Docker Compose. Please check configuration or Docker status!
    echo Run 'docker-compose logs' for more details.
    pause
    exit /b 1
)

echo Services started successfully!
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000
echo Press any key to exit...
pause
endlocal