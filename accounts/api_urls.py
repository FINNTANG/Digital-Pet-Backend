"""
用户账户API的URL配置

这个文件定义了REST API的URL路由。
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import AuthViewSet, UserViewSet

# 创建DRF路由器
# 路由器会自动生成标准的RESTful URL
router = DefaultRouter()

# 注册ViewSet
# basename用于生成URL名称：auth-register, auth-login等
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='users')

# URL模式
urlpatterns = [
    # DRF路由器生成的URL
    # 包括：
    # - POST   /api/auth/register/
    # - POST   /api/auth/login/
    # - POST   /api/auth/logout/
    # - GET    /api/users/
    # - GET    /api/users/{id}/
    # - GET    /api/users/me/
    # - PUT    /api/users/me/
    # - PATCH  /api/users/me/
    # - POST   /api/users/change-password/
    # - POST   /api/users/upload-avatar/
    path('', include(router.urls)),
    
    # JWT Token刷新
    # POST /api/token/refresh/
    # {
    #     "refresh": "<refresh_token>"
    # }
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]










