#!/bin/bash

# Digital Pet Backend - 快速部署脚本
# 适用于 Linux/Mac 系统

set -e

echo "=========================================="
echo "  Digital Pet Backend - 快速部署脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未检测到 Docker，请先安装 Docker${NC}"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: 未检测到 Docker Compose，请先安装 Docker Compose${NC}"
    exit 1
fi

# 使用 docker compose 或 docker-compose
COMPOSE_CMD="docker compose"
if ! docker compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
fi

echo -e "${GREEN}✓ Docker 和 Docker Compose 已安装${NC}"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}警告: .env 文件不存在${NC}"
    echo "正在从 .env.example 创建 .env 文件..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env 文件已创建${NC}"
        echo -e "${YELLOW}请编辑 .env 文件配置必要的环境变量（特别是生产环境）${NC}"
        echo ""
        read -p "是否现在编辑 .env 文件？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo -e "${RED}错误: .env.example 文件不存在${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env 文件已存在${NC}"
fi

echo ""
echo "=========================================="
echo "  开始部署"
echo "=========================================="
echo ""

# 停止并删除旧容器
echo "1. 停止并删除旧容器..."
$COMPOSE_CMD down

# 构建镜像
echo ""
echo "2. 构建 Docker 镜像..."
$COMPOSE_CMD build

# 启动服务
echo ""
echo "3. 启动服务..."
$COMPOSE_CMD up -d

# 等待服务启动
echo ""
echo "4. 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "5. 检查服务状态..."
$COMPOSE_CMD ps

# 显示日志
echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo -e "${GREEN}服务访问地址：${NC}"
echo "  - API 服务: http://localhost"
echo "  - API 文档: http://localhost/swagger/"
echo "  - Django Admin: http://localhost/admin/"
echo ""
echo -e "${YELLOW}默认管理员账号：${NC}"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo -e "${RED}⚠️  生产环境请立即修改默认密码！${NC}"
echo ""
echo "常用命令："
echo "  查看日志: $COMPOSE_CMD logs -f"
echo "  停止服务: $COMPOSE_CMD down"
echo "  重启服务: $COMPOSE_CMD restart"
echo "  进入容器: $COMPOSE_CMD exec web bash"
echo ""
echo "详细文档请查看: DOCKER_DEPLOYMENT.md"
echo ""
