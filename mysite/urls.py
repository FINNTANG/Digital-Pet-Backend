"""
URL configuration for mysite project.

URL配置说明：
- path('路径', 视图函数, name='URL名称')
- include() 函数用于包含其他应用的URL配置
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home_view

# API文档相关
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger API文档配置
schema_view = get_schema_view(
    openapi.Info(
        title="Django用户管理与LLM服务 API",
        default_version='v1',
        description="""
        ## 📖 API文档
        
        这是一个完整的用户管理和LLM服务API。
        
        ### 功能模块
        - **认证模块**：用户注册、登录、登出
        - **用户管理**：个人信息管理、密码修改、头像上传
        - **LLM服务**：AI聊天、历史记录
        
        ### 认证方式
        使用JWT（JSON Web Token）认证。
        
        登录后获得access_token和refresh_token：
        - access_token有效期：1小时
        - refresh_token有效期：7天
        
        在需要认证的接口中，添加请求头：
        ```
        Authorization: Bearer <access_token>
        ```
        
        ### 使用流程
        1. 注册账号：POST /api/auth/register/
        2. 登录获取Token：POST /api/auth/login/
        3. 使用Token访问其他API
        4. Token过期时刷新：POST /api/token/refresh/
        """,
        terms_of_service="",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # ========== 管理后台 ==========
    path('admin/', admin.site.urls),
    
    # ========== 网页界面 ==========
    # 首页
    path('', home_view, name='home'),
    
    # 用户管理（传统视图）
    path('accounts/', include('accounts.urls')),
    
    # LLM服务
    path('llm/', include('llm_service.urls')),
    
    # ========== REST API ==========
    # 用户管理API
    path('api/', include('accounts.api_urls')),
    
    # LLM服务API
    path('api/', include('llm_service.api_urls')),
    
    # ========== API文档 ==========
    # Swagger UI（推荐）
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
    
    # ReDoc UI（另一种风格的API文档）
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='api-redoc'),
    
    # JSON格式的API Schema
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='api-schema'),
]

# 开发环境下提供媒体文件访问
# 生产环境应该使用Nginx等Web服务器处理
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
