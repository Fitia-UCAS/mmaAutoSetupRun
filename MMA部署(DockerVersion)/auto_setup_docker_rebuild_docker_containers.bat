@echo off
setlocal EnableDelayedExpansion

:: Script: Rebuild Docker containers (without removing images)
:: Assumption: Images and volumes exist, docker-compose.yml is in the current directory

echo Checking if Docker is running...
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Docker is not running or not installed. Please start Docker Desktop.
    pause
    exit /b 1
)

echo Checking if docker-compose is available...
docker-compose --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: docker-compose is not installed. Please ensure Docker Desktop is installed or install docker-compose separately.
    pause
    exit /b 1
)

echo Checking if images exist...
docker images -q mathmodelagent-backend:latest | findstr . >nul
if %ERRORLEVEL% neq 0 (
    echo Error: mathmodelagent-backend:latest image does not exist. Please run 'docker-compose build' first.
    pause
    exit /b 1
)
docker images -q mathmodelagent-frontend:latest | findstr . >nul
if %ERRORLEVEL% neq 0 (
    echo Error: mathmodelagent-frontend:latest image does not exist. Please run 'docker-compose build' first.
    pause
    exit /b 1
)

echo Checking if docker-compose.yml exists...
if not exist "docker-compose.yml" (
    echo Error: docker-compose.yml file not found in the current directory.
    pause
    exit /b 1
)

echo Stopping and removing existing containers (if any)...
docker-compose down
if %ERRORLEVEL% neq 0 (
    echo Warning: Failed to stop containers. Continuing...
    pause
)

echo Starting Docker Compose services...
docker-compose up -d
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to start containers. Please check docker-compose.yml or view logs (docker-compose logs).
    pause
    exit /b 1
)

echo Checking container status...
timeout /t 5 /nobreak >nul
docker ps -f "name=mathmodelagent_"
if %ERRORLEVEL% neq 0 (
    echo Warning: No running mathmodelagent containers found. Please check logs (docker-compose logs).
    pause
) else (
    echo Containers started successfully:
    docker ps -f "name=mathmodelagent_"
)

echo.
echo Done! Services can be accessed at the following addresses:
echo - Redis: localhost:6379
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:5173
echo.
echo If there are issues, run 'docker-compose logs' to view logs.
pause
echo Final pause for debugging...
pause