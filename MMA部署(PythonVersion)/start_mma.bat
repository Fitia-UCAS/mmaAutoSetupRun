@echo off
chcp 65001 >nul

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
