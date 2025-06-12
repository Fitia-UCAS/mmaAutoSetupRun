# [MathModelAgent](https://github.com/jihe520/MathModelAgent) 自动部署脚本 Docker 版本

欢迎体验 MathModelAgent 的自动化部署！这是原项目推荐的DOCKER布置流程的详细版本，但是据我体验依据于docker配置的体验还不如本地配置的体验...比如py或者其他bat脚本...如果你将脚本粘贴给ai的话，你会得到你想要的答案...

## DOCKER部署流程

按以下步骤操作，确保部署顺畅：

1. **配置后端 `.env.dev`**：
   
   - 复制 `backend\.env.dev.example` 为 `backend\.env.dev`。
   - 编辑 `backend\.env.dev`，配置以下关键项（参考下图示例）：
     - `REDIS_URL`：Docker 使用 `redis://redis:6379/0`，本地使用 `redis://localhost:6379/0`。
     - 模型和 API 密钥：如 `COORDINATOR_MODEL`, `COORDINATOR_API_KEY`, `MODELER_MODEL`, `MODELER_API_KEY` 等。
     - 参考 [LiteLLM 文档](https://docs.litellm.ai/docs/) 获取模型选项。
   - 示例配置：
     ![后端 .env.dev 配置](../assets/docker%20env%20dev%E9%85%8D%E7%BD%AE.png)
   
2. **安装 Docker Desktop**：

    **参考资料**：

    - [Windows | Docker Docs](https://docs.docker.com/desktop/setup/install/windows-install/)
    - [如何优雅地变更 Docker Desktop 的镜像存储路径](https://cloud.tencent.com/developer/article/2414097)
    - [新版本 Docker Desktop 自定义安装路径和镜像地址修改](https://blog.csdn.net/hx2019626/article/details/145140014)
    
   - 指定安装和资源路径，避免占满 C 盘。示例命令（路径可自定义）：
     ```bash
     start /w "" "Docker Desktop Installer.exe" install --accept-license --installation-dir="E:\Docker\Docker"
     ```
   - 在 Docker Desktop 的 `设置 > 资源` 中设置存储路径，节省空间：
     ![Docker 资源设置](../assets/docker%20resources.png)

3. **配置镜像源**：
   - 编辑 `%USERPROFILE%\.docker\daemon.json` 或在 Docker Desktop 的 `设置 > Docker Engine` 中粘贴以下配置，加速镜像拉取：
     ```json
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
     ![Docker Engine 设置](../assets/doker%20engine.png)

4. **运行自动部署脚本**：
   - 将 `auto_setup_run_docker.bat` 放入 MathModelAgent 根目录，双击执行。脚本会：
     - 检查 Docker 是否运行。
     - 配置镜像源（若未配置）。
     - 通过 Docker Compose 启动服务。
   - **示例输出**：
     ```
     Checking if Docker is installed and running...
     Docker version 28.1.1, build 4eba377
     Verifying project directory...
     Configuring Docker registry mirrors...
     daemon.json already exists. Please ensure it contains valid registry mirrors
     Stopping and removing existing containers if any...
     Note: Data is persisted in volumes and will not be lost when containers are removed.
     Checking if buildx is installed...
     buildx is installed. Using buildx for optimized builds...
     
     Do you want to clear all Docker cache (including build cache, unused images, containers, networks, etc.)? (y/n, default n):
     y
     Clearing all Docker cache...
     Deleted build cache objects:
     m1lo2klxl0afvorolekpoc2jo
     27rlaiv5mdu8wi51u4bh69a1y
     i8vh5fje4xd45szesf34ha4jd
     04xgs4t04hp42svb4io1qqmuc
     krn5lu3zfmlxn2kwfm32w6l0o
     1uc50znytbpqyv11meyc5gcl6
     0ldriecb5pc5vyxwno1vxgq6p
     hewpj9kofys4at2dbet7x06nz
     r21g4m1sjrpnv4nl1wbht2dah
     33ag6el4oiuf2x62z7s7iagmb
     zxlqvn52lm3sx44ded2d5wcnj
     jp5eyt36owbi6co4e0a471zha
     qduxjrkzu2vlt83js1aslbs2e
     054afhjxh46v4h3yj56q3vrcd
     auy427m8bwk87grr10uzzax5x
     osax9jry88wcrgjhy4zthcjva
     lvnladfwthvk5bjx1cqp79x22
     snqrv83uh78622u551ysrl6yt
     akozw4fg07ugd0uyrmonjnbsy
     16kstytgj799crgqk5zwap18g
     xhr4okd09b1wgqqxfj23y7xf8
     q0jxjblthcae37b8oy9lv4ppo
     i5ixitbnr8tyn5yezhetk5fbg
     vywv5zexcde80ha1uw0rjmd9s
     1tst53vft0vbe5vrgha0w5spt
     fbnc72mn3honj932j3j2koyax
     vfgfcwsz7dy0uvau6idumsdke
     tjln077bnzwow1v0hzggzmr6o
     xx0jc1pgf37ead39nvrab9hvj
     njty45fngodo8f60kwfkmql86
     7xre50287nb9lir6qeryb31zp
     yypieudv32msavd1jr6n66l7j
     
     Total reclaimed space: 7.641GB
     Clearing buildx build cache...
     Total:  0B
     Docker cache cleared.
     
     Do you want to build with cache? (y/n, default n):
     n
     Starting Docker Compose services...
     Building images with buildx...
     [+] Building 253.6s (14/14) FINISHED                                                                                                   docker:desktop-linux
      => [internal] load build definition from Dockerfile                                                                                                   0.1s
      => => transferring dockerfile: 823B                                                                                                                   0.0s
      => [internal] load metadata for ghcr.io/astral-sh/uv:latest                                                                                           3.8s
      => [internal] load metadata for docker.io/library/python:3.12-slim                                                                                   20.9s
      => [internal] load .dockerignore                                                                                                                      0.1s
      => => transferring context: 269B                                                                                                                      0.0s
      => FROM ghcr.io/astral-sh/uv:latest@sha256:d7e699d374d4e5cb52a37d5c8f0ee15e3c7572850325953bf9fa8d781cfa92fc                                           4.4s
      => => resolve ghcr.io/astral-sh/uv:latest@sha256:d7e699d374d4e5cb52a37d5c8f0ee15e3c7572850325953bf9fa8d781cfa92fc                                     0.1s
      => => sha256:81a969a72471c39e4ae1409ff3b696d7f096a27fa0da9385f92368983bd0b166 94B / 94B                                                               0.5s
      => => sha256:dd057dab1ec8d754c4d2a0d8e8ad61c1efd72c9f11c200e3506fc7c543b3a1f8 17.65MB / 17.65MB                                                       3.4s
      => => extracting sha256:dd057dab1ec8d754c4d2a0d8e8ad61c1efd72c9f11c200e3506fc7c543b3a1f8                                                              0.4s
      => => extracting sha256:81a969a72471c39e4ae1409ff3b696d7f096a27fa0da9385f92368983bd0b166                                                              0.1s
      => [builder 1/7] FROM docker.io/library/python:3.12-slim@sha256:0175d8ff0ad1dc8ceca4bcf311c3e47d08807a940959fa1cdbcefa87841883a1                     15.6s
      => => resolve docker.io/library/python:3.12-slim@sha256:0175d8ff0ad1dc8ceca4bcf311c3e47d08807a940959fa1cdbcefa87841883a1                              0.1s
      => => sha256:2085f9e6ccaec82a287654f932d6c768f0f9084a8f567ea03979491279dbd06c 248B / 248B                                                             6.1s
      => => sha256:9e1259a465a5cb12ab4d313f1aacea70ac0462fa9387e76fdb5369810f7401f6 13.66MB / 13.66MB                                                      14.3s
      => => sha256:ce1945dade9f42ba70b6318fa2e3862b64c774d98efc56b2f552a36f7dd58b82 3.51MB / 3.51MB                                                        12.0s
      => => sha256:61320b01ae5e0798393ef25f2dc72faf43703e60ba089b07d7170acbabbf8f62 28.23MB / 28.23MB                                                      11.0s
      => => extracting sha256:61320b01ae5e0798393ef25f2dc72faf43703e60ba089b07d7170acbabbf8f62                                                              0.9s
      => => extracting sha256:ce1945dade9f42ba70b6318fa2e3862b64c774d98efc56b2f552a36f7dd58b82                                                              0.2s
      => => extracting sha256:9e1259a465a5cb12ab4d313f1aacea70ac0462fa9387e76fdb5369810f7401f6                                                              0.5s
      => => extracting sha256:2085f9e6ccaec82a287654f932d6c768f0f9084a8f567ea03979491279dbd06c                                                              0.1s
      => [internal] load build context                                                                                                                      4.2s
      => => transferring context: 89.31MB                                                                                                                   3.8s
      => [builder 2/7] COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/                                                                               0.5s
      => [builder 3/7] WORKDIR /app                                                                                                                         0.2s
      => [builder 4/7] COPY pyproject.toml uv.lock ../                                                                                                       0.2s
      => [builder 5/7] RUN --mount=type=cache,target=/root/.cache/uv     uv sync --locked --no-install-project                                            123.8s
      => [builder 6/7] COPY . .                                                                                                                             1.1s
      => [builder 7/7] RUN --mount=type=cache,target=/root/.cache/uv     uv sync --locked                                                                   0.6s
      => exporting to image                                                                                                                                89.8s
      => => exporting layers                                                                                                                               76.1s
      => => exporting manifest sha256:3f79c2ec17c3eb364eb4208ecb3e31c05d1631314978e594057ba86723cd4a20                                                      0.0s
      => => exporting config sha256:a52068d189a70de85f0c405374388314005247b23fd75cf268ca910e14ced6ae                                                        0.0s
      => => exporting attestation manifest sha256:095c022c971bea95606c27264d6486ce9da5697114ccc04ece58ad9e4d763b67                                          0.1s
      => => exporting manifest list sha256:23e0d7534bf2d5a9c4370166baa51544a0d7bdaff85f8fb1cacb2ff493bd02b8                                                 0.0s
      => => naming to docker.io/library/mathmodelagent-backend:latest                                                                                       0.0s
      => => unpacking to docker.io/library/mathmodelagent-backend:latest                                                                                   13.4s
     
     View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/vzn9o441iagmxg9ekevzbl2gn
     [+] Building 123.9s (11/11) FINISHED                                                                                                   docker:desktop-linux
      => [internal] load build definition from Dockerfile                                                                                                   0.2s
      => => transferring dockerfile: 377B                                                                                                                   0.0s
      => [internal] load metadata for docker.io/library/node:20                                                                                             2.8s
      => [internal] load .dockerignore                                                                                                                      0.2s
      => => transferring context: 672B                                                                                                                      0.0s
      => [1/6] FROM docker.io/library/node:20@sha256:7c4cd7c6935554b79c6fffb88e7bde3db0ce25b45d4c634d1fb0f1a6e7f5b782                                      59.6s
      => => resolve docker.io/library/node:20@sha256:7c4cd7c6935554b79c6fffb88e7bde3db0ce25b45d4c634d1fb0f1a6e7f5b782                                       0.1s
      => => sha256:3fbcc227ac4b717b6faa06829f8381fcc888df989de0f866c75ac2033b569038 446B / 446B                                                             0.8s
      => => sha256:c657c59ebca66266d2e7c560e99090131867fc1ee1eba67a43765ddba49e163d 1.25MB / 1.25MB                                                         1.9s
      => => sha256:d8df3b059598a8606029f057c8a333d8c6ce52f1519fc522b802059feef5085c 48.63MB / 48.63MB                                                      23.1s
      => => sha256:2995dfd1a19c2122791620e7b5cdabcf911e54bcc4ed1358a36bf4e93895f6c5 3.32kB / 3.32kB                                                         1.2s
      => => sha256:e23f099911d692f62b851cf49a1e93294288a115f5cd2d014180e4d3684d34ab 211.36MB / 211.36MB                                                    51.7s
      => => sha256:79b2f47ad4443652b9b5cc81a95ede249fd976310efdbee159f29638783778c0 64.40MB / 64.40MB                                                      38.2s
      => => sha256:37927ed901b1b2608b72796c6881bf645480268eca4ac9a37b9219e050bb4d84 24.02MB / 24.02MB                                                      10.4s
      => => sha256:3e6b9d1a95114e19f12262a4e8a59ad1d1a10ca7b82108adcf0605a200294964 48.49MB / 48.49MB                                                      16.5s
      => => extracting sha256:3e6b9d1a95114e19f12262a4e8a59ad1d1a10ca7b82108adcf0605a200294964                                                              1.4s
      => => extracting sha256:37927ed901b1b2608b72796c6881bf645480268eca4ac9a37b9219e050bb4d84                                                              0.5s
      => => extracting sha256:79b2f47ad4443652b9b5cc81a95ede249fd976310efdbee159f29638783778c0                                                              1.7s
      => => extracting sha256:e23f099911d692f62b851cf49a1e93294288a115f5cd2d014180e4d3684d34ab                                                              4.2s
      => => extracting sha256:2995dfd1a19c2122791620e7b5cdabcf911e54bcc4ed1358a36bf4e93895f6c5                                                              0.1s
      => => extracting sha256:d8df3b059598a8606029f057c8a333d8c6ce52f1519fc522b802059feef5085c                                                              1.5s
      => => extracting sha256:c657c59ebca66266d2e7c560e99090131867fc1ee1eba67a43765ddba49e163d                                                              0.1s
      => => extracting sha256:3fbcc227ac4b717b6faa06829f8381fcc888df989de0f866c75ac2033b569038                                                              0.1s
      => [internal] load build context                                                                                                                      0.7s
      => => transferring context: 9.94MB                                                                                                                    0.4s
      => [2/6] WORKDIR /app                                                                                                                                 1.0s
      => [3/6] COPY package.json pnpm-lock.yaml ../                                                                                                          0.2s
      => [4/6] RUN npm install -g pnpm                                                                                                                      4.4s
      => [5/6] RUN pnpm install                                                                                                                            23.6s
      => [6/6] COPY . .                                                                                                                                     0.6s
      => exporting to image                                                                                                                                30.8s
      => => exporting layers                                                                                                                               18.0s
      => => exporting manifest sha256:41b5d12c9795d493d47dd75ba0ead2089bf4fdac61f62ea1b45bff7ff19cacae                                                      0.0s
      => => exporting config sha256:fcc7c8121b69d35c108bd00c460ae9fb5db884f1664158dd9a385b84662e0eb5                                                        0.0s
      => => exporting attestation manifest sha256:62c14828588c71528ab97bccf03e7472605c853cfe60214c3f793f952d7f67ff                                          0.1s
      => => exporting manifest list sha256:08dfd85468e46940f4245729aef1bca2f64bd2bca3d564e2974d90eb8dca9f07                                                 0.0s
      => => naming to docker.io/library/mathmodelagent-frontend:latest                                                                                      0.0s
      => => unpacking to docker.io/library/mathmodelagent-frontend:latest                                                                                  12.4s
     
     View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/f2x8temy98g2djb9q7jjbmazi
     [+] Running 8/8
      ✔ redis Pulled                                                                                                                                       13.6s
        ✔ f03ac91e0937 Pull complete                                                                                                                        3.0s
        ✔ 3db14a52e194 Pull complete                                                                                                                        1.5s
        ✔ 8493ebef02b7 Pull complete                                                                                                                        9.9s
        ✔ 4f4fb700ef54 Pull complete                                                                                                                        9.8s
        ✔ 3535ba13b4da Pull complete                                                                                                                        9.4s
        ✔ 63ba5ae8d20d Pull complete                                                                                                                        9.6s
        ✔ f18232174bc9 Pull complete                                                                                                                        2.8s
     [+] Running 6/6
      ✔ Network mathmodelagent_default        Created                                                                                                       0.1s
      ✔ Volume "mathmodelagent_backend_venv"  Created                                                                                                       0.0s
      ✔ Volume "mathmodelagent_redis_data"    Created                                                                                                       0.0s
      ✔ Container mathmodelagent_redis        Started                                                                                                      21.9s
      ✔ Container mathmodelagent_backend      Started                                                                                                      21.0s
      ✔ Container mathmodelagent_frontend     Started                                                                                                       5.5s
     Docker has been set up successfully
     Starting Docker containers for backend, frontend, and Redis...
     Press any key to exit...
     Press any key to continue . . .
     
     Microsoft Windows [版本 10.0.19045.5737]
     (c) Microsoft Corporation。保留所有权利。
     
     C:\Users\aFei>docker volume ls
     DRIVER    VOLUME NAME
     local     727e7b7bad6e3145f0c6ecc4af839d2fe769252595f8be0c8c8f87fbcffdd942
     local     mathmodelagent_backend_venv
     local     mathmodelagent_redis_data
     
     C:\Users\aFei>
     ```
   - 关闭命令行窗口。
   
5. **docker container点击映射网页访问MMA即可使用！**
   
   - **提示**：若未安装 buildx，构建可能极慢。建议从 [Docker buildx v0.24.0](https://github.com/docker/buildx/releases/tag/v0.24.0) 下载 `buildx-v0.24.0.windows-amd64.exe`（或根据系统选择版本）：

> - 移动至 `%USERPROFILE%\.docker\cli-plugins`（若无此文件夹则创建）。
>- 重命名为 `docker-buildx.exe`。
> - 在命令行验证：
>   ```
>   C:\Users\YourUser>docker buildx version
>   github.com/docker/buildx v0.24.0 d0e5e86c8b88ae4865040bc96917c338f4dd673c
>   ```

### 常见问题（避坑指南）

**坑点做法**：直接双击 `Docker Desktop Installer.exe` 默认安装。

- **问题**：
  - 默认安装将 Docker 文件和镜像存储在 `%USERPROFILE%\AppData\Local\Docker\wsl\`，C 盘空间告急！
  - 未配置镜像源，导致拉取镜像缓慢或失败。
- **解决办法**：指定安装路径并配置镜像源。

### 资源管理（保护你的硬盘）

- **存储占用**：部署约需 14GB 后续如果有其他镜像，会更大...，默认存储在 `%USERPROFILE%\AppData\Local\Docker\wsl\`。
  ![存储空间占用](../assets/space.png)

- **空间清理**：硬盘空间不足时，运行以下命令：
  
  ```bash
  docker system prune -a
  docker volume prune
  ```
  
- **优化存储**：
  1. 在 Docker Desktop 的 `设置 > 资源` 修改存储路径。
  2. 其他操作：重启电脑后运行 [DockerSetup.ps1](../MMA部署(OtherScripts)/DockerSetup.ps1)，通过符号链接迁移存储路径（**谨慎操作，回滚复杂，只推荐Hacker或者精通win系统的高手使用**）。
