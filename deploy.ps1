# Digital Pet Backend - 快速部署脚本
# 适用于 Windows 系统

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Digital Pet Backend - 快速部署脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否安装
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker 已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未检测到 Docker，请先安装 Docker Desktop" -ForegroundColor Red
    exit 1
}

# 检查 Docker Compose 是否可用
$composeCmd = "docker compose"
try {
    $composeVersion = & docker compose version 2>&1
    if ($LASTEXITCODE -ne 0) {
        $composeCmd = "docker-compose"
        $composeVersion = docker-compose --version
    }
    Write-Host "✓ Docker Compose 已安装: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未检测到 Docker Compose" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 检查 .env 文件
if (-not (Test-Path .env)) {
    Write-Host "警告: .env 文件不存在" -ForegroundColor Yellow
    Write-Host "正在从 .env.example 创建 .env 文件..."
    
    if (Test-Path .env.example) {
        Copy-Item .env.example .env
        Write-Host "✓ .env 文件已创建" -ForegroundColor Green
        Write-Host "请编辑 .env 文件配置必要的环境变量（特别是生产环境）" -ForegroundColor Yellow
        Write-Host ""
        $edit = Read-Host "是否现在编辑 .env 文件？(y/n)"
        if ($edit -eq "y" -or $edit -eq "Y") {
            notepad .env
        }
    } else {
        Write-Host "错误: .env.example 文件不存在" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ .env 文件已存在" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  开始部署" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 停止并删除旧容器
Write-Host "1. 停止并删除旧容器..." -ForegroundColor Yellow
if ($composeCmd -eq "docker compose") {
    & docker compose down
} else {
    & docker-compose down
}

# 构建镜像
Write-Host ""
Write-Host "2. 构建 Docker 镜像..." -ForegroundColor Yellow
if ($composeCmd -eq "docker compose") {
    & docker compose build
} else {
    & docker-compose build
}

# 启动服务
Write-Host ""
Write-Host "3. 启动服务..." -ForegroundColor Yellow
if ($composeCmd -eq "docker compose") {
    & docker compose up -d
} else {
    & docker-compose up -d
}

# 等待服务启动
Write-Host ""
Write-Host "4. 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host ""
Write-Host "5. 检查服务状态..." -ForegroundColor Yellow
if ($composeCmd -eq "docker compose") {
    & docker compose ps
} else {
    & docker-compose ps
}

# 显示日志
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  部署完成！" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务访问地址：" -ForegroundColor Green
Write-Host "  - API 服务: http://localhost"
Write-Host "  - API 文档: http://localhost/swagger/"
Write-Host "  - Django Admin: http://localhost/admin/"
Write-Host ""
Write-Host "默认管理员账号：" -ForegroundColor Yellow
Write-Host "  用户名: admin"
Write-Host "  密码: admin123"
Write-Host ""
Write-Host "⚠️  生产环境请立即修改默认密码！" -ForegroundColor Red
Write-Host ""
Write-Host "常用命令："
Write-Host "  查看日志: $composeCmd logs -f"
Write-Host "  停止服务: $composeCmd down"
Write-Host "  重启服务: $composeCmd restart"
Write-Host "  进入容器: $composeCmd exec web bash"
Write-Host ""
Write-Host "详细文档请查看: DOCKER_DEPLOYMENT.md"
Write-Host ""
