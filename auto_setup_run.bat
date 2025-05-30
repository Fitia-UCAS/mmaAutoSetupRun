@echo off
chcp 65001 > nul
echo ===== Starting MathModelAgent System (Local Version) =====

REM Check for Python
echo Checking for Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
  echo Error: Python not found. Please install Python 3.8 or higher.
  echo Download from: https://www.python.org/downloads/
  pause
  exit /b 1
)

REM Check for Node.js
echo Checking for Node.js...
set NODE_PORTABLE_DIR=%cd%\nodejs-portable
set NODE_SUB_DIR=%NODE_PORTABLE_DIR%\node-v20.17.0-win-x64
set NODE_EXE=%NODE_SUB_DIR%\node.exe
if not exist "%NODE_SUB_DIR%" (
  echo Node.js not found. Downloading portable version...
  powershell -Command "& {Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.17.0/node-v20.17.0-win-x64.zip' -OutFile 'node.zip'}"
  if exist node.zip (
    echo Extracting Node.js...
    powershell -Command "& {Expand-Archive -Path 'node.zip' -DestinationPath '%NODE_PORTABLE_DIR%' -Force}"
    del node.zip
  ) else (
    echo Failed to download Node.js. Download manually from https://nodejs.org/en/download
    pause
    exit /b 1
  )
)

REM Set paths for npm and pnpm
set NPM_CMD=%NODE_SUB_DIR%\npm.cmd
set PNPM_CMD=%NODE_SUB_DIR%\pnpm.cmd

REM Install pnpm if not present
if not exist "%PNPM_CMD%" (
  echo Installing pnpm...
  call "%NPM_CMD%" config set prefix "%NODE_SUB_DIR%"
  call "%NPM_CMD%" install -g pnpm
  if not exist "%PNPM_CMD%" (
    echo Error: pnpm installation failed. Check Node.js installation.
    pause
    exit /b 1
  )
)

REM Check for Redis
set REDIS_PORTABLE_DIR=%cd%\redis-portable
if not exist "%REDIS_PORTABLE_DIR%" (
  echo Redis not found. Downloading portable version...
  powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip' -OutFile 'redis-portable.zip'}"
  if exist redis-portable.zip (
    echo Extracting Redis...
    powershell -Command "& {Expand-Archive -Path 'redis-portable.zip' -DestinationPath '%REDIS_PORTABLE_DIR%' -Force}"
    del redis-portable.zip
  ) else (
    echo Failed to download Redis. Download manually from https://github.com/tporadowski/redis/releases
    pause
    exit /b 1
  )
)
set REDIS_PATH=%REDIS_PORTABLE_DIR%

REM Check configuration files
if not exist .\backend\.env.dev (
  echo Backend config not found. Copying example config...
  copy .\backend\.env.dev.example .\backend\.env.dev
  echo Please edit .\backend\.env.dev to add your API keys and settings.
  pause
)

if not exist .\frontend\.env.development (
  echo Frontend config not found. Copying example config...
  copy .\frontend\.env.example .\frontend\.env.development
  pause
)

REM Start Redis server
echo Starting Redis server...
start "Redis Server" cmd /k "%REDIS_PATH%\redis-server.exe"

REM Configure backend
echo Configuring backend...
cd backend
if not exist .venv (
  echo Creating Python virtual environment...
  python -m venv .venv
)
echo Installing backend dependencies...
call .venv\Scripts\activate.bat
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install uv
set UV_LINK_MODE=copy
uv sync
echo Starting backend server...
start "Backend Server" cmd /k "call .venv\Scripts\activate.bat && set ENV=DEV && uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120"
cd ..

REM Configure frontend
echo Configuring frontend...
cd frontend
echo Installing frontend dependencies...
call "%PNPM_CMD%" i
echo Starting frontend server...
start "Frontend Server" cmd /k "call "%PNPM_CMD%" run dev"
cd ..

echo.
echo ===== MathModelAgent System Started Successfully =====
echo - Backend API: http://localhost:8000
echo - Frontend: http://localhost:5173
echo.
echo Results will be saved in backend/project/work_dir/xxx/*
echo - notebook.ipynb: Generated code
echo - res.md: Results in markdown format
echo - res.docx: Results in Word format (with images)
echo.
echo To stop the system, close the "Redis Server", "Backend Server", and "Frontend Server" windows.
pause