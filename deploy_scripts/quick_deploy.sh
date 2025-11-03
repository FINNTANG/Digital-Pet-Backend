#!/bin/bash
# Django LLM 项目快速部署脚本
# 适用于 1Panel 环境

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量（根据实际情况修改）
PROJECT_NAME="django_llm"
PROJECT_DIR="/opt/${PROJECT_NAME}"
VENV_PATH="${PROJECT_DIR}/venv"
PYTHON_VERSION="python3.11"
DOMAIN="yourdomain.com"

# 打印带颜色的消息
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# 检查是否以 root 身份运行
check_root() {
    if [[ $EUID -ne 0 ]]; then
       print_error "此脚本需要 root 权限运行"
       exit 1
    fi
}

# 检查 Python 版本
check_python() {
    print_info "检查 Python 版本..."
    if ! command -v $PYTHON_VERSION &> /dev/null; then
        print_error "$PYTHON_VERSION 未安装"
        print_info "请先安装 Python 3.11+"
        exit 1
    fi
    PYTHON_VER=$($PYTHON_VERSION --version)
    print_success "Python 版本: $PYTHON_VER"
}

# 创建项目目录
create_directories() {
    print_info "创建项目目录..."
    mkdir -p $PROJECT_DIR
    mkdir -p $PROJECT_DIR/logs
    mkdir -p $PROJECT_DIR/media
    mkdir -p $PROJECT_DIR/staticfiles
    mkdir -p /opt/backups/$PROJECT_NAME
    print_success "目录创建完成"
}

# 创建虚拟环境
create_venv() {
    print_info "创建 Python 虚拟环境..."
    cd $PROJECT_DIR
    $PYTHON_VERSION -m venv venv
    print_success "虚拟环境创建完成"
}

# 安装依赖
install_dependencies() {
    print_info "安装项目依赖..."
    source $VENV_PATH/bin/activate
    pip install --upgrade pip
    
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        pip install -r $PROJECT_DIR/requirements.txt
        print_success "依赖安装完成"
    else
        print_error "未找到 requirements.txt 文件"
        exit 1
    fi
}

# 配置环境变量
setup_env() {
    print_info "配置环境变量..."
    
    # 生成 SECRET_KEY
    SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    cat > $PROJECT_DIR/.env << EOF
# Django 配置
DJANGO_SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},localhost,127.0.0.1

# 数据库配置（默认使用SQLite）
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=${PROJECT_DIR}/db.sqlite3

# LLM API 配置（需要手动填写）
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
EOF
    
    print_success "环境变量配置完成"
    print_info "请编辑 $PROJECT_DIR/.env 文件，填写 API 密钥"
}

# 数据库迁移
migrate_database() {
    print_info "执行数据库迁移..."
    source $VENV_PATH/bin/activate
    cd $PROJECT_DIR
    
    python manage.py makemigrations
    python manage.py migrate
    
    print_success "数据库迁移完成"
}

# 收集静态文件
collect_static() {
    print_info "收集静态文件..."
    source $VENV_PATH/bin/activate
    cd $PROJECT_DIR
    
    python manage.py collectstatic --noinput
    
    print_success "静态文件收集完成"
}

# 创建超级用户（交互式）
create_superuser() {
    print_info "创建管理员账号..."
    source $VENV_PATH/bin/activate
    cd $PROJECT_DIR
    
    python manage.py createsuperuser
    
    print_success "管理员账号创建完成"
}

# 设置权限
set_permissions() {
    print_info "设置文件权限..."
    chown -R www-data:www-data $PROJECT_DIR
    chmod -R 755 $PROJECT_DIR
    chmod -R 775 $PROJECT_DIR/media
    chmod -R 775 $PROJECT_DIR/logs
    print_success "权限设置完成"
}

# 创建 Gunicorn 配置
create_gunicorn_config() {
    print_info "创建 Gunicorn 配置..."
    
    cat > $PROJECT_DIR/gunicorn_config.py << 'EOF'
"""
Gunicorn 配置文件
"""
import multiprocessing
import os

# 绑定地址和端口
bind = "127.0.0.1:8000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作线程数
threads = 2

# 工作模式
worker_class = "sync"

# 最大请求数
max_requests = 1000
max_requests_jitter = 50

# 超时时间
timeout = 120
graceful_timeout = 30
keepalive = 5

# 日志
accesslog = "/opt/django_llm/logs/gunicorn_access.log"
errorlog = "/opt/django_llm/logs/gunicorn_error.log"
loglevel = "info"

# 进程名称
proc_name = "django_llm"

# PID文件
pidfile = "/opt/django_llm/gunicorn.pid"

# 守护进程
daemon = False
EOF
    
    print_success "Gunicorn 配置创建完成"
}

# 创建 systemd 服务
create_systemd_service() {
    print_info "创建 systemd 服务..."
    
    cat > /etc/systemd/system/${PROJECT_NAME}.service << EOF
[Unit]
Description=Django LLM Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${VENV_PATH}/bin"
ExecStart=${VENV_PATH}/bin/gunicorn -c ${PROJECT_DIR}/gunicorn_config.py mysite.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable ${PROJECT_NAME}
    print_success "systemd 服务创建完成"
}

# 启动服务
start_service() {
    print_info "启动应用服务..."
    systemctl start ${PROJECT_NAME}
    sleep 3
    
    if systemctl is-active --quiet ${PROJECT_NAME}; then
        print_success "服务启动成功"
    else
        print_error "服务启动失败，请检查日志"
        journalctl -u ${PROJECT_NAME} -n 50
        exit 1
    fi
}

# 创建备份脚本
create_backup_script() {
    print_info "创建备份脚本..."
    
    cat > $PROJECT_DIR/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/django_llm"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/opt/django_llm"

mkdir -p $BACKUP_DIR

# 备份数据库
cp $PROJECT_DIR/db.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# 备份媒体文件
tar -czf $BACKUP_DIR/media_$DATE.tar.gz $PROJECT_DIR/media/

# 删除7天前的备份
find $BACKUP_DIR -name "*.sqlite3" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF
    
    chmod +x $PROJECT_DIR/backup.sh
    
    # 添加到 crontab
    (crontab -l 2>/dev/null; echo "0 3 * * * $PROJECT_DIR/backup.sh >> $PROJECT_DIR/logs/backup.log 2>&1") | crontab -
    
    print_success "备份脚本创建完成（每天凌晨3点执行）"
}

# 配置防火墙
configure_firewall() {
    print_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        ufw allow 80/tcp
        ufw allow 443/tcp
        print_success "防火墙规则已添加"
    else
        print_info "未检测到 ufw，请手动配置防火墙"
    fi
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "=========================================="
    echo "  🎉 部署完成！"
    echo "=========================================="
    echo ""
    echo "项目目录: $PROJECT_DIR"
    echo "虚拟环境: $VENV_PATH"
    echo "配置文件: $PROJECT_DIR/.env"
    echo ""
    echo "服务管理命令："
    echo "  启动服务: sudo systemctl start $PROJECT_NAME"
    echo "  停止服务: sudo systemctl stop $PROJECT_NAME"
    echo "  重启服务: sudo systemctl restart $PROJECT_NAME"
    echo "  查看状态: sudo systemctl status $PROJECT_NAME"
    echo "  查看日志: tail -f $PROJECT_DIR/logs/gunicorn_error.log"
    echo ""
    echo "下一步："
    echo "  1. 编辑 $PROJECT_DIR/.env 文件，配置 API 密钥"
    echo "  2. 配置 Nginx 反向代理（参考部署文档）"
    echo "  3. 配置 SSL 证书（如果有域名）"
    echo "  4. 访问 http://localhost:8000/admin/ 配置 LLM"
    echo ""
    echo "=========================================="
}

# 主流程
main() {
    echo "=========================================="
    echo "  Django LLM 项目快速部署脚本"
    echo "=========================================="
    echo ""
    
    check_root
    check_python
    create_directories
    
    # 检查项目文件是否存在
    if [ ! -f "$PROJECT_DIR/manage.py" ]; then
        print_error "项目文件不存在！"
        print_info "请先将项目文件上传到 $PROJECT_DIR"
        exit 1
    fi
    
    create_venv
    install_dependencies
    setup_env
    migrate_database
    collect_static
    
    # 交互式创建管理员
    read -p "是否创建管理员账号？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_superuser
    fi
    
    set_permissions
    create_gunicorn_config
    create_systemd_service
    start_service
    create_backup_script
    configure_firewall
    
    show_deployment_info
}

# 运行主流程
main "$@"








