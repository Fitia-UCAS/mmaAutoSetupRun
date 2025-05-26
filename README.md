# [MathModelAgent](https://github.com/jihe520/MathModelAgent)自动部署脚本 README

## 本次更新

新增 `start_mma.bat` 和 `start_mma_all_windows.bat` 启动脚本。

## 脚本介绍

### 批处理脚本：auto_setup_run.bat

**这是啥？**  
Windows 懒人专属！自动检查 Python、Node.js、Redis，缺啥下啥，配置环境变量，启动 MathModelAgent 全家桶，简单粗暴！

**咋用？**  
1. 双击 `auto_setup_run.bat`。  
2. 脚本检查 Python（需 3.8+）。  
3. 缺 Node.js？自动下载 v20.17.0 到 `nodejs-portable`。  
4. 缺 Redis？自动下载 v5.0.14.1 到 `redis-portable`。  
5. 自动配置 `backend/.env.dev` 和 `frontend/.env`（需手动填 API key 和 model）。  
6. 启动 Redis、后端（`http://localhost:8000`）、前端（`http://localhost:5173`），弹出三个窗口。  
7. 想停？关闭 “Redis Server”、“Backend Server”、“Frontend Server” 窗口。

### 批处理脚本：start_mma.bat

**这是啥？**  
Windows 简易启动脚本，适合已配置好环境的用户，直接启动前端和后端。

**咋用？**  
1. 确保 Python、Node.js、pnpm、Redis 已安装，`backend/.env.dev` 和 `frontend/.env` 已配置。  
2. 双击 `start_mma.bat`。  
3. 启动后端（`http://localhost:8000`）和前端（`http://localhost:5173`），需手动启动 Redis。  
4. 关闭窗口停止服务。

### 批处理脚本：start_mma_all_windows.bat

**这是啥？**  
Windows 批处理启动脚本，适合已安装 Node.js 的用户，自动启动 Redis、前端、后端，弹出三个窗口，操作直观！

**咋用？**  

1. 确保 Python（3.8+）、Node.js、pnpm 已安装，Redis 放在 `redis-portable`。  
2. 双击 `start_mma_all_windows.bat`。  
3. 自动配置环境变量，安装依赖，启动 Redis、后端（`http://localhost:8000`）、前端（`http://localhost:5173`）。  
4. 关闭三个窗口停止服务。

### Python 脚本：auto_setup_run_win.py

**这是啥？**  
Windows 专用 Python 脚本，自动检查环境、安装依赖、动态分配端口，启动 MathModelAgent 系统。

**咋用？**  
1. 安装 Python（推荐 3.12）、Redis、Node.js、pnpm。  
2. 运行 `python auto_setup_run_win.py`。  
3. 弹出对话框选择 Redis 和 Node.js 安装路径（**非非提醒**：路径选错脚本会生气！）。  
4. 输入 API key 和 model（如 `deepseek/deepseek-chat`）。  
5. 脚本检查 Redis，安装依赖，配置 `.env`，启动 Redis、后端（`http://localhost:8000` 或动态端口）、前端（`http://localhost:5173`）。  
6. 查看日志 `log/main.log`，Ctrl+C 安全退出。

### Python 脚本：auto_setup_run_win_and_mac.py

**这是啥？**  
跨平台 Python 脚本，支持 Windows 和 macOS，功能与 `auto_setup_run_win.py` 类似。

**咋用？**  

1. 安装 Python（推荐 3.12）、Redis、Node.js、pnpm。  
2. 运行 `python auto_setup_run_win_and_mac.py`。  
3. 选择 Redis 和 Node.js 路径（macOS 可能在 `/usr/local/bin` 或 `/opt/homebrew/bin`）。  
4. 输入 API key 和 model。  
5. 启动服务，端口同上，日志查看 `log/main.log`。

## 项目输出

- 服务启动后，生成文件保存在 `backend/project/work_dir/xxx/`：  
  - `notebook.ipynb`：生成代码。  
  - `res.md`：Markdown 格式结果。  
  - `res.docx`：带图片的 Word 文档。

## 视频教程

- [auto_setup_run.bat 教程](./auto_setup_run[-v bat].mp4)
- [auto_setup_run_win.py 教程](./auto_setup_run_win[-v py].mp4)

## 脚本对比

### 启动脚本

| 特性 | start_mma.bat | start_mma_all_windows.bat |
|------|---------------|---------------------------|
| 平台 | Windows | Windows |
| 功能 | 快速启动前端和后端（需手动配置环境） | 启动 Redis、前端、后端，自动配置环境 |
| 使用 | 双击运行 | 双击运行 |
| 依赖 | Python（3.12推荐）、Redis、Node.js、pnpm（手动安装） | Python（3.8+）、Node.js、pnpm（手动），Redis 放 `redis-portable` |
| 路径选择 | 无 | 固定 `redis-portable` |
| 亮点 | 轻量快速，窗口化运行 | 自动配置 `.env`，三个窗口并行，清华镜像 |
| 输出 | 前端：`http://localhost:5173`<br>后端：`http://localhost:8000` | 同左 |
| 坑点 | 不检查环境，不启动 Redis，需手动配置 | 需手动装 Node.js，Redis 路径固定 |

### 安装配置脚本

| 特性 | auto_setup_run.bat | auto_setup_run_win.py | auto_setup_run_win_and_mac.py |
|------|---------------------|------------------------|-------------------------------|
| 平台 | Windows | Windows | Windows, macOS |
| 功能 | 自动下载依赖、配置并启动系统 | 环境检测、动态端口、配置并启动 | 同 Windows 版，跨平台 |
| 使用 | 双击运行 | `python auto_setup_run_win.py` | `python auto_setup_run_win_and_mac.py` |
| 依赖 | Python（3.8+），自动下 Node.js v20.17.0、Redis 5.0.14.1 | Python（3.12推荐）、Redis、Node.js、pnpm（手动） | 同 Windows 版 |
| 路径选择 | 自动下载到项目目录 | 手动选择 | 手动选择 |
| 亮点 | 全自动下载、窗口化、清华镜像 | 端口扫描、详细日志、API 验证 | 跨平台、端口扫描、日志 |
| 输出 | 前端：`http://localhost:5173`<br>后端：`http://localhost:8000` | 同左（后端端口可变） | 同左（后端端口可变） |
| 坑点 | 固定版本、需联网 | 需手动装依赖、路径要准 | macOS 可能有 bug |

## 选择指南

- **启动脚本**：适用于已配置好环境的用户，快速启动系统。  
  - `start_mma.bat`：轻量，需手动启动 Redis。  
  - `start_mma_all_windows.bat`：自动启动 Redis、前端、后端，窗口化操作。  

- **安装配置脚本**：适用于初次部署或环境不完整的用户，自动安装依赖并配置系统。  
  - `auto_setup_run.bat`：全自动下载依赖，适合 Windows 新手。  
  - `auto_setup_run_win.py`：支持动态端口，详细日志，适合 Windows 进阶用户。  
  - `auto_setup_run_win_and_mac.py`：跨平台支持，适合 macOS 用户。  

## TODO

- 优化错误提示，添加交互式配置向导。  
- 完善 macOS 支持，测试 Linux 兼容性。  
- Docker 镜像，非非喊你来贡献！  

## 终极提醒

- 路径选错，后果自负！选路径时擦亮眼，特别是 Python 脚本！  
- 依赖得手动装，别指望脚本啥都干！  
- 有 bug？改脚本！非非超忙，欢迎 PR！😜  
- 想用最新版 Node.js 或 Redis？手动安装后用 Python 脚本，灵活又自由！  

有好点子？快去改脚本，众所周知，非非超渣！😎