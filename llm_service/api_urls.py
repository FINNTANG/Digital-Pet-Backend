"""
LLM服务API的URL配置

这个文件定义了LLM服务REST API的URL路由。
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import LLMViewSet, LLMConfigViewSet

# 创建DRF路由器
router = DefaultRouter()

# 注册ViewSet
# basename用于生成URL名称
router.register(r'llm', LLMViewSet, basename='llm')
router.register(r'llm-configs', LLMConfigViewSet, basename='llm-config')

# URL模式
urlpatterns = [
    # DRF路由器生成的URL
    # LLM服务相关：
    # - POST   /api/llm/chat/              # 发送消息
    # - GET    /api/llm/messages/          # 获取消息历史
    # - GET    /api/llm/sessions/          # 获取会话列表
    # - DELETE /api/llm/sessions/{id}/     # 删除会话
    # - POST   /api/llm/sessions/{id}/clear/  # 清空会话
    # - GET    /api/llm/statistics/        # 聊天统计
    #
    # LLM配置管理（仅管理员）：
    # - GET    /api/llm-configs/           # 配置列表
    # - POST   /api/llm-configs/           # 创建配置
    # - GET    /api/llm-configs/{id}/      # 配置详情
    # - PUT    /api/llm-configs/{id}/      # 更新配置
    # - DELETE /api/llm-configs/{id}/      # 删除配置
    # - POST   /api/llm-configs/{id}/activate/    # 激活配置
    # - POST   /api/llm-configs/{id}/deactivate/  # 禁用配置
    path('', include(router.urls)),
]










