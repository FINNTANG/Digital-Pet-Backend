# Django LLM 项目 1Panel 部署完整指南

## 📖 项目概览

### 项目特点
- **框架**: Django 5.2.7
- **数据库**: SQLite（可升级为PostgreSQL/MySQL）
- **核心功能**:
  - 用户管理系统（注册/登录/个人中心）
  - AI聊天服务（多宠物人格：狐狸/狗/蛇）
  - 情绪识别（DeepFace + GPT-4o Vision）
  - REST API + JWT认证
  - 支持游客访问
- **技术栈**: LangChain + OpenAI + Django REST Framework

---

## 🎯 部署目标

完成本指南后，你将实现：
- ✅ 项目在生产环境运行
- ✅ 使用 Nginx 反向代理
- ✅ SSL/HTTPS 加密访问
- ✅ 自动重启和进程守护
- ✅ 日志监控和管理
- ✅ 静态文件高效服务

---

## 📋 前置要求

### 1Panel 版本要求
- 1Panel 版本：>= 1.10.0
- 操作系统：Ubuntu 20.04+ / Debian 11+ / CentOS 8+

### 服务器配置建议
| 配置项 | 最低配置 | 推荐配置 |
|--------|----------|----------|
| CPU | 1核 | 2核+ |
| 内存 | 2GB | 4GB+ |
| 硬盘 | 20GB | 40GB+ |
| 带宽 | 1Mbps | 5Mbps+ |

### 域名和证书（可选）
- 域名已解析到服务器IP
- 用于配置HTTPS访问

---

## 🚀 部署步骤

## 第一阶段：1Panel 环境准备

### 1.1 安装 1Panel（如果尚未安装）

```bash
# 官方一键安装脚本
curl -sSL https://resource.fit2cloud.com/1panel/package/quick_start.sh -o quick_start.sh && bash quick_start.sh
```

安装完成后：
- 访问：`http://服务器IP:端口`
- 登录 1Panel 控制台

### 1.2 安装必要的运行时

在 1Panel 控制台中安装：

#### a. 安装 Python 运行时
1. 进入 **应用商店** → **运行环境**
2. 找到 **Python**，点击安装
3. 选择版本：**Python 3.11** （推荐）
4. 等待安装完成

#### b. 安装 OpenResty（Nginx）
1. 在 **应用商店** → **Web服务器**
2. 安装 **OpenResty** 或 **Nginx**
3. 安装完成后会自动启动

#### c. 安装数据库（可选，用于生产环境）
如果要升级到 MySQL/PostgreSQL：
1. 在 **应用商店** → **数据库**
2. 安装 **MySQL 8.0** 或 **PostgreSQL 14**
3. 记录数据库密码

---

## 第二阶段：项目部署

### 2.1 创建项目目录

使用 1Panel 的 **文件管理** 或 SSH 连接：

```bash
# 创建项目根目录
mkdir -p /opt/django_llm
cd /opt/django_llm

# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 2.2 上传项目文件

**方法一：使用 1Panel 文件管理器**
1. 进入 **文件** → **文件管理**
2. 导航到 `/opt/django_llm`
3. 上传整个项目文件夹（或压缩包后上传解压）

**方法二：使用 Git（推荐）**
```bash
cd /opt/django_llm
git clone <你的项目仓库地址> .

# 或使用SFTP上传
# 使用 WinSCP、FileZilla 等工具上传
```

### 2.3 安装项目依赖

```bash
# 确保虚拟环境已激活
source /opt/django_llm/venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
cd /opt/django_llm
pip install -r requirements.txt

# 如果遇到 DeepFace 安装问题，可以尝试：
pip install deepface --no-deps
pip install tf-keras tensorflow
```

**常见问题处理**：
```bash
# 如果缺少系统依赖，安装：
sudo apt-get update
sudo apt-get install -y python3-dev build-essential libpq-dev

# 如果遇到 Pillow 安装问题：
sudo apt-get install -y libjpeg-dev zlib1g-dev
```

---

## 第三阶段：项目配置

### 3.1 修改生产环境配置

编辑 `mysite/settings.py`：

```python
# ========== 生产环境配置 ==========

# 1. 关闭调试模式
DEBUG = False

# 2. 配置允许的域名
ALLOWED_HOSTS = [
    'yourdomain.com',      # 你的域名
    'www.yourdomain.com',  # www域名
    '服务器IP地址',         # 服务器IP
    'localhost',
    '127.0.0.1',
]

# 3. 安全配置
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '请生成新的密钥')

# 4. 数据库配置（如果使用MySQL）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_llm',
        'USER': 'django_user',
        'PASSWORD': os.environ.get('DB_PASSWORD', '数据库密码'),
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# 5. 静态文件配置
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# 6. 安全增强
SECURE_SSL_REDIRECT = True  # 强制HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 7. CORS 配置（生产环境）
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]
```

### 3.2 生成新的 SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

将生成的密钥配置到环境变量或 settings.py 中。

### 3.3 创建环境变量文件

创建 `.env` 文件（可选）：

```bash
cd /opt/django_llm
nano .env
```

添加内容：
```env
# Django 配置
DJANGO_SECRET_KEY=你生成的密钥
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,服务器IP

# 数据库配置（如果使用MySQL）
DB_ENGINE=django.db.backends.mysql
DB_NAME=django_llm
DB_USER=django_user
DB_PASSWORD=数据库密码
DB_HOST=localhost
DB_PORT=3306

# LLM API 配置
OPENAI_API_KEY=你的OpenAI_API密钥
OPENAI_API_BASE=https://api.openai.com/v1
```

### 3.4 数据库迁移

```bash
# 激活虚拟环境
source /opt/django_llm/venv/bin/activate

# 执行迁移
cd /opt/django_llm
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput
```

---

## 第四阶段：配置 Gunicorn

### 4.1 安装 Gunicorn

```bash
source /opt/django_llm/venv/bin/activate
pip install gunicorn
```

### 4.2 创建 Gunicorn 配置文件

```bash
nano /opt/django_llm/gunicorn_config.py
```

添加内容：
```python
"""
Gunicorn 配置文件
"""
import multiprocessing

# 绑定地址和端口
bind = "127.0.0.1:8000"

# 工作进程数（推荐：CPU核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# 工作线程数
threads = 2

# 工作模式
worker_class = "sync"

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 超时时间（秒）
timeout = 120

# 优雅重启超时
graceful_timeout = 30

# 保活
keepalive = 5

# 日志
accesslog = "/opt/django_llm/logs/gunicorn_access.log"
errorlog = "/opt/django_llm/logs/gunicorn_error.log"
loglevel = "info"

# 进程名称
proc_name = "django_llm"

# 守护进程
daemon = False

# PID文件
pidfile = "/opt/django_llm/gunicorn.pid"

# 用户和组
# user = "www-data"
# group = "www-data"
```

### 4.3 创建日志目录

```bash
mkdir -p /opt/django_llm/logs
```

### 4.4 测试 Gunicorn

```bash
source /opt/django_llm/venv/bin/activate
cd /opt/django_llm

# 测试运行
gunicorn -c gunicorn_config.py mysite.wsgi:application
```

如果启动成功，按 `Ctrl+C` 停止，继续下一步。

---

## 第五阶段：配置系统服务

### 5.1 使用 1Panel 的进程守护功能

1. 进入 1Panel → **网站** → **运行环境** → **进程守护**
2. 点击 **创建进程守护**
3. 配置如下：

| 配置项 | 值 |
|--------|-----|
| 名称 | django_llm |
| 启动命令 | `/opt/django_llm/venv/bin/gunicorn -c /opt/django_llm/gunicorn_config.py mysite.wsgi:application` |
| 工作目录 | `/opt/django_llm` |
| 用户 | www-data 或 root |
| 自动启动 | 是 |

4. 点击 **保存并启动**

### 5.2 或使用 Systemd（替代方案）

创建服务文件：
```bash
sudo nano /etc/systemd/system/django_llm.service
```

添加内容：
```ini
[Unit]
Description=Django LLM Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/django_llm
Environment="PATH=/opt/django_llm/venv/bin"
ExecStart=/opt/django_llm/venv/bin/gunicorn -c /opt/django_llm/gunicorn_config.py mysite.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start django_llm
sudo systemctl enable django_llm
sudo systemctl status django_llm
```

---

## 第六阶段：配置 Nginx 反向代理

### 6.1 使用 1Panel 创建网站

1. 进入 1Panel → **网站** → **网站管理**
2. 点击 **创建网站**
3. 配置如下：

| 配置项 | 值 |
|--------|-----|
| 网站类型 | 反向代理 |
| 主域名 | yourdomain.com |
| 代理地址 | http://127.0.0.1:8000 |
| 启用 HTTPS | 是（如果有域名） |

4. 高级配置 - 点击 **配置文件**，修改为：

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # 强制HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL 证书（1Panel自动配置）
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 日志
    access_log /opt/django_llm/logs/nginx_access.log;
    error_log /opt/django_llm/logs/nginx_error.log;
    
    # 客户端上传限制
    client_max_body_size 50M;
    
    # 静态文件
    location /static/ {
        alias /opt/django_llm/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias /opt/django_llm/media/;
        expires 7d;
    }
    
    # 反向代理到 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时配置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

5. 点击 **保存**

### 6.2 配置 SSL 证书（如果有域名）

在 1Panel 中：
1. 进入 **网站** → 选择你的网站 → **SSL证书**
2. 选择 **Let's Encrypt** 或上传自己的证书
3. 点击 **申请** 或 **上传**
4. 证书会自动配置和续期

### 6.3 重启 Nginx

```bash
# 在 1Panel 中重启 OpenResty/Nginx
# 或使用命令行
sudo systemctl restart openresty
```

---

## 第七阶段：配置 Django Admin LLM

### 7.1 登录 Django 管理后台

访问：`https://yourdomain.com/admin/`

使用之前创建的超级用户登录。

### 7.2 添加 LLM 配置

1. 进入 **LLM配置** → **增加 LLM配置**
2. 填写配置：

| 字段 | 值 |
|------|-----|
| 配置名称 | OpenAI GPT-4o |
| 提供商 | OpenAI |
| 模型名称 | openai/chatgpt-4o-latest |
| API密钥 | 你的API密钥 |
| API基础URL | https://openrouter.ai/api/v1 |
| 温度 | 0.7 |
| 最大令牌数 | 4000 |
| 是否启用 | ✓ |

3. 点击 **保存**

---

## 第八阶段：测试和验证

### 8.1 功能测试清单

```bash
# 1. 检查服务状态
sudo systemctl status django_llm

# 2. 检查日志
tail -f /opt/django_llm/logs/gunicorn_error.log
tail -f /opt/django_llm/logs/nginx_access.log

# 3. 测试 API
curl http://localhost:8000/api/docs/
```

### 8.2 访问测试

| 功能 | URL | 期望结果 |
|------|-----|----------|
| 首页 | https://yourdomain.com/ | 正常显示 |
| 注册 | https://yourdomain.com/accounts/register/ | 可以注册 |
| 登录 | https://yourdomain.com/accounts/login/ | 可以登录 |
| AI聊天 | https://yourdomain.com/llm/chat/ | 游客可访问 |
| API文档 | https://yourdomain.com/api/docs/ | 显示Swagger文档 |
| 管理后台 | https://yourdomain.com/admin/ | 可以登录 |

### 8.3 性能测试（可选）

```bash
# 安装 Apache Bench
sudo apt-get install apache2-utils

# 并发测试
ab -n 1000 -c 10 https://yourdomain.com/
```

---

## 第九阶段：监控和维护

### 9.1 日志管理

配置日志轮转：
```bash
sudo nano /etc/logrotate.d/django_llm
```

添加内容：
```
/opt/django_llm/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload django_llm > /dev/null 2>&1 || true
    endscript
}
```

### 9.2 数据库备份

在 1Panel 中：
1. 进入 **数据库** → 选择数据库
2. 点击 **备份** → 配置定时备份
3. 推荐：每天凌晨3点备份，保留7天

或使用脚本：
```bash
nano /opt/django_llm/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/django_llm"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/django_llm/db.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# 备份媒体文件
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /opt/django_llm/media/

# 删除7天前的备份
find $BACKUP_DIR -name "*.sqlite3" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

添加定时任务：
```bash
chmod +x /opt/django_llm/backup.sh
crontab -e
```

添加：
```
0 3 * * * /opt/django_llm/backup.sh >> /opt/django_llm/logs/backup.log 2>&1
```

### 9.3 监控告警

在 1Panel 中：
1. 进入 **监控** → **主机监控**
2. 配置告警规则：
   - CPU 使用率 > 80%
   - 内存使用率 > 80%
   - 磁盘使用率 > 90%
3. 配置通知方式（邮件/钉钉/企业微信）

---

## 🔒 安全加固

### 10.1 防火墙配置

```bash
# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 允许 SSH（确保已配置）
sudo ufw allow 22/tcp

# 启用防火墙
sudo ufw enable

# 检查状态
sudo ufw status
```

### 10.2 限制访问

在 Nginx 配置中添加：
```nginx
# 限制请求频率
limit_req_zone $binary_remote_addr zone=django:10m rate=10r/s;

server {
    # ...
    
    location / {
        limit_req zone=django burst=20 nodelay;
        # ...
    }
}
```

### 10.3 禁用不必要的端口

```bash
# 确保 Gunicorn 只监听本地
# 在 gunicorn_config.py 中：
bind = "127.0.0.1:8000"  # 不要使用 0.0.0.0
```

---

## 🐛 常见问题排查

### 问题1：502 Bad Gateway

**原因**：Gunicorn 未启动或无法连接

**解决**：
```bash
# 检查 Gunicorn 状态
sudo systemctl status django_llm

# 查看日志
tail -f /opt/django_llm/logs/gunicorn_error.log

# 重启服务
sudo systemctl restart django_llm
```

### 问题2：静态文件404

**原因**：静态文件未正确收集或Nginx配置错误

**解决**：
```bash
# 重新收集静态文件
source /opt/django_llm/venv/bin/activate
python manage.py collectstatic --noinput

# 检查权限
sudo chown -R www-data:www-data /opt/django_llm/staticfiles/
```

### 问题3：数据库连接失败

**原因**：数据库未启动或配置错误

**解决**：
```bash
# 检查数据库服务
sudo systemctl status mysql

# 测试连接
mysql -u django_user -p django_llm

# 检查 settings.py 中的数据库配置
```

### 问题4：LLM API 调用失败

**原因**：API密钥错误或网络问题

**解决**：
```bash
# 在管理后台检查 LLM 配置
# 确保 API 密钥正确
# 测试网络连接
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 问题5：内存占用过高

**原因**：DeepFace 模型加载或工作进程过多

**解决**：
```python
# 减少 Gunicorn workers 数量
# 在 gunicorn_config.py 中：
workers = 2  # 降低数量

# 或禁用 DeepFace（如果不需要情绪识别）
# 注释掉相关导入和调用
```

---

## 📊 性能优化建议

### 1. 使用 Redis 缓存

```bash
# 安装 Redis
pip install django-redis

# 在 settings.py 中配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
```

### 2. 数据库优化

```python
# 使用 PostgreSQL 替代 SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_llm',
        'USER': 'django_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # 连接池
    }
}
```

### 3. 启用 Gzip 压缩

在 Nginx 配置中：
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

### 4. CDN 加速（可选）

将静态文件上传到 CDN：
- 阿里云 OSS
- 腾讯云 COS
- 七牛云

---

## 🎓 进阶配置

### 使用 Celery 异步任务

```bash
# 安装 Celery
pip install celery redis

# 创建 celery.py 配置文件
# 用于处理 LLM 请求、情绪识别等耗时任务
```

### 配置 WebSocket（实时聊天）

```bash
# 安装 Channels
pip install channels channels-redis

# 配置 ASGI
# 实现实时消息推送
```

---

## ✅ 部署检查清单

完成以下检查确保部署成功：

- [ ] Python 3.11+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖已安装
- [ ] settings.py 已配置为生产环境
- [ ] SECRET_KEY 已更新
- [ ] ALLOWED_HOSTS 已配置
- [ ] 数据库迁移已完成
- [ ] 超级用户已创建
- [ ] 静态文件已收集
- [ ] Gunicorn 配置完成
- [ ] 系统服务已创建并启动
- [ ] Nginx 反向代理已配置
- [ ] SSL 证书已配置（如果有域名）
- [ ] 防火墙已配置
- [ ] 日志轮转已配置
- [ ] 数据库备份已配置
- [ ] LLM API 已配置并测试
- [ ] 所有功能已测试通过

---

## 📞 技术支持

### 相关文档
- Django 官方文档: https://docs.djangoproject.com/
- 1Panel 官方文档: https://1panel.cn/docs/
- Gunicorn 文档: https://docs.gunicorn.org/

### 常用命令速查

```bash
# 重启应用
sudo systemctl restart django_llm

# 查看日志
tail -f /opt/django_llm/logs/gunicorn_error.log

# 进入 Django Shell
source /opt/django_llm/venv/bin/activate
python manage.py shell

# 清理会话
python manage.py clearsessions

# 创建管理员
python manage.py createsuperuser
```

---

## 🎉 部署完成

恭喜！你的 Django LLM 项目已成功部署到 1Panel。

现在你可以：
- ✅ 通过域名访问应用
- ✅ 在管理后台管理用户和配置
- ✅ 使用 AI 聊天功能
- ✅ 通过 API 进行集成

**祝您使用愉快！**

---

*最后更新：2025-10-27*








