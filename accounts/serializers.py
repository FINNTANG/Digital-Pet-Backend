"""
用户账户相关的序列化器

序列化器（Serializer）的作用：
1. 将Python对象（如User、UserProfile）转换为JSON格式（序列化）
2. 将JSON数据转换为Python对象（反序列化）
3. 验证输入数据的有效性

序列化器相当于API的"表单"，定义了API接口接受和返回的数据格式。
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, EmailVerification


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户资料序列化器
    
    用于序列化UserProfile模型的数据。
    嵌套在UserSerializer中使用，展示用户的扩展信息。
    """
    
    # 只读字段：年龄（从@property计算得出）
    age = serializers.ReadOnlyField()
    
    # 头像URL（自定义方法字段）
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'avatar', 'avatar_url', 'bio', 'birth_date', 'gender',
            'email_verified', 'phone_verified',
            'login_count', 'last_login_ip',
            'created_at', 'updated_at', 'age'
        ]
        read_only_fields = [
            'email_verified', 'phone_verified',  # 验证状态不能直接修改
            'login_count', 'last_login_ip',  # 统计信息只读
            'created_at', 'updated_at', 'age', 'avatar_url'
        ]
    
    def get_avatar_url(self, obj):
        """获取头像完整URL"""
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        elif obj.avatar:
            return obj.avatar.url
        return None


class UserSerializer(serializers.ModelSerializer):
    """
    用户信息序列化器
    
    用于展示User模型的基本信息和关联的Profile信息。
    主要用于GET请求，返回用户完整信息。
    """
    
    # 嵌套序列化UserProfile
    profile = UserProfileSerializer(read_only=True)
    
    # 全名（拼接first_name和last_name）
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name', 'full_name',
            'is_active', 'is_staff',
            'date_joined', 'last_login',
            'profile'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login',
            'is_staff'  # 普通用户不能修改staff状态
        ]
    
    def get_full_name(self, obj):
        """获取全名"""
        if obj.first_name or obj.last_name:
            return f"{obj.last_name}{obj.first_name}".strip()
        return obj.username


class RegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    
    处理用户注册逻辑，包括：
    - 验证用户名和邮箱是否重复
    - 验证密码强度
    - 确认两次密码输入一致
    - 创建用户和对应的Profile
    """
    
    # 确认密码字段（不存储到数据库）
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='确认密码'
    )
    
    # 手机号（可选）
    phone = serializers.CharField(
        required=False,
        max_length=11,
        label='手机号',
        help_text='11位手机号码（可选）'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone']
        extra_kwargs = {
            'password': {
                'write_only': True,  # 密码字段只写不读
                'style': {'input_type': 'password'}
            },
            'email': {
                'required': True  # 邮箱必填
            }
        }
    
    def validate_username(self, value):
        """
        验证用户名
        
        检查：
        1. 用户名长度
        2. 用户名是否已存在
        """
        if len(value) < 3:
            raise serializers.ValidationError('用户名至少需要3个字符')
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('该用户名已被注册')
        
        return value
    
    def validate_email(self, value):
        """
        验证邮箱
        
        检查邮箱是否已被注册
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已被注册')
        
        return value
    
    def validate_phone(self, value):
        """
        验证手机号
        
        检查：
        1. 手机号格式（11位数字）
        2. 手机号是否已被注册
        """
        if not value:
            return value
        
        # 检查长度
        if len(value) != 11:
            raise serializers.ValidationError('手机号必须是11位数字')
        
        # 检查是否全是数字
        if not value.isdigit():
            raise serializers.ValidationError('手机号只能包含数字')
        
        # 检查是否已被注册
        if UserProfile.objects.filter(phone=value).exists():
            raise serializers.ValidationError('该手机号已被注册')
        
        return value
    
    def validate_password(self, value):
        """
        验证密码强度
        
        使用Django内置的密码验证器，检查：
        - 密码长度
        - 密码复杂度
        - 常见密码检查
        - 与用户信息相似度
        """
        validate_password(value)
        return value
    
    def validate(self, data):
        """
        整体验证
        
        验证两次密码输入是否一致
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '两次输入的密码不一致'
            })
        
        return data
    
    def create(self, validated_data):
        """
        创建用户
        
        步骤：
        1. 移除不属于User模型的字段
        2. 创建User对象（密码会自动加密）
        3. 更新UserProfile信息（由Signal自动创建）
        """
        # 移除不属于User模型的字段
        validated_data.pop('password_confirm')
        phone = validated_data.pop('phone', None)
        
        # 创建用户（使用create_user确保密码正确加密）
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # 更新UserProfile（由Signal自动创建）
        if phone:
            user.profile.phone = phone
            user.profile.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    登录序列化器
    
    接受用户名（或邮箱）和密码，用于用户登录验证。
    不绑定到模型（使用Serializer而非ModelSerializer）。
    """
    
    username = serializers.CharField(
        required=True,
        label='用户名或邮箱',
        help_text='可以使用用户名或邮箱登录'
    )
    
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label='密码'
    )


class ChangePasswordSerializer(serializers.Serializer):
    """
    修改密码序列化器
    
    用于已登录用户修改自己的密码。
    需要提供原密码进行验证。
    """
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label='原密码'
    )
    
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label='新密码'
    )
    
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label='确认新密码'
    )
    
    def validate_old_password(self, value):
        """
        验证原密码是否正确
        
        从context中获取当前用户，验证原密码。
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value
    
    def validate_new_password(self, value):
        """验证新密码强度"""
        validate_password(value)
        return value
    
    def validate(self, data):
        """验证两次新密码输入是否一致"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': '两次输入的新密码不一致'
            })
        
        # 检查新密码是否与旧密码相同
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({
                'new_password': '新密码不能与原密码相同'
            })
        
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    更新用户信息序列化器
    
    用于更新User和UserProfile的信息。
    支持部分更新（PATCH）。
    """
    
    # 嵌套的Profile字段
    phone = serializers.CharField(
        source='profile.phone',
        required=False,
        max_length=11,
        allow_blank=True
    )
    
    bio = serializers.CharField(
        source='profile.bio',
        required=False,
        max_length=500,
        allow_blank=True
    )
    
    birth_date = serializers.DateField(
        source='profile.birth_date',
        required=False,
        allow_null=True
    )
    
    gender = serializers.ChoiceField(
        source='profile.gender',
        choices=UserProfile.GENDER_CHOICES,
        required=False,
        allow_blank=True
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name',
            'phone', 'bio', 'birth_date', 'gender'
        ]
    
    def validate_phone(self, value):
        """验证手机号"""
        if not value:
            return value
        
        if len(value) != 11 or not value.isdigit():
            raise serializers.ValidationError('手机号必须是11位数字')
        
        # 检查手机号是否被其他用户使用
        user = self.context['request'].user
        if UserProfile.objects.filter(phone=value).exclude(user=user).exists():
            raise serializers.ValidationError('该手机号已被其他用户使用')
        
        return value
    
    def update(self, instance, validated_data):
        """
        更新用户和资料
        
        分别处理User字段和Profile字段的更新。
        """
        # 分离profile数据
        profile_data = validated_data.pop('profile', {})
        
        # 更新User字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新UserProfile字段
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class EmailVerificationSerializer(serializers.ModelSerializer):
    """
    邮箱验证序列化器
    
    用于查看邮箱验证记录。
    """
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailVerification
        fields = [
            'id', 'user', 'user_email', 'token',
            'created_at', 'expires_at', 'is_used', 'is_expired'
        ]
        read_only_fields = ['id', 'user', 'token', 'created_at']
    
    def get_is_expired(self, obj):
        """检查是否已过期"""
        return not obj.is_valid()


