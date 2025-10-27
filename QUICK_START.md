# 🚀 Docker 快速启动指南

## 最简部署（3 步完成）

### 1️⃣ 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件（至少配置数据库密码）
# Windows: notepad .env
# Linux/Mac: nano .env
```

**最小配置（开发环境）：**
```env
DEBUG=True
DB_PASSWORD=your_password_here
```

**生产环境必须配置：**
```env
DEBUG=False
SECRET_KEY=<运行命令生成>
DB_PASSWORD=<强密码>
ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

生成 SECRET_KEY：
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2️⃣ 一键启动

**Windows:**
```powershell
# 方式 1: 使用部署脚本（推荐）
.\deploy.ps1

# 方式 2: 手动启动
docker compose up -d
```

**Linux/Mac:**
```bash
# 方式 1: 使用部署脚本（推荐）
chmod +x deploy.sh
./deploy.sh

# 方式 2: 手动启动
docker-compose up -d
```

### 3️⃣ 访问应用

等待约 30 秒后访问：

- 🌐 **API 服务**: http://localhost
- 📚 **API 文档**: http://localhost/swagger/
- ⚙️ **管理后台**: http://localhost/admin/

**默认管理员账号：**
- 用户名: `admin`
- 密码: `admin123`

⚠️ **生产环境请立即修改默认密码！**

---

## 🔧 常用命令速查

### 容器管理

```bash
# 查看服务状态
docker compose ps

# 查看实时日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f web

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 停止并删除数据（危险）
docker compose down -v
```

### Django 管理

```bash
# 进入容器
docker compose exec web bash

# 数据库迁移
docker compose exec web python manage.py migrate

# 创建超级用户
docker compose exec web python manage.py createsuperuser

# 进入 Django Shell
docker compose exec web python manage.py shell
```

### 数据库管理

```bash
# 进入数据库
docker compose exec db psql -U digitalpet -d digitalpet

# 备份数据库
docker compose exec db pg_dump -U digitalpet digitalpet > backup.sql

# 恢复数据库
docker compose exec -T db psql -U digitalpet digitalpet < backup.sql
```

---

## 🛠️ 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker compose logs

# 检查端口占用
# Windows:
netstat -ano | findstr :80
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :80
lsof -i :8000
```

### 数据库连接失败

```bash
# 检查数据库状态
docker compose ps db

# 查看数据库日志
docker compose logs db

# 重启数据库
docker compose restart db
```

### 静态文件无法访问

```bash
# 重新收集静态文件
docker compose exec web python manage.py collectstatic --noinput

# 重启 Nginx
docker compose restart nginx
```

### 完全重置

```bash
# 停止并删除所有容器和数据卷
docker compose down -v

# 重新构建并启动
docker compose up -d --build
```

---

## 📊 服务架构

```
┌─────────────────────────────────────────┐
│           Nginx (Port 80)               │
│  - 反向代理                              │
│  - 静态文件服务                          │
│  - 负载均衡                              │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│      Django App (Gunicorn:8000)         │
│  - REST API                              │
│  - LLM 服务                              │
│  - 用户管理                              │
└──────┬──────────────────────┬───────────┘
       │                      │
       ▼                      ▼
┌─────────────┐        ┌─────────────┐
│ PostgreSQL  │        │   Redis     │
│  (Port 5432)│        │ (Port 6379) │
│  - 主数据库  │        │  - 缓存     │
└─────────────┘        └─────────────┘
```

---

## 🔐 安全检查清单

部署到生产环境前，请确保：

- [ ] `DEBUG=False`
- [ ] 修改了 `SECRET_KEY`
- [ ] 修改了数据库密码
- [ ] 配置了 `ALLOWED_HOSTS`
- [ ] 配置了 `CORS_ALLOWED_ORIGINS`
- [ ] 修改了默认管理员密码
- [ ] 启用了 HTTPS
- [ ] 配置了防火墙
- [ ] 设置了定期备份

---

## 📖 更多文档

- 📘 [完整部署文档](DOCKER_DEPLOYMENT.md) - 详细的部署指南
- 📗 [项目 README](README.md) - 项目说明文档
- 📙 [API 文档](http://localhost/swagger/) - 在线 API 文档

---

## 💡 提示

1. **首次启动较慢**：需要下载镜像和构建容器，约需 5-10 分钟
2. **数据持久化**：数据存储在 Docker 数据卷中，容器重启不会丢失
3. **日志位置**：应用日志存储在 `./logs` 目录
4. **端口冲突**：如果 80 端口被占用，在 `.env` 中设置 `NGINX_PORT=8080`

---

## 🆘 需要帮助？

- 查看 [完整部署文档](DOCKER_DEPLOYMENT.md)
- 查看日志：`docker compose logs -f`
- 检查容器状态：`docker compose ps`
- 提交 Issue 到项目仓库
