@echo off
chcp 65001 > nul
echo ===== Starting MathModelAgent System (Local Version) =====

REM 设置 Redis 路径
set REDIS_PORTABLE_DIR=%cd%\redis-portable
set REDIS_PATH=%REDIS_PORTABLE_DIR%

REM 检查配置文件
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

REM 启动 Redis 服务
echo Starting Redis server...
start "Redis Server" cmd /k "%REDIS_PATH%\redis-server.exe"

REM 启动后端
echo Starting backend server...
cd backend
if not exist .venv (
  echo Error: Virtual environment not found. Please create it and install dependencies manually.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
start "Backend Server" cmd /k "set ENV=DEV && uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120"
cd ..

REM 启动前端
echo Starting frontend server...
cd frontend
start "Frontend Server" cmd /k "pnpm run dev"
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