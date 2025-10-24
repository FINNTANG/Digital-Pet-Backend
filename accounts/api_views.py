"""
用户账户相关的API视图

这个文件包含所有REST API的视图函数。
使用ViewSet组织代码，提供RESTful接口。
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer, UserUpdateSerializer, UserProfileSerializer
)
from .models import UserProfile


def get_client_ip(request):
    """
    获取客户端真实IP地址
    
    优先从X-Forwarded-For头获取（代理/负载均衡环境）
    否则从REMOTE_ADDR获取
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For可能包含多个IP，取第一个
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AuthViewSet(viewsets.GenericViewSet):
    """
    认证相关API视图集
    
    这个ViewSet不绑定到任何模型（使用GenericViewSet）
    通过@action装饰器定义自定义的API端点
    
    端点：
    - POST /api/auth/register/  # 用户注册
    - POST /api/auth/login/     # 用户登录
    - POST /api/auth/logout/    # 用户登出
    """
    
    permission_classes = [permissions.AllowAny]  # 允许未认证用户访问
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        用户注册API
        
        请求格式：
        POST /api/auth/register/
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "phone": "13800138000"  // 可选
        }
        
        响应格式：
        {
            "status": "success",
            "message": "注册成功",
            "data": {
                "user": { ... },  // 用户信息
                "tokens": {       // JWT令牌
                    "access": "...",
                    "refresh": "..."
                }
            }
        }
        """
        # 验证数据
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
                    'user': UserSerializer(user, context={'request': request}).data,
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
        
        支持使用用户名或邮箱登录
        
        请求格式：
        POST /api/auth/login/
        {
            "username": "testuser",  // 或使用email
            "password": "SecurePass123!"
        }
        
        响应格式：
        {
            "status": "success",
            "message": "登录成功",
            "data": {
                "user": { ... },
                "tokens": { ... }
            }
        }
        """
        # 验证数据格式
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # 支持邮箱登录
        if '@' in username:
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
                'message': '账号已被禁用，请联系管理员'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 更新登录信息
        user.profile.increment_login_count()
        user.profile.last_login_ip = get_client_ip(request)
        user.profile.save()
        
        # 生成JWT Token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'success',
            'message': '登录成功',
            'data': {
                'user': UserSerializer(user, context={'request': request}).data,
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
        
        将Refresh Token加入黑名单（需要启用token blacklist）
        
        请求格式：
        POST /api/auth/logout/
        Authorization: Bearer <access_token>
        {
            "refresh": "<refresh_token>"
        }
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                # 将token加入黑名单（需要配置Simple JWT的BlacklistApp）
                token.blacklist()
            
            return Response({
                'status': 'success',
                'message': '登出成功'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'登出失败：{str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理API视图集
    
    提供用户的CRUD操作
    
    端点：
    - GET    /api/users/              # 用户列表（管理员）
    - GET    /api/users/{id}/         # 用户详情（管理员）
    - GET    /api/users/me/           # 当前用户信息
    - PUT    /api/users/me/           # 更新当前用户信息
    - PATCH  /api/users/me/           # 部分更新
    - POST   /api/users/change-password/  # 修改密码
    - POST   /api/users/upload-avatar/    # 上传头像
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        根据不同的action设置不同的权限
        
        - me相关操作：需要登录
        - list、retrieve、update、destroy：需要管理员权限
        """
        if self.action in ['me', 'update_me', 'change_password', 'upload_avatar']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    def get_queryset(self):
        """
        优化查询性能
        
        使用select_related预加载profile，减少数据库查询次数
        """
        return super().get_queryset().select_related('profile')
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        获取当前用户信息
        
        GET /api/users/me/
        Authorization: Bearer <access_token>
        """
        serializer = UserSerializer(request.user, context={'request': request})
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """
        更新当前用户信息
        
        PUT/PATCH /api/users/me/
        {
            "first_name": "张",
            "last_name": "三",
            "phone": "13800138000",
            "bio": "这是我的个人简介",
            "gender": "M"
        }
        """
        partial = request.method == 'PATCH'  # PATCH支持部分更新
        
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=partial,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # 返回更新后的完整用户信息
            return Response({
                'status': 'success',
                'message': '更新成功',
                'data': UserSerializer(request.user, context={'request': request}).data
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
                'message': '密码修改成功，请重新登录'
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
        Content-Type: multipart/form-data
        
        Form Data:
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
        max_size = 2 * 1024 * 1024  # 2MB
        if avatar.size > max_size:
            return Response({
                'status': 'error',
                'message': '图片大小不能超过2MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存头像
        request.user.profile.avatar = avatar
        request.user.profile.save()
        
        # 返回新的头像URL
        serializer = UserProfileSerializer(
            request.user.profile,
            context={'request': request}
        )
        
        return Response({
            'status': 'success',
            'message': '头像上传成功',
            'data': {
                'avatar_url': serializer.data['avatar_url']
            }
        })
    
    @action(detail=False, methods=['delete'])
    def delete_avatar(self, request):
        """
        删除头像
        
        DELETE /api/users/delete-avatar/
        """
        if request.user.profile.avatar:
            request.user.profile.avatar.delete()
            request.user.profile.save()
            
            return Response({
                'status': 'success',
                'message': '头像已删除'
            })
        
        return Response({
            'status': 'error',
            'message': '您还没有上传头像'
        }, status=status.HTTP_400_BAD_REQUEST)



