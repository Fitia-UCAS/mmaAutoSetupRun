# MathModelAgent 供Anadonda用户参考的安装指南

本指南详细总结了运行 `MathModelAgent` 项目所需的软件安装、环境配置和运行步骤。所有操作均基于 Windows 系统，并使用 Conda 管理 Python 环境。

## 环境准备

### 安装 Anaconda

- 下载并安装 [Anaconda](https://www.anaconda.com/products/distribution)（内嵌 Python 3.12）。
- 安装完成后，打开 **Anaconda Prompt**。

### 创建并激活 Conda 环境

- 创建名为 `MathModelAgent` 的虚拟环境：
  ```bash
  conda create -n MathModelAgent python=3.12
  ```
- 激活环境：
  ```bash
  conda activate MathModelAgent
  ```
  
- 如果后续要删除该环境，用
  
  ```bash
  conda env remove -n MathModelAgent
  ```

### 安装 Redis

- 下载 Redis（推荐 v7.x，或v8.x）并解压到 `D:\Redis`（**这里是示例路径，具体需要修改成你的安装路径**）。

- `win+r`输入`cmd`运行如下命令（**注意你自己的安装/解压路径**）

    切换路径：

    ```cmd
    D:
    cd D:\Redis-8.0.1-Windows-x64-cygwin-with-Service
    ```

    启动 Redis 服务：

    ```cmd
    D:\Redis-8.0.1-Windows-x64-cygwin-with-Service\redis-server.exe
    ```

- 验证 Redis（**非必要**）
  
  启动另外一个`cmd`窗口输入如下命令:
  
  ```cmd
  redis-cli ping
  ```
  
  上述运行结果应为：
  
  ```cmd
  PONG
  ```

### 安装 Node.js 和 pnpm

- 下载并安装 [Node.js — Download Node.js®](https://nodejs.org/zh-cn/download)。
- 全局安装 pnpm：
  ```cmd
  npm install -g pnpm
  ```
- 验证安装：
  ```cmd
  pnpm -v
  ```

## 后端配置与运行

### 进入后端目录

```bash
E:
cd E:\repo2\MathModelAgent\backend
```

### 配置环境变量

- 复制并编辑 `.env.dev` 文件：
  ```bash
  copy .env.dev.example .env.dev
  ```
- 使用文本编辑器打开 `backend\.env.dev`，填写以下内容：
  ```plaintext
  API_KEY=您的API密钥
  MODEL=推荐模型（如 deepseek/deepseek-chat）
  ```
- **API_KEY** 和 **MODEL**：从支持的 LLM 服务提供商（如 OpenAI、DeepSeek）获取。

### 安装后端依赖

- 安装核心依赖：
  ```bash
  pip install fastapi uvicorn redis pandas scikit-learn pydantic-settings loguru pypandoc openai litellm semanticscholar nbformat ansi2html e2b_code_interpreter jupyter_client icecream python-multipart rich
  ```
- 完整依赖列表请参见下方的 `requirements.txt`。

### 启动后端服务

- 运行以下命令：
  ```bash
  set ENV=DEV & uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120
  ```
- 确认服务启动成功：
  ```bash
  INFO:     Uvicorn running on http://0.0.0.0:8000 （Press CTRL+C to quit）
  ```

## 前端配置与运行

### 进入前端目录

-   再打开一个`Anaconda Prompt`切换路径

    运行如下命令：

```bash
E:
cd E:\repo2\MathModelAgent\frontend
```

###  配置环境变量

- 复制并编辑 `.env` 文件：
  ```bash
  copy .env.example .env
  ```
- 确保 `frontend\.env` 包含：
  ```plaintext
  VITE_API_BASE_URL=http://localhost:8000
  VITE_WS_URL=ws://localhost:8000
  ```

### 安装前端依赖

- 运行以下命令：
  ```bash
  pnpm i
  ```

### 启动前端服务

- 运行以下命令：
  ```bash
  pnpm run dev
  ```
  
- 访问 `http://localhost:5173` 查看前端界面。

    这里可能会有警告，但是这是正常的，只是提醒你可以更新（如果你`nodejs`版本很新的话）

    ```bash
    (base) E:\repo2\MathModelAgent\frontend>pnpm i
    Lockfile is up to date, resolution step is skipped
    Already up to date
    ╭ Warning ────────────────────────────────────────────────────╮│                      ││   Ignored build scripts: @biomejs/biome, @fortawesome/fontawesome-free, core-js, core-js-pure, esbuild, leveldown,
    ││   vue-demi.
    ││   Run "pnpm approve-builds" to pick which dependencies should be allowed to run scripts.                 
    ││
    │╰────────────────────────────────────────────────────────────╯
    Done in 601ms using pnpm v10.6.3
    (base) E:\repo2\MathModelAgent\frontend>pnpm run dev
    > frontend@0.0.0 dev E:\repo2\MathModelAgent\frontend
    > vite
      VITE v6.1.1  ready in 574 ms
      ➜  Local:   http://localhost:5173/
      ➜  Network: use --host to expose
      ➜  press h + enter to show help
    ```

## 项目输出

- 运行后，生成的文件保存在 `backend/project/work_dir`：
  - `notebook.ipynb`：运行代码。
  - `res.md`：Markdown 格式的论文。

## 完整的 `requirements.txt`

以下是后端所需的完整 Python 依赖列表：

```plaintext
aiofile>=3.9.0
aiohappyeyeballs==2.6.1
aiohttp==3.11.18
aioredis>=2.0.1
aiosignal==1.3.2
annotated-types==0.7.0
ansi2html==1.9.2
anyio==4.9.0
asttokens==3.0.0
attrs==25.3.0
celery>=5.4.0
certifi==2025.4.26
charset-normalizer==3.4.2
click==8.2.0
colorama==0.4.6
distro==1.9.0
e2b==1.5.0
e2b_code_interpreter==1.5.0
executing==2.2.0
fastapi==0.115.12
fastjsonschema==2.21.1
filelock==3.18.0
frozenlist==1.6.0
fsspec==2025.3.2
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
huggingface-hub==0.31.2
icecream==2.1.4
idna==3.10
ipykernel>=6.29.5
jinja2==3.1.6
jiter==0.9.0
joblib==1.5.0
jsonschema==4.23.0
jsonschema-specifications==2025.4.1
jupyter_client==8.6.3
litellm==1.70.0
loguru==0.7.3
markdown-it-py==3.0.0
MarkupSafe==3.0.2
matplotlib>=3.10.1
mdurl==0.1.2
multidict==6.4.3
nbformat==5.10.4
nest-asyncio==1.6.0
numpy==2.2.5
openai==1.75.0
openpyxl>=3.1.5
packaging==25.0
pandas==2.2.3
platformdirs==4.3.8
protobuf==5.29.4
pydantic==2.11.4
pydantic-core==2.33.2
pydantic-settings==2.9.1
pygments==2.19.1
pypandoc==1.15
python-dateutil==2.9.0.post0
python-dotenv==1.1.0
python-multipart==0.0.20
pytz==2025.2
pywin32==310
pyyaml==6.0.2
pyzmq==26.4.0
redis==6.1.0
referencing==0.36.2
regex==2024.11.6
requests==2.32.3
rich==14.0.0
rpds-py==0.25.0
scikit-learn==1.6.1
scipy==1.15.3
seaborn>=0.13.2
semanticscholar==0.10.0
six==1.17.0
sniffio==1.3.1
starlette==0.46.2
statsmodels>=0.14.4
tenacity==9.1.2
threadpoolctl==3.6.0
tiktoken==0.9.0
tokenizers==0.21.1
tornado==6.5
tqdm==4.67.1
traitlets==5.14.3
typing-extensions==4.13.2
tzdata==2025.2
urllib3==2.4.0
uvicorn==0.34.2
websocket>=0.2.1
win32-setctime==1.2.0
xgboost>=3.0.0
yarl==1.20.0
zipp==3.21.0
```

## 上述配置后之后再次运行只需运行如下代码

- 启动第一个 `anaconda prompt` 窗口，运行如下命令：
```
conda activate MathModelAgent
E:
cd E:\repo2\MathModelAgent\backend
set ENV=DEV
uvicorn app.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 60 --ws-ping-timeout 120
```

- 再启动一个 `anaconda prompt` 窗口，运行如下命令：

```
conda activate MathModelAgent
E:
cd E:\repo2\MathModelAgent\frontend
pnpm run dev
```