# Django LLM 项目部署脚本说明

本目录包含用于快速部署 Django LLM 项目的脚本和配置文件。

## 📁 文件说明

### 1. quick_deploy.sh
自动化部署脚本，一键完成大部分部署工作。

**功能**：
- ✅ 检查 Python 环境
- ✅ 创建项目目录结构
- ✅ 创建虚拟环境
- ✅ 安装项目依赖
- ✅ 配置环境变量
- ✅ 执行数据库迁移
- ✅ 收集静态文件
- ✅ 创建管理员账号
- ✅ 设置文件权限
- ✅ 配置 Gunicorn
- ✅ 创建 systemd 服务
- ✅ 配置自动备份
- ✅ 配置防火墙

**使用方法**：
```bash
# 1. 上传项目文件到 /opt/django_llm
# 2. 上传此脚本
# 3. 赋予执行权限
chmod +x quick_deploy.sh

# 4. 以 root 身份运行
sudo ./quick_deploy.sh
```

**注意事项**：
- 脚本需要 root 权限
- 运行前确保项目文件已上传到 `/opt/django_llm`
- 脚本会自动生成 SECRET_KEY 和环境变量文件
- 部署完成后需要手动编辑 `.env` 文件填写 API 密钥

### 2. production_settings.py
Django 生产环境配置模板。

**功能**：
- 生产环境安全配置
- 数据库配置（SQLite/MySQL/PostgreSQL）
- 静态文件配置
- 日志配置
- 缓存配置（Redis）
- 邮件配置
- 性能优化配置

**使用方法**：
```bash
# 1. 复制到项目 mysite 目录
cp production_settings.py /opt/django_llm/mysite/settings_production.py

# 2. 在 settings.py 末尾添加
echo "
try:
    from .settings_production import *
except ImportError:
    pass
" >> /opt/django_llm/mysite/settings.py

# 3. 根据实际情况修改配置
nano /opt/django_llm/mysite/settings_production.py
```

**配置说明**：
- 默认使用 SQLite，可切换到 MySQL/PostgreSQL
- 所有敏感信息通过环境变量读取
- 包含完整的安全配置和日志配置
- 提供 Redis 缓存配置（注释状态）

### 3. nginx_config_template.conf
Nginx 反向代理配置模板。

**功能**：
- HTTP 到 HTTPS 重定向
- SSL/TLS 安全配置
- 静态文件服务优化
- 媒体文件服务
- Gzip 压缩
- 请求限流
- 安全头部配置
- WebSocket 支持

**使用方法**：

**方法一：在 1Panel 中使用**
1. 登录 1Panel
2. 进入 **网站** → **网站管理** → **创建网站**
3. 选择 **反向代理**
4. 点击 **配置文件**
5. 将模板内容复制粘贴，修改域名和路径
6. 保存并重启

**方法二：手动配置**
```bash
# 1. 复制配置文件
sudo cp nginx_config_template.conf /etc/nginx/sites-available/django_llm.conf

# 2. 修改配置
sudo nano /etc/nginx/sites-available/django_llm.conf
# 替换 yourdomain.com 为你的域名
# 替换 /path/to/your/cert.pem 为实际证书路径

# 3. 创建软链接
sudo ln -s /etc/nginx/sites-available/django_llm.conf /etc/nginx/sites-enabled/

# 4. 测试配置
sudo nginx -t

# 5. 重启 Nginx
sudo systemctl restart nginx
```

**限流配置**：
需要在 `nginx.conf` 或主配置文件的 `http` 块中添加：
```nginx
limit_req_zone $binary_remote_addr zone=django_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=5r/s;
limit_conn_zone $binary_remote_addr zone=addr:10m;
```

## 🚀 快速开始

### 完整部署流程

```bash
# 1. 上传项目文件
# 使用 SFTP 或 1Panel 文件管理器上传到 /opt/django_llm

# 2. 运行部署脚本
cd /path/to/deploy_scripts
chmod +x quick_deploy.sh
sudo ./quick_deploy.sh

# 3. 配置环境变量
sudo nano /opt/django_llm/.env
# 填写 OPENAI_API_KEY 等

# 4. 配置 Nginx（使用 1Panel 或手动配置）

# 5. 配置 SSL 证书（如果有域名）

# 6. 访问网站
# http://yourdomain.com（会自动跳转到 HTTPS）

# 7. 配置 LLM
# 访问 https://yourdomain.com/admin/
# 添加 LLM 配置
```

## 📋 部署后检查清单

- [ ] 服务运行正常：`sudo systemctl status django_llm`
- [ ] Nginx 配置正确：`sudo nginx -t`
- [ ] SSL 证书有效（如果配置了）
- [ ] 静态文件可访问：`https://yourdomain.com/static/`
- [ ] 管理后台可访问：`https://yourdomain.com/admin/`
- [ ] API 文档可访问：`https://yourdomain.com/api/docs/`
- [ ] 聊天功能正常：`https://yourdomain.com/llm/chat/`
- [ ] 日志正常记录：`tail -f /opt/django_llm/logs/gunicorn_error.log`
- [ ] 备份脚本已配置：`crontab -l`

## 🔧 常用维护命令

### 服务管理
```bash
# 启动服务
sudo systemctl start django_llm

# 停止服务
sudo systemctl stop django_llm

# 重启服务
sudo systemctl restart django_llm

# 查看状态
sudo systemctl status django_llm

# 查看日志
sudo journalctl -u django_llm -n 100
```

### 日志查看
```bash
# Gunicorn 访问日志
tail -f /opt/django_llm/logs/gunicorn_access.log

# Gunicorn 错误日志
tail -f /opt/django_llm/logs/gunicorn_error.log

# Django 日志
tail -f /opt/django_llm/logs/django.log

# Nginx 访问日志
tail -f /opt/django_llm/logs/nginx_access.log

# Nginx 错误日志
tail -f /opt/django_llm/logs/nginx_error.log
```

### 代码更新
```bash
# 1. 拉取最新代码
cd /opt/django_llm
git pull

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装新依赖
pip install -r requirements.txt

# 4. 数据库迁移
python manage.py migrate

# 5. 收集静态文件
python manage.py collectstatic --noinput

# 6. 重启服务
sudo systemctl restart django_llm
```

### 数据库管理
```bash
# 进入 Django Shell
cd /opt/django_llm
source venv/bin/activate
python manage.py shell

# 创建管理员
python manage.py createsuperuser

# 清理会话
python manage.py clearsessions

# 数据库备份（手动）
cp /opt/django_llm/db.sqlite3 /opt/backups/django_llm/db_$(date +%Y%m%d).sqlite3
```

## 🛡️ 安全建议

1. **定期更新**
   ```bash
   sudo apt update && sudo apt upgrade
   pip install --upgrade pip
   pip list --outdated
   ```

2. **监控日志**
   - 定期检查错误日志
   - 关注异常访问模式
   - 设置日志告警

3. **备份策略**
   - 每日自动备份数据库
   - 每周备份媒体文件
   - 异地存储重要备份

4. **防火墙规则**
   ```bash
   sudo ufw status
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

5. **SSL 证书续期**
   - Let's Encrypt 证书会自动续期
   - 检查续期状态：`sudo certbot renew --dry-run`

## 📞 获取帮助

遇到问题？
1. 查看日志文件了解详细错误
2. 参考主部署文档：`../1Panel部署指南.md`
3. 检查环境变量配置
4. 确认服务状态和端口占用

## 📝 自定义配置

### 修改端口
在 `gunicorn_config.py` 中：
```python
bind = "127.0.0.1:8000"  # 修改为其他端口
```

### 修改工作进程数
在 `gunicorn_config.py` 中：
```python
workers = 4  # 根据服务器配置调整
```

### 修改域名
1. 编辑 `.env` 文件的 `ALLOWED_HOSTS`
2. 修改 Nginx 配置中的 `server_name`
3. 更新 SSL 证书（如果域名变更）
4. 重启服务

---

**祝部署顺利！** 🎉








