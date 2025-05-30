# [MathModelAgent](https://github.com/jihe520/MathModelAgent) 自动部署脚本 README

欢迎踏上 MathModelAgent 的自动化部署之旅！这篇 README 是你的“通关秘籍”，助你轻松搞定这个数学建模神器的部署。Windows 硬核党、macOS 文艺范儿，这里都有你的专属脚本！非非警告：先读后动手，路径搞错可别怪我！😜

## 更新日志

### 新功能
- **重磅登场：`auto_setup_run_docker.bat`！** 扔进 MathModelAgent 目录，双击启动，Docker 魔法自动搞定！但坑不少，务必啃完 README 再动手！🚨

### 移除auto_setup_run_win_and_mac自动配置脚本，因无法验证

## 前置条件（跳过会后悔）

- **Docker Desktop**：必须安装、运行、登录！没 Docker？直接 GG！
- **用代理**：偷偷翻墙才顺畅。
- **镜像源必备**：配置国内镜像源，避开 VPN 冲突和认证麻烦。
- **后端的.env.dev对于doker有特定配置**

**非非提醒**：尽管`auto_setup_run_docker.bat` 会尝试配置镜像源，但可能需手动在 Docker Engine 界面点 `Apply & Restart` 生效。

## 推荐部署流程（正确姿势）

**参考资料（学霸笔记）：**

- [Windows | Docker Docs](https://docs.docker.com/desktop/setup/install/windows-install/)
- [如何优雅的变更 Docker Desktop 的镜像存储路径 - 腾讯云开发者社区](https://cloud.tencent.com/developer/article/2414097)
- [新版本 Docker Desktop 自定义安装路径和下载镜像地址路径修改](https://blog.csdn.net/hx2019626/article/details/145140014)

为了丝滑部署，照着这几步走：

1. **安装 Docker Desktop**：

   - 指定安装和资源路径，避免默认塞满 C 盘。示例命令（路径可自定）：
     ```bash
     start /w "" "Docker Desktop Installer.exe" install --accept-license --installation-dir="E:\Docker\Docker"
     ```
   - 在 Docker Desktop 的 `设置 > 资源` 里配置存储路径，省空间又省心：
     ![Docker 资源设置](./assets/docker%20resources.png)

2. **配置镜像源**：
   - 用下面`daemon.json` 配置国内镜像源，加速拉取镜像。直接改 `%USERPROFILE%\.docker\daemon.json` 或在 Docker 的 `设置 > Docker Engine` 贴上这神级配置：

     ```python
     {
       "builder": {
         "gc": {
           "defaultKeepStorage": "20GB",
           "enabled": true
         }
       },
       "experimental": false,
       "registry-mirrors": [
         "https://docker.1ms.run",
         "https://docker.xuanyuan.me",
         "https://hub.rat.dev",
         "https://dislabaiot.xyz",
         "https://doublezonline.cloud",
         "https://xdark.top"
       ]
     }
     ```

     

     ![Docker Engine 设置界面](./assets/doker%20engine.png)

3. **运行自动部署脚本**：

   - 将 `auto_setup_run_docker.bat` 放入 MathModelAgent 目录，双击运行。脚本会：
     - 检查 Docker 是否正常运行。
     - 配置镜像源。
     - 设置环境变量。
     - 启动 Docker Compose，点燃全场！

   **示例输出**（感受这气势）：

   ```
   Checking if Docker is installed and running...
   Docker version 28.1.1, build 4eba377
   Verifying project directory...
   Configuring Docker registry mirror...
   daemon.json already exists. Please ensure it contains valid registry mirrors
   Configuring environment variables...
   Starting Docker Compose services...
   [+] Building 1028.6s (27/27) FINISHED
   ...
   [+] Running 8/8
    ✔ backend Built
    ✔ frontend Built
    ✔ Network mathmodelagent_default Created
    ✔ Volume "mathmodelagent_redis_data" Created
    ✔ Volume "mathmodelagent_backend_venv" Created
    ✔ Container mathmodelagent_redis Started
    ✔ Container mathmodelagent_backend Started
    ✔ Container mathmodelagent_frontend Started
   Services started successfully
   Frontend: http://localhost:5173
   Backend API: http://localhost:8000
   ```
   关闭上述cmd窗口。

   > **非非警告**：构建可能慢如乌龟（示例里用了 1028.6 秒！后续非非又试了试基本每次5-8min）。网速差？换个更快镜像源，飞起来！

4. 修改后端配置文件样式如下（示例apikey和model）
   ![docker env dev配置](./assets/docker%20env%20dev%E9%85%8D%E7%BD%AE.png)

5. 修改后端配置文件后再运行上述 bat 脚本，ctrl + 点击 访问前端，即可食用。

## 常见错误（别踩坑）

**错误做法**：直接双击 `Docker Desktop Installer.exe` 默认安装。

- **问题**：
  - 默认安装会把 Docker 核心文件和镜像塞到 `%USERPROFILE%\AppData\Local\Docker\wsl\`，C 盘空间吃紧！
  - 没配置镜像源，拉取镜像慢如蜗牛，甚至超时失败。
- **解决办法**：按“推荐部署流程”走，指定安装路径、配置镜像源，省心又高效。

## 资源管理（救硬盘于水火）

- **存储黑洞**：部署约占 14GB，Docker 文件和镜像默认在 `%USERPROFILE%\AppData\Local\Docker\wsl\`。
  ![存储空间占用](./assets/space.png)

如果你很不幸直接双击docker安装文件安装了docker，可以尝试以下方式释放空间...

- **大扫除**：硬盘告急？用这俩命令清理：
  
  ```bash
  docker system prune -a
  docker volume prune
  ```
  
- **存储优化**：
  1. 在 Docker Desktop 的 `设置 > 资源` 改存储路径。
  2. 高级玩法：重启电脑后跑 [DockerSetup.ps1](./收录脚本/DockerSetup.ps1)，用符号链接挪存储路径（但回滚麻烦，谨慎操作）。

## 脚本介绍（你的懒人神器）

### 批处理脚本：`auto_setup_run_docker.bat`
**这是啥？**
Docker 爱好者的福音！Windows 专属，自动检查 Docker、配镜像源、调环境变量、启动全家桶。一键起飞，省心到爆！

**咋用？**

1. 把脚本丢进 MathModelAgent 目录，双击开跑。
2. 脚本确认 Docker 活着没，死了就让你去装。
3. 自动配镜像源（若 `daemon.json` 没配好，会帮你搞定）。
4. 复制 `backend/.env.dev.example` 和 `frontend/.env.example` 到对应 `.env` 文件（记得手动填 API key 和 model，修改docker的redis配置）。
5. 启动 Docker Compose，点亮前端（`http://localhost:5173`）和后端（`http://localhost:8000`）。
6. 出错？跑 `docker-compose logs` 查原因。
7. 想停？按任意键退出，优雅下线。

### 批处理脚本：`auto_setup_run.bat`

**这是啥？**
Windows 懒人神器！自动检查 Python、Node.js、Redis，缺啥装啥，配好环境变量，启动 MathModelAgent 全家桶，简单又暴力！

**咋用？**
1. 双击 `auto_setup_run.bat`，坐等魔法。
2. 检查 Python（要 3.8+），没有就催你去装。
3. 没 Node.js？自动下 v20.17.0 到 `nodejs-portable`.
4. 缺 Redis？自动拉 v5.0.14.1 到 `redis-portable`.
5. 配置 `backend/.env.dev` 和 `frontend/.env`（API key 和 model 得你手填）。
6. 启动 Redis、后端（`http://localhost:8000`）、前端（`http://localhost:5173`），弹出仨窗口。
7. 想停？关掉 “Redis Server”、“Backend Server”、“Frontend Server” 窗口。

### 批处理脚本：`start_mma.bat`
**这是啥？**
Windows 极简启动脚本，专为环境已配好的大佬设计（需要是本地配置，而不是docker），点一下就跑前端后端，干净利落！

**咋用？**

1. 确保 Python、Node.js、pnpm、Redis 都装好，`backend/.env.dev` 和 `frontend/.env` 也配齐。
2. 双击 `start_mma.bat`。
3. 启动后端（`http://localhost:8000`）和前端（`http://localhost:5173`）。Redis 得你自己手动开。
4. 关窗口停服务，简单粗暴。

### 批处理脚本：`start_mma_all_windows.bat`
**这是啥？**
Windows 批处理全家桶启动器（需要是本地配置，而不是docker），适合 Node.js 已就位的玩家。自动开 Redis、前端、后端，仨窗口齐飞，操作爽到爆！

**咋用？**
1. 确保 Python（3.8+）、Node.js、pnpm 装好，Redis 扔在 `redis-portable`。
2. 双击 `start_mma_all_windows.bat`。
3. 自动配环境变量，装依赖，启动 Redis、后端（`http://localhost:8000`）、前端（`http://localhost:5173`）。

### Python 脚本：`auto_setup_run_win.py`

**这是啥？**
Windows 专属 Python 脚本，智能检查环境、装依赖、动态分配端口，启动 MathModelAgent 像开挂一样顺！

**咋用？**

1. 装好 Python（推荐 3.12）、Redis、Node.js、pnpm。
2. 跑 `python auto_setup_run_win.py`。
3. 弹出对话框让你选 Redis 和 Node.js 路径（**非非警告**：选错路径，脚本会翻脸！）。
4. 脚本检查 Redis，装依赖，配 `.env`，启动 Redis、后端（`http://localhost:8000` 或动态端口）、前端（`http://localhost:5173`）。
6. 日志在 `log/main.log`，Ctrl+C 优雅退出。

## 项目输出（你的劳动成果）

服务跑起来后，成果文件都乖乖躺在 `backend/project/work_dir/xxx/`：
- `notebook.ipynb`：代码神器，拿去跑模型！
- `res.md`：Markdown 格式结果，简洁又好看。
- `res.docx`：带图的 Word 文档，装逼必备！

## 脚本对比（选对工具，事半功倍）

### 启动脚本

| 特性 | start_mma.bat | start_mma_all_windows.bat |
|------|---------------|---------------------------|
| 平台 | Windows | Windows |
| 功能 | 快速启动前端和后端（需手动配环境） | 启动 Redis、前端、后端，自动配环境 |
| 使用 | 双击运行 | 双击运行 |
| 依赖 | Python（3.12推荐）、Redis、Node.js、pnpm（手动装） | Python（3.8+）、Node.js、pnpm（手动），Redis 放 `redis-portable` |
| 路径选择 | 无 | 固定 `redis-portable` |
| 亮点 | 轻量快速，窗口化运行 | 自动配 `.env`，仨窗口并行，清华镜像加速 |
| 输出 | 前端：`http://localhost:5173`<br>后端：`http://localhost:8000` | 同左 |
| 坑点 | 不检查环境，Redis 得手动开 | 需手动装 Node.js，Redis 路径固定 |

### 安装配置脚本
| 特性 | auto_setup_run.bat | auto_setup_run_docker.bat | auto_setup_run_win.py |
|------|---------------------|---------------------------|------------------------|
| 平台 | Windows | Windows | Windows |
| 功能 | 自动下载依赖、配置并启动系统 | 检查 Docker、配镜像源、启动 Docker Compose | 环境检测、动态端口、配置并启动 |
| 使用 | 双击运行 | 双击运行 | `python auto_setup_run_win.py` |
| 依赖 | Python（3.8+），自动下 Node.js v20.17.0、Redis 5.0.14.1 | Docker Desktop | Python（3.12推荐）、Redis、Node.js、pnpm（手动） |
| 路径选择 | 自动下载到项目目录 | 无（需 docker-compose.yml） | 手动选择 |
| 亮点 | 全自动下载、窗口化、清华镜像 | Docker 一键部署，镜像源加速 | 端口扫描、详细日志、API 验证 |
| 输出 | 前端：`http://localhost:5173`<br>后端：`http://localhost:8000` | 同左 | 同左（后端端口可变） |
| 坑点 | 固定版本、需联网 | Docker 需预装，网络慢会卡 | 需手动装依赖、路径要准 |

## 选择指南（别选错，浪费感情）

**安装配置脚本**：新手或环境不全？选这些！

- `auto_setup_run.bat`：全自动下载，Windows 小白的最爱。
- `auto_setup_run_docker.bat`：Docker 党专属，一键部署，省心省力。
- `auto_setup_run_win.py`：动态端口+详细日志，Windows 进阶玩家的菜。

**启动脚本**：环境已就绪？直接开跑！

- `start_mma.bat`：轻量如羽，Redis 得你自己搞。

- `start_mma_all_windows.bat`：Redis、前端、后端全自动。配合`auto_setup_run.bat`使用。

## 终极提醒（不听后悔）

有好点子？快改脚本！遇到 bug？改脚本吧！众所周知，非非超渣！😎