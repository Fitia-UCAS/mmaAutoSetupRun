@echo off
chcp 65001 >nul

echo === 启动 Redis ===
start cmd /k ".\redis-portable\redis-server.exe"
echo 等待 Redis 启动...
timeout /t 1 /nobreak >nul
echo 检查 Redis 是否运行...
redis-cli -h 127.0.0.1 -p 6379 ping | findstr PONG >nul
if errorlevel 1 (
    echo Redis 启动失败，请检查 redis-server.exe 或端口 6379 是否被占用
    pause
    exit /b
)

echo === 启动后端 ===
cd backend

echo === 启动 FastAPI 后端 ===
set ENV=DEV
start cmd /k "..\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120 --reload"

cd ..

echo === 启动前端 ===
cd frontend
start cmd /k "pnpm run dev"

echo === 所有服务已启动 ===
pause