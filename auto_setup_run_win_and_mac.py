import subprocess
import sys
from pathlib import Path
import os
import shutil
import time
import signal
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import socket
import platform

# 自动安装所需的 Python 库（仅限不在 pyproject.toml 中的库）
required_libraries = ["python-dotenv", "psutil"]
for lib in required_libraries:
    try:
        __import__(lib)
    except ImportError:
        print(f"Installing {lib}...")
        subprocess.run([sys.executable, "-m", "pip", "install", lib], check=True)

# 导入不在 pyproject.toml 中的库
from dotenv import load_dotenv, set_key
import psutil

# 定义 backend/.env.dev 中必需的变量
required_vars = [
    "COORDINATOR_API_KEY",
    "COORDINATOR_MODEL",
    "MODELER_API_KEY",
    "MODELER_MODEL",
    "CODER_API_KEY",
    "CODER_MODEL",
    "WRITER_API_KEY",
    "WRITER_MODEL",
    "DEFAULT_API_KEY",
    "DEFAULT_MODEL",
]

# 配置项目路径和日志
project_root = Path.cwd()
log_dir = project_root / "log"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "main.log"

file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="w")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]"
)
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 从 .env 文件加载环境变量
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

# 全局变量用于追踪服务进程
frontend_process = None
backend_process = None
redis_process = None

# 检测操作系统
is_windows = platform.system() == "Windows"
is_mac = platform.system() == "Darwin"


# 打开目录选择对话框并返回选择的路径
def select_directory(title: str) -> str:
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title=title)
    root.destroy()
    return directory


# 获取或提示用户输入目录路径并保存到 .env 文件
def get_user_input(env_var: str, title: str) -> str:
    value = os.getenv(env_var)
    while not value or not Path(value).exists():
        value = select_directory(title)
        if value and Path(value).exists():
            set_key(env_path, env_var, value, quote_mode="never")
            logger.info(f"Set {env_var} to {value}")
        else:
            messagebox.showerror("Error", f"Please select a valid directory for {env_var}.")
    return value


# 检查目录是否包含所有必需文件
def check_path_valid(path: str, required_files: list) -> bool:
    path_obj = Path(path)
    if not path_obj.exists():
        logger.error(f"Directory does not exist: {path}")
        return False
    missing_files = [file for file in required_files if not (path_obj / file).exists()]
    if missing_files:
        logger.error(f"Missing files in {path}: {', '.join(missing_files)}")
        return False
    logger.info(f"Path {path} is valid with all required files present")
    return True


# 启动 Redis 服务器并验证其运行状态
def start_redis(redis_path: str) -> bool:
    global redis_process
    redis_server = Path(redis_path) / ("redis-server.exe" if is_windows else "redis-server")
    if not redis_server.exists():
        logger.error(f"Redis server not found at {redis_server}")
        return False

    for attempt in range(3):
        logger.info(f"Attempt {attempt + 1}: Starting Redis server: {redis_server}")
        try:
            redis_process = subprocess.Popen(
                [str(redis_server)],
                creationflags=subprocess.CREATE_NEW_CONSOLE if is_windows else 0
            )
            time.sleep(1.5)  # 等待 Redis 初始化
            if check_redis(redis_path):
                logger.info("Redis started successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to start Redis on attempt {attempt + 1}: {e}")
    logger.error("Failed to start Redis after 3 attempts. Please check the path or start manually.")
    return False


# 通过发送 PING 命令验证 Redis 是否运行
def check_redis(redis_path: str) -> bool:
    redis_cli = Path(redis_path) / ("redis-cli.exe" if is_windows else "redis-cli")
    if not redis_cli.exists():
        logger.error(
            f"Redis CLI not found at {redis_cli}. Please ensure Redis is installed correctly."
        )
        messagebox.showerror(
            "Error",
            f"Redis CLI not found at {redis_cli}. Please install Redis or update the REDIS_PATH in .env.",
        )
        return False

    try:
        result = subprocess.run([str(redis_cli), "ping"], capture_output=True, text=True, timeout=5)
        if result.stdout.strip() == "PONG":
            logger.info("Redis is running and responding to PING")
            return True
        else:
            logger.warning(f"Redis PING returned unexpected result: {result.stdout.strip()}")
            return False
    except Exception as e:
        logger.error(f"Error checking Redis: {e}")
        return False


# 配置后端和前端环境文件
def configure_env_files(project_root: Path):
    backend_env = project_root / "backend" / ".env.dev"
    frontend_env = project_root / "frontend" / ".env"
    backend_env_example = project_root / "backend" / ".env.dev.example"

    # 处理 backend .env.dev 创建或更新
    if not backend_env.exists():
        if backend_env_example.exists():
            shutil.copy(backend_env_example, backend_env)
            logger.info(f"Created {backend_env} from {backend_env_example}")
        else:
            with backend_env.open("w") as f:
                f.write("# Please set the following required variables\n")
                for var in required_vars:
                    f.write(f"{var}=\n")
                f.write("\n# Optional variables with defaults\n")
                f.write("MAX_CHAT_TURNS=60\n")
                f.write("MAX_RETRIES=5\n")
                f.write("SERVER_HOST=http://localhost:8000\n")
                f.write("LOG_LEVEL=DEBUG\n")
                f.write("DEBUG=true\n")
                f.write("REDIS_URL=redis://localhost:6379/0\n")
                f.write("REDIS_MAX_CONNECTIONS=20\n")
                f.write("CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000\n")
            logger.info(f"Created new {backend_env} with placeholders")
    else:
        logger.info(f"Backend .env already exists at {backend_env}")

    # 提示用户编辑 .env.dev 并设置必需变量
    logger.info(
        f"Please edit {backend_env} and set the required variables: {', '.join(required_vars)}"
    )
    while True:
        input("Press Enter when you have finished editing.")
        load_dotenv(dotenv_path=backend_env, override=True)
        missing_vars = [var for var in required_vars if not os.getenv(var, "").strip()]
        if not missing_vars:
            logger.info("All required variables are set. Proceeding.")
            break
        else:
            logger.error(
                f"The following required variables are missing or empty: {', '.join(missing_vars)}"
            )
            response = input("Do you want to edit the file again? (Y/N): ").strip().upper()
            if response != "Y":
                logger.error("Required variables are missing. Exiting.")
                sys.exit(1)

    # 配置前端 .env
    if not frontend_env.exists():
        with frontend_env.open("w") as f:
            f.write("VITE_API_BASE_URL=http://localhost:8000\n")
            f.write("VITE_WS_URL=ws://localhost:8000\n")
        logger.info(f"Created new {frontend_env}")


# 使用 uv 安装后端依赖并设置虚拟环境
def install_backend_dependencies(project_root: Path):
    backend_dir = project_root / "backend"
    os.chdir(backend_dir)

    uv_path = Path(sys.executable).parent / ("Scripts" if is_windows else "bin") / ("uv.exe" if is_windows else "uv")
    if not uv_path.exists():
        logger.info("Installing uv package manager...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "uv"],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.returncode != 0 or not uv_path.exists():
            logger.error(f"Failed to install uv: {result.stderr}")
            messagebox.showerror(
                "Error", "Failed to install uv package manager. Please install it manually."
            )
            sys.exit(1)
        logger.info("uv package manager installed successfully")

    logger.info("Installing backend dependencies...")
    result = subprocess.run(
        [str(uv_path), "sync"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    if result.returncode != 0:
        logger.error(f"Failed to sync backend dependencies: {result.stderr}")
        sys.exit(1)

    logger.info("Backend dependencies installed successfully")
    venv_dir = backend_dir / ".venv"
    if not venv_dir.exists():
        logger.error("Virtual environment not created")
        sys.exit(1)
    logger.info("Virtual environment ready")
    return venv_dir


# 获取 npm 的全局二进制目录
def get_global_bin_dir(npm_path: Path) -> Path:
    try:
        result = subprocess.run(
            [str(npm_path), "config", "get", "prefix"],
            capture_output=True,
            text=True,
            check=True,
        )
        prefix = result.stdout.strip()
        bin_dir = Path(prefix) if is_windows else Path(prefix) / "bin"
        logger.info(f"Global bin directory: {bin_dir}")
        return bin_dir
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get global prefix: {e}")
        sys.exit(1)


# 根据 npm 的全局二进制目录定位 pnpm 命令路径
def get_pnpm_path(npm_path: Path) -> Path:
    bin_dir = get_global_bin_dir(npm_path)
    pnpm_path = bin_dir / ("pnpm.cmd" if is_windows else "pnpm")
    logger.info(f"Checking if pnpm exists at {pnpm_path}")
    if not pnpm_path.exists():
        logger.info("pnpm not found, attempting to install globally...")
        result = subprocess.run(
            [str(npm_path), "install", "-g", "pnpm"],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.returncode != 0 or not pnpm_path.exists():
            logger.error(f"Failed to install pnpm: {result.stderr}")
            messagebox.showerror(
                "Error", "Failed to install pnpm. Please install it manually using npm."
            )
            sys.exit(1)
        logger.info("pnpm installed successfully")
    return pnpm_path


# 使用 pnpm 安装前端依赖
def install_frontend_dependencies(project_root: Path, nodejs_path: str):
    frontend_dir = project_root / "frontend"
    os.chdir(frontend_dir)

    npm_path = Path(nodejs_path) / ("npm.cmd" if is_windows else "npm")
    node_path = Path(nodejs_path) / ("node.exe" if is_windows else "node")
    if not npm_path.exists() or not node_path.exists():
        logger.error(f"npm or node not found at {nodejs_path}")
        sys.exit(1)

    logger.info(f"node_path: {node_path}")
    logger.info(f"npm_path: {npm_path}")

    env = os.environ.copy()
    env["PATH"] = str(nodejs_path) + os.pathsep + env["PATH"]

    try:
        subprocess.run([str(npm_path), "--version"], check=True, capture_output=True, env=env)
        logger.info("npm is functioning correctly")
    except subprocess.CalledProcessError:
        logger.error("npm is not functioning correctly. Please check Node.js installation.")
        sys.exit(1)

    pnpm_path = get_pnpm_path(npm_path)
    logger.info("Installing frontend dependencies with pnpm...")
    result = subprocess.run(
        [str(pnpm_path), "install"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        env=env,
    )
    if result.returncode == 0:
        logger.info("Frontend dependencies installed successfully")
    else:
        logger.error(f"Failed to install frontend dependencies: {result.stderr}")
        sys.exit(1)


# 使用 pnpm 启动前端开发服务器
def run_frontend(project_root: Path, nodejs_path: str) -> subprocess.Popen:
    global frontend_process
    frontend_dir = project_root / "frontend"
    os.chdir(frontend_dir)
    npm_path = Path(nodejs_path) / ("npm.cmd" if is_windows else "npm")
    node_path = Path(nodejs_path) / ("node.exe" if is_windows else "node")

    logger.info(f"nodejs_path: {nodejs_path}")
    logger.info(f"node exists: {node_path.exists()}")
    logger.info(f"npm exists: {npm_path.exists()}")
    if not node_path.exists() or not npm_path.exists():
        logger.error(f"Node.js path invalid: {nodejs_path}")
        sys.exit(1)

    pnpm_path = get_pnpm_path(npm_path)

    env = os.environ.copy()
    env["PATH"] = str(nodejs_path) + os.pathsep + env["PATH"]
    env["NODE"] = str(node_path)

    logger.info("Starting frontend server with 'pnpm run dev'...")
    frontend_process = subprocess.Popen(
        [str(pnpm_path), "run", "dev"],
        shell=True if is_windows else False,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if is_windows else 0,
        env=env,
    )
    return frontend_process


# 从起始端口扫描可用端口
def find_available_port(start_port: int = 8000, max_tries: int = 50) -> int:
    port = start_port
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("0.0.0.0", port))
                logger.info(f"Port {port} is available")
                return port
            except OSError as e:
                if e.errno in (98, 10048):
                    if clear_port(port):
                        time.sleep(1)
                        try:
                            s.bind(("0.0.0.0", port))
                            logger.info(f"Port {port} has been cleared and is available")
                            return port
                        except OSError as retry_e:
                            logger.warning(f"Retry bind failed for port {port}: {retry_e}")
                            port += 1
                    else:
                        logger.info(f"Failed to clear port {port}, trying next port")
                        port += 1
                else:
                    logger.error(f"Unexpected error binding to port {port}: {e}")
                    raise
    logger.error(f"No available ports found between {start_port} and {port-1}")
    raise RuntimeError("No available ports found")


# 尝试清理端口
def clear_port(port: int) -> bool:
    try:
        cleared = False
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status in ("LISTEN", "TIME_WAIT"):
                process = psutil.Process(conn.pid)
                logger.info(f"Terminating process {conn.pid} using port {port}")
                process.terminate()
                try:
                    process.wait(timeout=3)
                    cleared = True
                except psutil.TimeoutExpired:
                    process.kill()
                    cleared = True
        return cleared
    except Exception as e:
        logger.warning(f"Failed to clear port {port}: {e}")
        return False


# 在指定端口上启动后端服务器
def run_backend(project_root: Path, port: int) -> subprocess.Popen:
    global backend_process
    backend_dir = project_root / "backend"
    venv_python = (
        backend_dir / ".venv" / ("Scripts" if is_windows else "bin") / ("python.exe" if is_windows else "python")
    )
    if not venv_python.exists():
        logger.warning(
            f"Virtual environment Python not found at {venv_python}, using system Python"
        )
        venv_python = sys.executable

    env = os.environ.copy()
    env["ENV"] = "DEV"

    logger.info(f"Starting backend server on port {port} using {venv_python}...")
    backend_process = subprocess.Popen(
        [
            str(venv_python),
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
            "--reload",
            "--ws-ping-interval",
            "60",
            "--ws-ping-timeout",
            "120",
        ],
        cwd=str(backend_dir),
        env=env,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if is_windows else 0,
    )

    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect(("localhost", port))
                logger.info(f"Backend successfully started on port {port}")
                break
        except (ConnectionRefusedError, socket.timeout):
            if attempt < max_attempts - 1:
                time.sleep(1)
            else:
                logger.error("Backend failed to start after multiple attempts.")
                sys.exit(1)
    return backend_process


# 递归终止进程及其子进程
def terminate_process_tree(pid: int):
    try:
        process = psutil.Process(pid)
        for child in process.children(recursive=True):
            try:
                child.terminate()
                child.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                child.kill()
                logger.info(f"Killed child process {child.pid} after termination timeout")
        process.terminate()
        process.wait(timeout=3)
        logger.info(f"Process {pid} terminated successfully")
    except psutil.NoSuchProcess:
        logger.info(f"Process {pid} does not exist, no action taken")
    except Exception as e:
        logger.error(f"Failed to terminate process {pid}: {e}")
        try:
            process.kill()
            logger.info(f"Forced kill of process {pid}")
        except psutil.NoSuchProcess:
            pass


# 递归删除 Python 缓存文件
def clear_python_cache(project_root: Path):
    logger.info(f"Clearing Python cache files in {project_root}...")
    cache_count = 0
    for pycache_dir in project_root.glob("**/__pycache__"):
        shutil.rmtree(pycache_dir, ignore_errors=True)
        cache_count += 1
    for pyc_file in project_root.glob("**/*.pyc"):
        pyc_file.unlink(missing_ok=True)
        cache_count += 1
    logger.info(f"Removed {cache_count} Python cache items.")


# 关闭前端、后端和 Redis 服务
def shutdown_services():
    global frontend_process, backend_process, redis_process
    logger.info("Shutting down services...")

    if backend_process and backend_process.poll() is None:
        logger.info("Terminating backend server...")
        terminate_process_tree(backend_process.pid)

    if frontend_process and frontend_process.poll() is None:
        logger.info("Terminating frontend server...")
        terminate_process_tree(frontend_process.pid)

    if redis_process and redis_process.poll() is None:
        logger.info("Terminating Redis server...")
        terminate_process_tree(redis_process.pid)

    logger.info("All services stopped.")


# 处理终止信号
def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, initiating shutdown...")
    shutdown_services()
    clear_python_cache(project_root)
    logger.info("Project shutdown complete.")
    sys.exit(0)


# 主函数：初始化并启动项目服务
def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    clear_python_cache(project_root)

    redis_path = get_user_input("REDIS_PATH", "Select Redis installation directory")
    nodejs_path = get_user_input("NODEJS_PATH", "Select Node.js installation directory")

    redis_files = ["redis-server.exe", "redis-cli.exe"] if is_windows else ["redis-server", "redis-cli"]
    node_files = ["npm.cmd"] if is_windows else ["npm"]

    if not check_path_valid(redis_path, redis_files):
        messagebox.showerror("Error", f"Invalid Redis path: {redis_path}. Please select again.")
        redis_path = select_directory("Select Redis installation directory")
        set_key(env_path, "REDIS_PATH", redis_path, quote_mode="never")

    if not check_path_valid(nodejs_path, node_files):
        messagebox.showerror("Error", f"Invalid Node.js path: {nodejs_path}. Please select again.")
        nodejs_path = select_directory("Select Node.js installation directory")
        set_key(env_path, "NODEJS_PATH", nodejs_path, quote_mode="never")

    logger.info("Checking Redis status...")
    if not check_redis(redis_path):
        if start_redis(redis_path):
            logger.info("Redis started successfully")
        else:
            logger.error("Failed to start Redis. Please check the path or start manually.")
            sys.exit(1)

    logger.info("Configuring environment files...")
    configure_env_files(project_root)

    logger.info("Installing backend dependencies...")
    venv_dir = install_backend_dependencies(project_root)
    venv_python = venv_dir / ("Scripts" if is_windows else "bin") / ("python.exe" if is_windows else "python")
    if not venv_python.exists():
        logger.error(f"Virtual environment Python not found: {venv_python}")
        sys.exit(1)

    logger.info("Scanning for available backend port...")
    try:
        port = find_available_port()
        logger.info(f"Selected port {port} for backend")
    except RuntimeError as e:
        logger.error(f"Failed to select port: {e}")
        sys.exit(1)

    frontend_env = project_root / "frontend" / ".env"
    set_key(
        frontend_env,
        "VITE_API_BASE_URL",
        f"http://localhost:{port}",
        quote_mode="never",
    )
    set_key(frontend_env, "VITE_WS_URL", f"ws://localhost:{port}", quote_mode="never")
    logger.info(
        f"Updated frontend .env: VITE_API_BASE_URL=http://localhost:{port} and VITE_WS_URL=ws://localhost:{port}"
    )

    logger.info("Installing frontend dependencies...")
    install_frontend_dependencies(project_root, nodejs_path)

    logger.info("Starting project services...")
    run_frontend(project_root, nodejs_path)
    run_backend(project_root, port)

    logger.info(f"Backend running at http://0.0.0.0:{port}")
    logger.info("Frontend running at http://localhost:5173 (check console for exact port)")

    try:
        while True:
            time.sleep(1)
            if frontend_process and frontend_process.poll() is not None:
                logger.error("Frontend process exited unexpectedly")
                break
            if backend_process and backend_process.poll() is not None:
                logger.error("Backend process exited unexpectedly")
                break
    except KeyboardInterrupt:
        logger.info("Received Ctrl+C, shutting down services...")
    finally:
        shutdown_services()
        clear_python_cache(project_root)
        logger.info("Project shutdown complete.")


if __name__ == "__main__":
    main()