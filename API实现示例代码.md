# 用户模块API实现示例代码

## 📝 完整实现示例

以下是基于Django REST Framework的完整实现代码，包含详细注释。

### 1. 数据模型扩展

```python
# accounts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from datetime import timedelta
from django.utils import timezone


class UserProfile(models.Model):
    """
    用户扩展信息模型
    
    Django的User模型只包含基本字段，这个模型用于存储额外信息。
    使用一对一关系（OneToOneField）与User关联。
    """
    
    # 关联到Django内置的User模型
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile',  # 反向查询名称：user.profile
        verbose_name='用户'
    )
    
    # 联系方式
    phone = models.CharField(
        max_length=11, 
        blank=True, 
        null=True,
        verbose_name='手机号',
        help_text='11位手机号码'
    )
    
    # 个人信息
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',  # 按年月分目录存储
        blank=True, 
        null=True,
        verbose_name='头像'
    )
    
    bio = models.TextField(
        blank=True, 
        verbose_name='个人简介',
        max_length=500
    )
    
    birth_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name='出生日期'
    )
    
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    ]
    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES, 
        blank=True,
        verbose_name='性别'
    )
    
    # 验证状态
    email_verified = models.BooleanField(
        default=False,
        verbose_name='邮箱已验证'
    )
    
    phone_verified = models.BooleanField(
        default=False,
        verbose_name='手机已验证'
    )
    
    # 统计信息
    login_count = models.IntegerField(
        default=0,
        verbose_name='登录次数'
    )
    
    last_login_ip = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name='最后登录IP'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return f"{self.user.username}的资料"
    
    def increment_login_count(self):
        """增加登录计数"""
        self.login_count += 1
        self.save(update_fields=['login_count'])


# Signal：自动创建UserProfile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    信号处理器：当创建User时自动创建对应的UserProfile
    
    这样就不需要在注册时手动创建UserProfile了。
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """保存User时也保存UserProfile"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class EmailVerification(models.Model):
    """
    邮箱验证令牌模型
    
    用于存储邮箱验证的临时令牌。
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='用户'
    )
    
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='验证令牌'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    expires_at = models.DateTimeField(
        verbose_name='过期时间'
    )
    
    is_used = models.BooleanField(
        default=False,
        verbose_name='已使用'
    )
    
    class Meta:
        verbose_name = '邮箱验证'
        verbose_name_plural = '邮箱验证'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的邮箱验证"
    
    def save(self, *args, **kwargs):
        """保存时自动设置过期时间（24小时后）"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """检查令牌是否有效"""
        return not self.is_used and timezone.now() < self.expires_at
```

### 2. 序列化器

```python
# accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, EmailVerification


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户资料序列化器
    
    用于序列化UserProfile模型数据。
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'avatar', 'bio', 'birth_date', 'gender',
            'email_verified', 'phone_verified', 
            'login_count', 'created_at'
        ]
        read_only_fields = ['email_verified', 'phone_verified', 'login_count', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    
    用于序列化User模型数据，包含关联的profile信息。
    """
    
    # 嵌套序列化UserProfile
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class RegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    
    处理用户注册逻辑，包括密码验证和确认。
    """
    
    # 额外字段：确认密码
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='确认密码'
    )
    
    # 额外字段：手机号（可选）
    phone = serializers.CharField(
        required=False,
        max_length=11,
        label='手机号'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
            'email': {'required': True}
        }
    
    def validate_email(self, value):
        """验证邮箱是否已被注册"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已被注册')
        return value
    
    def validate_phone(self, value):
        """验证手机号格式"""
        if value and len(value) != 11:
            raise serializers.ValidationError('手机号必须是11位数字')
        if value and UserProfile.objects.filter(phone=value).exists():
            raise serializers.ValidationError('该手机号已被注册')
        return value
    
    def validate_password(self, value):
        """验证密码强度"""
        validate_password(value)  # 使用Django内置的密码验证器
        return value
    
    def validate(self, data):
        """验证两次密码是否一致"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '两次输入的密码不一致'
            })
        return data
    
    def create(self, validated_data):
        """创建用户"""
        # 移除不属于User模型的字段
        validated_data.pop('password_confirm')
        phone = validated_data.pop('phone', None)
        
        # 创建用户（密码会自动加密）
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # 更新UserProfile（由signal自动创建）
        if phone:
            user.profile.phone = phone
            user.profile.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    登录序列化器
    
    接受用户名（或邮箱）和密码。
    """
    
    username = serializers.CharField(
        required=True,
        label='用户名或邮箱'
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
        """验证原密码是否正确"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value
    
    def validate_new_password(self, value):
        """验证新密码强度"""
        validate_password(value)
        return value
    
    def validate(self, data):
        """验证两次新密码是否一致"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': '两次输入的新密码不一致'
            })
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    更新用户信息序列化器
    """
    
    phone = serializers.CharField(
        source='profile.phone',
        required=False,
        max_length=11
    )
    
    bio = serializers.CharField(
        source='profile.bio',
        required=False,
        max_length=500
    )
    
    birth_date = serializers.DateField(
        source='profile.birth_date',
        required=False
    )
    
    gender = serializers.ChoiceField(
        source='profile.gender',
        choices=['M', 'F', 'O'],
        required=False
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'bio', 'birth_date', 'gender']
    
    def update(self, instance, validated_data):
        """更新用户和资料"""
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
```

### 3. API视图

```python
# accounts/api_views.py

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer, UserUpdateSerializer
)


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AuthViewSet(viewsets.GenericViewSet):
    """
    认证相关API视图集
    
    这个ViewSet不绑定到任何模型（GenericViewSet），
    而是提供一系列自定义的action。
    """
    
    permission_classes = [permissions.AllowAny]  # 默认允许所有人访问
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        用户注册API
        
        POST /api/auth/register/
        
        请求体：
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "phone": "13800138000"
        }
        """
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            # 创建用户
            user = serializer.save()
            
            # 生成JWT Token
            refresh = RefreshToken.for_user(user)
            
            # 返回成功响应
            return Response({
                'status': 'success',
                'message': '注册成功',
                'data': {
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                }
            }, status=status.HTTP_201_CREATED)
        
        # 验证失败，返回错误
        return Response({
            'status': 'error',
            'message': '注册失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        用户登录API
        
        POST /api/auth/login/
        
        请求体：
        {
            "username": "testuser",
            "password": "SecurePass123!"
        }
        """
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # 支持用户名或邮箱登录
        if '@' in username:
            # 使用邮箱登录
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': '用户名或密码错误'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 验证用户名和密码
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return Response({
                'status': 'error',
                'message': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'status': 'error',
                'message': '账号已被禁用'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 更新登录信息
        user.profile.increment_login_count()
        user.profile.last_login_ip = get_client_ip(request)
        user.profile.save()
        
        # 生成Token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'success',
            'message': '登录成功',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """
        用户登出API
        
        POST /api/auth/logout/
        Authorization: Bearer <access_token>
        
        请求体：
        {
            "refresh": "<refresh_token>"
        }
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # 将token加入黑名单（需要安装djangorestframework-simplejwt[blacklist]）
            
            return Response({
                'status': 'success',
                'message': '登出成功'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理API视图集
    
    提供用户的CRUD操作。
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        根据action设置不同的权限
        
        - me相关操作：需要登录
        - list、retrieve、update、destroy：需要管理员权限
        """
        if self.action in ['me', 'update_me', 'change_password']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        获取当前用户信息
        
        GET /api/users/me/
        Authorization: Bearer <access_token>
        """
        serializer = UserSerializer(request.user)
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """
        更新当前用户信息
        
        PUT/PATCH /api/users/me/
        Authorization: Bearer <access_token>
        
        请求体：
        {
            "first_name": "张",
            "last_name": "三",
            "phone": "13800138000",
            "bio": "这是我的个人简介",
            "gender": "M"
        }
        """
        partial = request.method == 'PATCH'
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=partial
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': '更新成功',
                'data': UserSerializer(request.user).data
            })
        
        return Response({
            'status': 'error',
            'message': '更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        修改密码
        
        POST /api/users/change-password/
        Authorization: Bearer <access_token>
        
        请求体：
        {
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
            "new_password_confirm": "NewPass123!"
        }
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # 设置新密码
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            
            return Response({
                'status': 'success',
                'message': '密码修改成功'
            })
        
        return Response({
            'status': 'error',
            'message': '密码修改失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def upload_avatar(self, request):
        """
        上传头像
        
        POST /api/users/upload-avatar/
        Authorization: Bearer <access_token>
        Content-Type: multipart/form-data
        
        请求体：
        - avatar: 图片文件
        """
        if 'avatar' not in request.FILES:
            return Response({
                'status': 'error',
                'message': '请上传图片文件'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        avatar = request.FILES['avatar']
        
        # 验证文件类型
        if not avatar.content_type.startswith('image/'):
            return Response({
                'status': 'error',
                'message': '只能上传图片文件'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证文件大小（限制2MB）
        if avatar.size > 2 * 1024 * 1024:
            return Response({
                'status': 'error',
                'message': '图片大小不能超过2MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存头像
        request.user.profile.avatar = avatar
        request.user.profile.save()
        
        return Response({
            'status': 'success',
            'message': '头像上传成功',
            'data': {
                'avatar_url': request.user.profile.avatar.url
            }
        })
```

### 4. URL配置

```python
# accounts/api_urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import AuthViewSet, UserViewSet

# 创建路由器
router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    # DRF路由
    path('', include(router.urls)),
    
    # JWT Token刷新
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

```python
# mysite/urls.py (更新)

from django.contrib import admin
from django.urls import path, include
from accounts.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    
    # 传统视图路由
    path('accounts/', include('accounts.urls')),
    
    # REST API路由
    path('api/', include('accounts.api_urls')),
    
    # LLM服务
    path('llm/', include('llm_service.urls')),
]
```

### 5. settings.py配置

```python
# mysite/settings.py (添加)

# REST Framework配置
REST_FRAMEWORK = {
    # 认证方式
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # 保留Session认证用于浏览器
    ],
    
    # 默认权限
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    
    # 分页
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # 过滤
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # 异常处理
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    
    # 日期时间格式
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
}

# JWT配置
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # Access Token有效期1小时
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # Refresh Token有效期7天
    'ROTATE_REFRESH_TOKENS': True,                    # 刷新时轮换Refresh Token
    'BLACKLIST_AFTER_ROTATION': True,                 # 轮换后将旧Token加入黑名单
    'UPDATE_LAST_LOGIN': True,                        # 更新last_login字段
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# 媒体文件配置（用于存储头像）
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 📝 使用示例

### 1. 用户注册

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "phone": "13800138000"
  }'
```

### 2. 用户登录

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

### 3. 获取当前用户信息

```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer <your_access_token>"
```

### 4. 更新用户信息

```bash
curl -X PATCH http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "张",
    "last_name": "三",
    "bio": "这是我的个人简介"
  }'
```

### 5. 修改密码

```bash
curl -X POST http://localhost:8000/api/users/change-password/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "OldPass123!",
    "new_password": "NewPass123!",
    "new_password_confirm": "NewPass123!"
  }'
```

## 🧪 测试代码

```python
# accounts/tests/test_api.py

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class AuthAPITestCase(TestCase):
    """认证API测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
    
    def test_register_success(self):
        """测试注册成功"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('tokens', response.data['data'])
        
        # 验证用户已创建
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_register_duplicate_email(self):
        """测试重复邮箱注册"""
        # 先创建一个用户
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='pass'
        )
        
        # 尝试用相同邮箱注册
        data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_success(self):
        """测试登录成功"""
        # 创建测试用户
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        # 登录
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('tokens', response.data['data'])
```

---

以上是完整的REST API实现代码，包含详细注释，适合新手学习！🚀


