# Docker 部署指南

本文档详细说明如何使用 Docker 和 Docker Compose 部署 Digital Pet Backend 项目。

## 📋 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [部署步骤](#部署步骤)
- [常用命令](#常用命令)
- [故障排查](#故障排查)
- [生产环境建议](#生产环境建议)

## 🔧 系统要求

- Docker 20.10 或更高版本
- Docker Compose 2.0 或更高版本
- 至少 2GB 可用内存
- 至少 10GB 可用磁盘空间

### 安装 Docker 和 Docker Compose

**Windows/Mac:**
- 下载并安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)

**Linux:**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
```

## 🚀 快速开始

### 1. 克隆项目（如果尚未克隆）

```bash
git clone <repository-url>
cd Digital-Pet-Backend
```

### 2. 创建环境变量文件

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，配置必要的环境变量
# Windows:
notepad .env

# Linux/Mac:
nano .env
```

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 访问应用

- **API 服务**: http://localhost
- **API 文档**: http://localhost/swagger/
- **Django Admin**: http://localhost/admin/

默认管理员账号：
- 用户名: `admin`
- 密码: `admin123`

**⚠️ 生产环境请立即修改默认密码！**

## ⚙️ 配置说明

### 环境变量配置

编辑 `.env` 文件配置以下参数：

#### Django 配置

```env
# 调试模式（生产环境必须设置为 False）
DEBUG=False

# Django 密钥（生产环境必须修改）
SECRET_KEY=your-secret-key-here

# 允许访问的主机（多个用逗号分隔）
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

生成安全的 SECRET_KEY：
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 数据库配置

```env
DB_NAME=digitalpet
DB_USER=digitalpet
DB_PASSWORD=your-strong-password-here
```

#### LLM 服务配置

```env
# OpenAI API 密钥
OPENAI_API_KEY=your-openai-api-key

# OpenAI API 基础 URL（可选，使用其他兼容服务时配置）
OPENAI_API_BASE=https://api.openai.com/v1
```

#### CORS 配置

```env
# 允许的跨域源（多个用逗号分隔）
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 📦 部署步骤

### 开发环境部署

1. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **初始化数据库**（如果需要）
   ```bash
   # 数据库迁移在容器启动时自动执行
   # 如需手动执行：
   docker-compose exec web python manage.py migrate
   ```

4. **创建超级用户**（可选）
   ```bash
   # 默认已创建 admin/admin123
   # 如需创建其他用户：
   docker-compose exec web python manage.py createsuperuser
   ```

### 生产环境部署

1. **配置环境变量**
   ```bash
   cp .env.example .env
   nano .env
   ```
   
   确保配置：
   - `DEBUG=False`
   - 强密码
   - 正确的 `ALLOWED_HOSTS`
   - 正确的 `CORS_ALLOWED_ORIGINS`

2. **配置域名和 HTTPS**
   
   修改 `nginx/conf.d/digitalpet.conf`：
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       # ... 其他配置
   }
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

4. **配置 SSL 证书**（推荐使用 Let's Encrypt）
   
   安装 Certbot：
   ```bash
   # 使用 Certbot 获取证书
   docker run -it --rm \
     -v /etc/letsencrypt:/etc/letsencrypt \
     -v /var/lib/letsencrypt:/var/lib/letsencrypt \
     -p 80:80 \
     certbot/certbot certonly --standalone -d yourdomain.com
   ```

## 🎯 常用命令

### 容器管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec web bash
```

### Django 管理

```bash
# 数据库迁移
docker-compose exec web python manage.py migrate

# 创建超级用户
docker-compose exec web python manage.py createsuperuser

# 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput

# 进入 Django shell
docker-compose exec web python manage.py shell
```

### 数据库管理

```bash
# 进入 PostgreSQL 命令行
docker-compose exec db psql -U digitalpet -d digitalpet

# 备份数据库
docker-compose exec db pg_dump -U digitalpet digitalpet > backup.sql

# 恢复数据库
docker-compose exec -T db psql -U digitalpet digitalpet < backup.sql

# 查看数据库日志
docker-compose logs db
```

### 清理和重建

```bash
# 停止并删除容器（保留数据卷）
docker-compose down

# 停止并删除容器和数据卷（谨慎使用）
docker-compose down -v

# 重新构建镜像
docker-compose build --no-cache

# 重新构建并启动
docker-compose up -d --build
```

## 🔍 故障排查

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs web
docker-compose logs db
docker-compose logs nginx

# 实时跟踪日志
docker-compose logs -f web
```

### 常见问题

#### 1. 容器启动失败

**问题**: Web 容器无法启动
```bash
# 检查日志
docker-compose logs web

# 检查端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Linux/Mac
```

#### 2. 数据库连接失败

**问题**: Django 无法连接到 PostgreSQL
```bash
# 检查数据库容器状态
docker-compose ps db

# 检查数据库日志
docker-compose logs db

# 测试数据库连接
docker-compose exec web python manage.py dbshell
```

#### 3. 静态文件无法访问

**问题**: 静态文件返回 404
```bash
# 重新收集静态文件
docker-compose exec web python manage.py collectstatic --noinput

# 检查 nginx 配置
docker-compose exec nginx nginx -t

# 重启 nginx
docker-compose restart nginx
```

#### 4. 权限问题

**问题**: 文件权限错误
```bash
# 修复权限（Linux/Mac）
sudo chown -R $USER:$USER .
chmod -R 755 .

# Windows: 以管理员身份运行 Docker Desktop
```

#### 5. 内存不足

**问题**: 容器因内存不足而崩溃
```bash
# 检查容器资源使用
docker stats

# 调整 Docker Desktop 的内存限制
# Settings -> Resources -> Memory
```

### 性能优化

```bash
# 清理未使用的镜像和容器
docker system prune -a

# 查看磁盘使用情况
docker system df

# 限制日志大小（在 docker-compose.yml 中添加）
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🏭 生产环境建议

### 安全建议

1. **使用强密码**
   - 数据库密码至少 16 位
   - Django SECRET_KEY 使用随机生成的字符串
   - 定期更换密码

2. **限制访问**
   - 配置防火墙规则
   - 使用 `ALLOWED_HOSTS` 限制访问域名
   - 配置 `CORS_ALLOWED_ORIGINS` 限制跨域请求

3. **启用 HTTPS**
   - 使用 SSL/TLS 证书
   - 配置 HSTS（HTTP Strict Transport Security）
   - 重定向 HTTP 到 HTTPS

4. **定期备份**
   ```bash
   # 创建备份脚本
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   docker-compose exec -T db pg_dump -U digitalpet digitalpet > backup_$DATE.sql
   
   # 定期执行备份（使用 cron）
   0 2 * * * /path/to/backup.sh
   ```

### 监控和日志

1. **配置日志轮转**
   ```yaml
   # 在 docker-compose.yml 中添加
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "5"
   ```

2. **监控工具**
   - 使用 Prometheus + Grafana 监控容器
   - 配置健康检查
   - 设置告警规则

### 扩展性

1. **水平扩展**
   ```bash
   # 增加 Web 服务实例
   docker-compose up -d --scale web=3
   ```

2. **负载均衡**
   - 配置 Nginx 负载均衡
   - 使用外部负载均衡器（如 HAProxy、AWS ELB）

3. **缓存优化**
   - 配置 Redis 缓存
   - 启用数据库查询缓存
   - 配置 CDN 服务静态文件

### 更新和维护

```bash
# 更新代码
git pull

# 重新构建并重启
docker-compose up -d --build

# 执行数据库迁移
docker-compose exec web python manage.py migrate

# 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput
```

## 📝 文件说明

- `Dockerfile`: Django 应用容器镜像定义
- `docker-compose.yml`: 服务编排配置
- `.dockerignore`: Docker 构建时忽略的文件
- `entrypoint.sh`: 容器启动脚本
- `nginx/nginx.conf`: Nginx 主配置文件
- `nginx/conf.d/digitalpet.conf`: 站点配置文件
- `.env.example`: 环境变量示例

## 🆘 获取帮助

如遇问题，请：
1. 查看日志：`docker-compose logs -f`
2. 检查容器状态：`docker-compose ps`
3. 查看本文档的故障排查部分
4. 提交 Issue 到项目仓库

## 📚 相关文档

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Django 部署文档](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Nginx 配置指南](https://nginx.org/en/docs/)
