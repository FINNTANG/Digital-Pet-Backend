"""
用户账户应用的URL配置

URL模式决定了用户访问不同网址时，应该调用哪个视图函数。
"""

from django.urls import path
from . import views

# URL模式列表
urlpatterns = [
    # 用户注册 - 访问 /accounts/register/ 时调用 register_view
    path('register/', views.register_view, name='register'),
    
    # 用户登录 - 访问 /accounts/login/ 时调用 login_view
    path('login/', views.login_view, name='login'),
    
    # 用户登出 - 访问 /accounts/logout/ 时调用 logout_view
    path('logout/', views.logout_view, name='logout'),
    
    # 个人中心 - 访问 /accounts/profile/ 时调用 profile_view
    path('profile/', views.profile_view, name='profile'),
]


