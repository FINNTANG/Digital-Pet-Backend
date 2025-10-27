# 使用官方 Python 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
# libgomp1: 用于 DeepFace 的多线程支持
# libglib2.0-0, libsm6, libxext6, libxrender-dev: 用于 OpenCV（DeepFace 依赖）
# postgresql-client: 用于数据库连接
# netcat-openbsd: 用于等待数据库就绪
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /app/staticfiles /app/media /app/logs

# 设置启动脚本权限
RUN chmod +x /app/entrypoint.sh

# 收集静态文件（在运行时执行，这里只是创建目录）
# RUN python manage.py collectstatic --noinput

# 创建非特权用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 切换到非特权用户
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令（使用 Gunicorn）
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "mysite.wsgi:application"]
