# 定义路径
$source = "C:\Users\你的用户名\AppData\Local\Docker"
$dest = "D:\Docker-link"
$backupRoot = "D:\2.Backup\Docker"
$backup = "$backupRoot\$($source -replace '[:\\]', '_')"
$logPath = "D:\Docker_MoveLog.txt"

# 函数：写入日志
function Write-Log {
    param([string]$message)
    $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'): $message"
    Add-Content -Path $logPath -Value $logMessage -Force
    Write-Host $message
}

# 函数：回滚操作
function Rollback {
    param([string]$source, [string]$backup)
    Write-Log "开始回滚操作..."

    # 删除符号链接（如果存在）
    if (Test-Path $source -PathType Container) {
        $item = Get-Item $source -Force
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            (Get-Item $source).Delete()
            Write-Log "已删除符号链接。"
        }
    }

    # 恢复备份
    if (Test-Path $backup) {
        if (Test-Path $source) {
            Remove-Item -Path $source -Recurse -Force
        }
        Copy-Item -Path $backup -Destination $source -Recurse -Force
        Write-Log "已从备份恢复原始文件夹。"
    }

    # 删除目标文件夹（如果存在）
    if (Test-Path $dest) {
        Remove-Item -Path $dest -Recurse -Force
        Write-Log "已删除目标文件夹。"
    }
    Write-Log "回滚操作完成。"
}

# 主逻辑
try {
    # 确保 Docker Desktop 已关闭
    Write-Log "正在检查 Docker Desktop 是否运行..."
    $dockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
    if ($dockerProcess) {
        throw "Docker Desktop 正在运行，请先关闭 Docker Desktop。"
    }

    # 确保日志文件目录存在
    $logDir = Split-Path $logPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -Path $logDir -ItemType Directory -Force | Out-Null
    }

    # 检查源路径是否存在
    if (-not (Test-Path $source)) {
        throw "源路径 $source 不存在。"
    }

    # 创建目标路径（如果不存在）
    if (-not (Test-Path $dest)) {
        New-Item -Path $dest -ItemType Directory -Force | Out-Null
        Write-Log "已创建目标路径 $dest"
    }

    # 创建备份
    Write-Log "正在创建备份..."
    New-Item -Path $backup -ItemType Directory -Force | Out-Null
    Copy-Item -Path $source -Destination $backup -Recurse -Force
    Write-Log "备份已创建在 $backup"

    # 使用 robocopy 复制文件
    Write-Log "正在复制文件到目标路径..."
    robocopy $source $dest /E /COPYALL /DCOPY:DAT /R:3 /W:10 /NFL /NDL /NJH /NJS /NC /NS /NP | Out-Null

    if ($LASTEXITCODE -ge 8) {
        throw "文件复制失败。Robocopy 退出代码: $LASTEXITCODE"
    }
    Write-Log "文件复制完成。"

    # 删除原始文件夹
    Remove-Item -Path $source -Recurse -Force
    Write-Log "原始文件夹已删除。"

    # 创建符号链接
    New-Item -ItemType SymbolicLink -Path $source -Target $dest | Out-Null
    Write-Log "符号链接已创建。"

    Write-Log "操作完成。Docker 文件夹已成功迁移到 D 盘并创建了符号链接。"
}
catch {
    Write-Log "错误：$($_.Exception.Message)"
    Rollback -source $source -backup $backup
    exit 1
}
finally {
    # 备份默认保留，不自动删除
    # 如果需要删除备份，取消注释以下行
    # Remove-Item -Path $backup -Recurse -Force
}