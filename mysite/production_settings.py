"""
Django Production Settings for mysite project.

This settings file is optimized for Docker deployment and production use.
All sensitive configurations are loaded from environment variables.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ========== 安全配置 ==========

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-^&_ejlcps++eu*$-&j_gw84c2&s_g&672$fpj00i3s3ja$u$#k')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

# 允许的主机（从环境变量读取，多个主机用逗号分隔）
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# 安全设置
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # REST API相关
    'rest_framework',  # Django REST Framework
    'rest_framework_simplejwt',  # JWT认证
    'django_filters',  # 过滤功能
    'drf_yasg',  # API文档生成
    'corsheaders',  # CORS跨域支持
    
    # 自定义应用
    'accounts',  # 用户管理应用
    'llm_service',  # LLM服务应用
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS中间件，必须放在CommonMiddleware之前
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'digitalpet'),
        'USER': os.environ.get('DB_USER', 'digitalpet'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'changeme123'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # 持久化数据库连接
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'  # 设置为中文

TIME_ZONE = 'Asia/Shanghai'  # 设置为中国时区

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 登录相关设置
LOGIN_URL = 'login'  # 未登录用户访问需要登录的页面时，跳转到登录页
LOGIN_REDIRECT_URL = 'home'  # 登录成功后跳转到首页
LOGOUT_REDIRECT_URL = 'login'  # 登出后跳转到登录页

# 媒体文件配置（用于存储用户上传的文件，如头像）
import os
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# REST Framework配置
REST_FRAMEWORK = {
    # 认证方式
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT Token认证
        'rest_framework.authentication.SessionAuthentication',  # Session认证（用于浏览器）
    ],
    
    # 默认权限
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',  # 登录后可写，未登录可读
    ],
    
    # 分页配置
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,  # 每页显示20条数据
    
    # 过滤、搜索、排序
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',  # 过滤
        'rest_framework.filters.SearchFilter',  # 搜索
        'rest_framework.filters.OrderingFilter',  # 排序
    ],
    
    # 日期时间格式
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    
    # 异常处理
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# JWT配置
from datetime import timedelta

SIMPLE_JWT = {
    # Token有效期
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # Access Token有效期1小时
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Refresh Token有效期7天
    
    # Token轮换
    'ROTATE_REFRESH_TOKENS': True,  # 刷新时轮换Refresh Token
    'BLACKLIST_AFTER_ROTATION': True,  # 轮换后将旧Token加入黑名单
    
    # 更新最后登录时间
    'UPDATE_LAST_LOGIN': True,
    
    # 算法和密钥
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    
    # 请求头配置
    'AUTH_HEADER_TYPES': ('Bearer',),  # 使用Bearer token
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    # 用户字段
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    # Token类型
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Swagger文档配置
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'put', 'delete', 'patch'],
}

# ========== CORS跨域配置 ==========

# CORS 配置：从环境变量读取
cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if cors_origins:
    CORS_ALLOWED_ORIGINS = cors_origins.split(',')
    CORS_ALLOW_ALL_ORIGINS = False
else:
    # 如果未配置，允许所有来源（仅开发环境）
    CORS_ALLOW_ALL_ORIGINS = DEBUG

# 允许携带Cookie
CORS_ALLOW_CREDENTIALS = True

# 允许的HTTP方法
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# 允许的请求头
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
