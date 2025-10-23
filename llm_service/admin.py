"""
LLM服务的管理后台配置

这个文件定义了在Django管理后台如何显示和管理LLM相关的数据。
"""

from django.contrib import admin
from .models import ChatMessage, LLMConfig


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    聊天消息的管理界面配置
    """
    
    # 列表页显示的字段
    list_display = ['user', 'role', 'content_preview', 'session_id', 'created_at']
    
    # 可以点击进入详情的字段
    list_display_links = ['content_preview']
    
    # 侧边栏过滤器
    list_filter = ['role', 'created_at', 'user']
    
    # 搜索框可搜索的字段
    search_fields = ['content', 'user__username']
    
    # 默认排序
    ordering = ['-created_at']
    
    # 只读字段
    readonly_fields = ['created_at']
    
    # 每页显示数量
    list_per_page = 50
    
    def content_preview(self, obj):
        """
        内容预览
        
        在列表页显示消息内容的前50个字符
        """
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = '消息内容'


@admin.register(LLMConfig)
class LLMConfigAdmin(admin.ModelAdmin):
    """
    LLM配置的管理界面配置
    """
    
    # 列表页显示的字段
    list_display = ['name', 'provider', 'model_name', 'is_active', 'created_at']
    
    # 可以点击进入详情的字段
    list_display_links = ['name']
    
    # 可以直接在列表页编辑的字段
    list_editable = ['is_active']
    
    # 侧边栏过滤器
    list_filter = ['provider', 'is_active', 'created_at']
    
    # 搜索框可搜索的字段
    search_fields = ['name', 'model_name']
    
    # 默认排序
    ordering = ['-created_at']
    
    # 只读字段
    readonly_fields = ['created_at', 'updated_at']
    
    # 字段分组显示
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'provider', 'model_name', 'is_active')
        }),
        ('API配置', {
            'fields': ('api_key', 'api_base'),
            'description': '⚠️ API密钥是敏感信息，请妥善保管'
        }),
        ('模型参数', {
            'fields': ('max_tokens', 'temperature'),
            'description': '这些参数控制LLM的行为'
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # 默认折叠
        }),
    )
