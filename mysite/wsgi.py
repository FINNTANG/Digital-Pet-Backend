"""
WSGI config for mysite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/

生产环境使用说明：
1. 通过环境变量DJANGO_SETTINGS_MODULE指定配置文件
2. 默认使用开发配置mysite.settings
3. 生产环境应设置为production_settings
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# 添加项目根目录到Python路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# 设置Django配置模块
# 生产环境通过环境变量DJANGO_SETTINGS_MODULE=production_settings覆盖
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# 获取WSGI应用
application = get_wsgi_application()

# 生产环境日志输出
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'production_settings':
    print("✅ WSGI应用已加载（生产环境配置）")
else:
    print("⚠️  WSGI应用已加载（开发环境配置）")
