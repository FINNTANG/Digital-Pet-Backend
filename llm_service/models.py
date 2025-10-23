"""
LLM服务相关的数据模型

数据模型（Model）定义了数据库表的结构。
Django会根据这些模型自动创建数据库表。
"""

from django.db import models
from django.contrib.auth.models import User


class ChatMessage(models.Model):
    """
    聊天消息模型
    
    用于存储用户与AI的对话记录。
    每条消息包含：用户、角色（用户或AI）、内容、时间戳等信息。
    """
    
    # 外键关联到用户
    # on_delete=models.CASCADE 表示当用户被删除时，相关的聊天记录也会被删除
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='用户',
        help_text='消息所属的用户'
    )
    
    # 消息角色：user（用户）或 assistant（AI助手）
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', 'AI助手'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='角色',
        help_text='消息的发送者角色'
    )
    
    # 消息内容
    content = models.TextField(
        verbose_name='消息内容',
        help_text='对话的具体内容'
    )
    
    # 创建时间（自动记录）
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    # 会话ID（用于区分不同的对话会话）
    session_id = models.CharField(
        max_length=100,
        default='default',
        verbose_name='会话ID',
        help_text='用于区分不同的对话会话'
    )
    
    class Meta:
        """
        Meta类用于定义模型的元数据
        """
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['-created_at']  # 按创建时间倒序排列（最新的在前）
    
    def __str__(self):
        """
        字符串表示方法
        
        当我们打印这个对象时，会显示这个格式的字符串。
        例如：小明(用户): 你好
        """
        return f"{self.user.username}({self.get_role_display()}): {self.content[:50]}"


class LLMConfig(models.Model):
    """
    LLM配置模型
    
    存储LLM相关的配置信息，比如API密钥、模型名称等。
    这样可以在后台管理界面中方便地修改配置，而不需要改代码。
    """
    
    # 配置名称
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='配置名称',
        help_text='例如：OpenAI配置、本地模型配置'
    )
    
    # LLM提供商
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('azure', 'Azure OpenAI'),
        ('anthropic', 'Anthropic (Claude)'),
        ('local', '本地模型'),
        ('other', '其他'),
    ]
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='openai',
        verbose_name='提供商'
    )
    
    # 模型名称
    model_name = models.CharField(
        max_length=100,
        default='gpt-3.5-turbo',
        verbose_name='模型名称',
        help_text='例如：gpt-3.5-turbo, gpt-4, claude-3-sonnet'
    )
    
    # API密钥（敏感信息，实际使用时应该加密或使用环境变量）
    api_key = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='API密钥',
        help_text='LLM服务的API密钥'
    )
    
    # API基础URL
    api_base = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='API基础URL',
        help_text='可选，用于自定义API端点'
    )
    
    # 是否启用
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='只有启用的配置才会被使用'
    )
    
    # 最大token数
    max_tokens = models.IntegerField(
        default=2000,
        verbose_name='最大Token数',
        help_text='单次对话的最大token数量'
    )
    
    # 温度参数（控制输出的随机性）
    temperature = models.FloatField(
        default=0.7,
        verbose_name='温度参数',
        help_text='0-1之间，越高越随机，越低越确定'
    )
    
    # 创建时间
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    # 更新时间
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = 'LLM配置'
        verbose_name_plural = 'LLM配置'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_display()})"
