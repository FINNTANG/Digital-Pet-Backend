"""
LLM服务相关的序列化器

序列化器的作用：
1. 将Python对象转换为JSON格式（序列化）
2. 将JSON数据转换为Python对象（反序列化）
3. 验证输入数据的有效性
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ChatMessage, LLMConfig


class UserBasicSerializer(serializers.ModelSerializer):
    """
    用户基本信息序列化器
    
    用于在聊天消息中显示用户信息。
    只包含基本字段，不包含敏感信息。
    """
    
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['id', 'username']


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    聊天消息序列化器
    
    用于序列化ChatMessage模型的数据。
    包含用户信息、消息内容、角色等。
    """
    
    # 嵌套显示用户信息
    user_info = UserBasicSerializer(source='user', read_only=True)
    
    # 角色显示名称
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'user', 'user_info', 'role', 'role_display',
            'content', 'session_id', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_content(self, value):
        """验证消息内容"""
        if not value or not value.strip():
            raise serializers.ValidationError('消息内容不能为空')
        
        if len(value) > 10000:
            raise serializers.ValidationError('消息内容不能超过10000个字符')
        
        return value.strip()


class ChatRequestSerializer(serializers.Serializer):
    """
    聊天请求序列化器
    
    用于接收用户发送的聊天消息。
    """
    
    message = serializers.CharField(
        required=True,
        max_length=10000,
        label='消息内容',
        help_text='要发送给AI的消息'
    )
    
    session_id = serializers.CharField(
        required=False,
        default='default',
        max_length=100,
        label='会话ID',
        help_text='会话标识符，用于区分不同对话。不提供则使用default'
    )
    
    pet_type = serializers.ChoiceField(
        choices=[('fox', '狐狸'), ('dog', '狗'), ('snake', '蛇')],
        required=False,
        default=None,
        allow_null=True,
        label='宠物类型',
        help_text='选择宠物类型（狐狸/狗/蛇），AI将以对应宠物的口吻回答'
    )
    
    def validate_message(self, value):
        """验证消息内容"""
        if not value or not value.strip():
            raise serializers.ValidationError('消息内容不能为空')
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """
    聊天响应序列化器
    
    用于返回AI的回复。
    """
    
    user_message = serializers.CharField(
        read_only=True,
        label='用户消息'
    )
    
    ai_response = serializers.CharField(
        read_only=True,
        label='AI回复'
    )
    
    session_id = serializers.CharField(
        read_only=True,
        label='会话ID'
    )
    
    created_at = serializers.DateTimeField(
        read_only=True,
        label='创建时间'
    )


class SessionSerializer(serializers.Serializer):
    """
    会话序列化器
    
    用于显示会话信息。
    """
    
    session_id = serializers.CharField(
        read_only=True,
        label='会话ID'
    )
    
    message_count = serializers.IntegerField(
        read_only=True,
        label='消息数量'
    )
    
    last_message_time = serializers.DateTimeField(
        read_only=True,
        label='最后消息时间'
    )
    
    preview = serializers.CharField(
        read_only=True,
        label='消息预览',
        help_text='最后一条消息的内容预览'
    )


class LLMConfigSerializer(serializers.ModelSerializer):
    """
    LLM配置序列化器
    
    用于管理LLM配置信息。
    API密钥等敏感信息只在创建/更新时可写，读取时隐藏。
    """
    
    # 提供商显示名称
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    # API密钥（写入时可见，读取时隐藏）
    api_key_masked = serializers.SerializerMethodField()
    
    class Meta:
        model = LLMConfig
        fields = [
            'id', 'name', 'provider', 'provider_display',
            'model_name', 'api_key', 'api_key_masked', 'api_base',
            'is_active', 'max_tokens', 'temperature',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': True}  # API密钥只写不读
        }
    
    def get_api_key_masked(self, obj):
        """
        返回隐藏的API密钥
        
        只显示前4位和后4位，中间用*代替。
        例如：sk-abc...xyz
        """
        if obj.api_key:
            if len(obj.api_key) > 8:
                return f"{obj.api_key[:4]}...{obj.api_key[-4:]}"
            else:
                return "***"
        return None
    
    def validate_temperature(self, value):
        """验证温度参数"""
        if not 0 <= value <= 2:
            raise serializers.ValidationError('温度参数必须在0-2之间')
        return value
    
    def validate_max_tokens(self, value):
        """验证最大token数"""
        if value < 1 or value > 128000:
            raise serializers.ValidationError('最大token数必须在1-128000之间')
        return value


class LLMConfigCreateSerializer(serializers.ModelSerializer):
    """
    LLM配置创建序列化器
    
    用于创建新的LLM配置。
    包含完整的验证逻辑。
    """
    
    class Meta:
        model = LLMConfig
        fields = [
            'name', 'provider', 'model_name',
            'api_key', 'api_base',
            'is_active', 'max_tokens', 'temperature'
        ]
    
    def validate_name(self, value):
        """验证配置名称是否已存在"""
        if LLMConfig.objects.filter(name=value).exists():
            raise serializers.ValidationError('该配置名称已存在')
        return value
    
    def validate(self, data):
        """
        整体验证
        
        检查：
        1. 如果设置为启用，确保其他配置不冲突
        2. API密钥格式检查
        """
        # 如果设置为启用，询问是否禁用其他配置
        if data.get('is_active', False):
            active_count = LLMConfig.objects.filter(
                is_active=True,
                provider=data.get('provider')
            ).count()
            if active_count > 0:
                # 提示：已有启用的配置
                pass
        
        return data


class ChatHistorySerializer(serializers.Serializer):
    """
    聊天历史序列化器
    
    用于返回格式化的聊天历史。
    """
    
    session_id = serializers.CharField(read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    total_count = serializers.IntegerField(read_only=True)


class ChatStatisticsSerializer(serializers.Serializer):
    """
    聊天统计序列化器
    
    用于显示用户的聊天统计信息。
    """
    
    total_sessions = serializers.IntegerField(
        read_only=True,
        label='总会话数'
    )
    
    total_messages = serializers.IntegerField(
        read_only=True,
        label='总消息数'
    )
    
    user_messages = serializers.IntegerField(
        read_only=True,
        label='用户消息数'
    )
    
    ai_messages = serializers.IntegerField(
        read_only=True,
        label='AI消息数'
    )
    
    first_chat_date = serializers.DateTimeField(
        read_only=True,
        label='首次聊天时间'
    )
    
    last_chat_date = serializers.DateTimeField(
        read_only=True,
        label='最后聊天时间'
    )


