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

echo Configuring Docker registry mirror...
if not exist "%USERPROFILE%\.docker\daemon.json" (
    echo Creating Docker daemon.json with registry mirror...
    mkdir "%USERPROFILE%\.docker" 2>nul
    echo { "registry-mirrors": ["https://docker.1ms.run", "https://docker.xuanyuan.me", "https://hub.rat.dev", "https://dislabaiot.xyz", "https://doublezonline.cloud", "https://xdark.top"] } > "%USERPROFILE%\.docker\daemon.json"
    echo Registry mirror set to multiple sources. Restarting Docker...
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
    :: 在文件末尾追加本地环境的注释
    echo.>> "backend\.env.dev"
    echo # 如果是本地local：REDIS_URL=redis://localhost:6379/0>> "backend\.env.dev"
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

echo Starting Docker Compose services...
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