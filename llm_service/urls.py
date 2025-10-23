"""
LLM服务应用的URL配置

定义LLM服务相关的URL路由。
"""

from django.urls import path
from . import views

urlpatterns = [
    # 聊天界面 - /llm/chat/
    path('chat/', views.chat_view, name='llm_chat'),
    
    # 发送消息API - /llm/send/
    path('send/', views.send_message, name='send_message'),
    
    # 聊天历史 - /llm/history/
    path('history/', views.chat_history_view, name='chat_history'),
    
    # 新建会话 - /llm/new-session/
    path('new-session/', views.new_session, name='new_session'),
    
    # 清空历史 - /llm/clear/
    path('clear/', views.clear_history, name='clear_history'),
]


