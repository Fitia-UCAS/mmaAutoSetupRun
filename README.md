# 自动部署脚本README

## 本次更新

- **批处理脚本**：感谢群友Pluto的`local_start.bat`，非非给它修了BUG！现在会检查MathModelAgent目录下的Redis和Node.js，没找到就自动下载，环境变量啥的再也不用愁！但小坑：没得选路径，爱用不用！😎

## 脚本介绍

### Python脚本：`auto_setup_run_win.py`

**这是啥？**
Windows用户的福音！这脚本自动检查环境、装依赖、配环境变量，一键启动MathModelAgent的前端、后端、Redis，省心到飞起！

**咋用？**

1. 先装好Python（3.12最香）、Redis、Node.js。
2. 敲`python auto_setup_run_win.py`。
3. 弹出对话框让你选Redis和Node.js的安装路径（**非非提醒**：眼睛擦亮，选错脚本会闹脾气！）。
4. 脚本检查Redis、装依赖、配`.env`，然后启动全家桶。
5. 日志喊前端在`http://localhost:5173`，后端在`http://0.0.0.0:8000`（或空闲端口），你就赢啦！

**亮点搁哪呢？**

- 环境变量没配？手动选路径，灵活！
- 端口被占？动态扫描，自动找空位！
- 日志详细到爆，`log/main.log`里非非帮你记好每一步！
- Ctrl+C或关窗口，脚本乖乖清理，不留垃圾！

**坑点**：依赖得自己装，路径选错别来找非非哭！😃

### Python脚本：`auto_setup_run_win_and_mac.py`
**这是啥？**
跨平台神器！Windows、macOS通吃，功能跟Windows版差不多，但macOS用户也能浪起来！

**咋用？**
1. 装Python（3.12推荐）、Redis、Node.js。
2. 跑`python auto_setup_run_win_and_mac.py`。
3. 选Redis和Node.js路径（**非非警告**：选错脚本直接罢工！）。
4. 剩下跟Windows版一样，启动后端口同上。

**亮点搁哪呢？**
- 自动识别系统，Windows/macOS随便跑！
- 日志、端口扫描、清理功能一个不少！
- macOS路径可能有点怪（Homebrew装的可能在`/usr/local/bin`或`/opt/homebrew/bin`）。

**坑点**：macOS支持还在磨合，可能有很多bug，遇到问题自己改脚本，非非看好你！😜 依赖还得手动装哦！

### 批处理脚本：`local_start.bat`
**这是啥？**
Windows懒人专属！一点就跑，Python、Redis、Node.js缺啥下啥，MathModelAgent直接起飞！简单粗暴，非非超爱！

**咋用？**

1. 双击`local_start.bat`。
2. 检查Python（3.8+够用）。
3. 没Node.js？自动下v20.17.0到`MathModelAgent/nodejs-portable`。
4. 没Redis？自动下5.0.14.1到`MathModelAgent/redis-portable`。
5. 配`.env`（API key和model得你自己填），装依赖，启动Redis、后端、前端。
6. 三个窗口弹出：Redis、后端（`http://0.0.0.0:8000`）、前端（`http://localhost:5173`）。
7. 想停？关窗口就好！

**亮点搁哪呢？**

- 全自动，依赖直接下载，懒人福音！
- 便携版解压到项目目录，省心！
- 出错暂停，提示一目了然！

**坑点**：路径没得选，版本固定（Node.js v20.17.0，Redis 5.0.14.1），想要最新版自己装！不喜欢？用Python脚本或改bat，非非给你点赞！😎

## TODO

- **用户体验**：错误提示更清晰，非非不想看你一脸懵！加个详细手册，教你装环境、跑脚本！
- **跨平台**：让`auto_setup_run_win_and_mac.py`在macOS稳如老狗，再补点说明。
- **依赖管理**：加Python版本检查，争取自动下Python、Redis、Node.js（懒人梦想，冲！）。
- Docker部署：这个非非还不会，要是你能编写就好了...

**非非的终极提醒**：路径选错我可不负责！有好点子？改脚本吧，别来烦我，众所周知，非非超渣！😜

## 脚本对比

| 特性 | `auto_setup_run_win.py` | `auto_setup_run_win_and_mac.py` | `local_start.bat` |
|------|:-----------------------:|---------------------------------|-------------------|
| **平台** | Windows | Windows, macOS | Windows |
| **功能** | 自动检查、装依赖、启动系统 | 同Windows版，跨平台 | 自动下载依赖、启动系统 |
| **使用** | `python auto_setup_run_win.py`，选路径 | `python auto_setup_run_win_and_mac.py`，选路径 | 双击`local_start.bat` |
| **依赖** | Python（3.12推荐）、Redis、Node.js（手动装） | 同Windows版 | Python（3.8+），自动下Node.js v20.17.0、Redis 5.0.14.1 |
| **路径选择** | 手动选 | 手动选 | 自动下到项目目录 |
| **亮点** | 环境检测、端口扫描、日志、自动清理 | 同Windows版，适配macOS | 自动下载、错误暂停、窗口化 |
| **输出** | 前端：`http://localhost:5173`<br>后端：`http://0.0.0.0:8000` | 同Windows版 | 同Python脚本，分窗口 |
| **坑点** | 手动装依赖，路径要准 | macOS好多bug，没办法，非非没有mac | 固定版本，无路径选择，`.env`手动配 |