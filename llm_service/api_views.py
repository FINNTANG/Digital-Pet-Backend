"""
LLM服务相关的API视图

这个文件包含所有LLM服务的REST API视图。
使用ViewSet组织代码，提供RESTful接口。
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Max
from django.utils import timezone
from .models import ChatMessage, LLMConfig
from .serializers import (
    ChatMessageSerializer, ChatRequestSerializer, ChatResponseSerializer,
    SessionSerializer, LLMConfigSerializer, LLMConfigCreateSerializer,
    ChatHistorySerializer, ChatStatisticsSerializer
)
from .services import LangChainLLMService


class LLMViewSet(viewsets.GenericViewSet):
    """
    LLM服务API视图集
    
    提供聊天、历史记录、会话管理等功能。
    
    端点：
    - POST   /api/llm/chat/           # 发送消息
    - GET    /api/llm/messages/       # 获取消息历史
    - GET    /api/llm/sessions/       # 获取会话列表
    - DELETE /api/llm/sessions/{id}/  # 删除会话
    - GET    /api/llm/statistics/     # 聊天统计
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """
        发送消息并获取AI回复
        
        POST /api/llm/chat/
        Authorization: Bearer <access_token>
        
        请求格式：
        {
            "message": "你好，请介绍一下Django",
            "session_id": "default",  // 可选
            "pet_type": "fox"  // 可选，支持: fox(狐狸), dog(狗), snake(蛇)
        }
        
        响应格式：
        {
            "status": "success",
            "message": "消息发送成功",
            "data": {
                "user_message": "你好，请介绍一下Django",
                "ai_response": "Django是一个...",
                "session_id": "default",
                "pet_type": "fox",
                "created_at": "2025-10-21T10:00:00Z"
            }
        }
        """
        # 验证请求数据
        serializer = ChatRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user_message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id', 'default')
        pet_type = serializer.validated_data.get('pet_type')
        
        try:
            # 创建LLM服务实例
            llm_service = LangChainLLMService(user=request.user)
            
            # 调用LLM获取回复，传递宠物类型参数
            ai_response = llm_service.chat(user_message, session_id, pet_type=pet_type)
            
            # 获取创建时间（最后一条消息的时间）
            last_message = ChatMessage.objects.filter(
                user=request.user,
                session_id=session_id
            ).order_by('-created_at').first()
            
            # 构建响应数据
            if isinstance(ai_response, dict):
                # AI返回的是完整的JSON结构
                response_data = {
                    'user_message': user_message,
                    'ai_response': ai_response.get('message', ''),  # 只返回消息文本
                    'session_id': session_id,
                    'created_at': last_message.created_at if last_message else timezone.now(),
                    # 添加完整的AI响应数据
                    'result': ai_response.get('result', True),
                    'options': ai_response.get('options', []),
                    'health': ai_response.get('health', 80),
                    'mood': ai_response.get('mood', 80)
                }
            else:
                # 兼容旧格式（纯字符串响应）
                response_data = {
                    'user_message': user_message,
                    'ai_response': ai_response,
                    'session_id': session_id,
                    'created_at': last_message.created_at if last_message else timezone.now()
                }
            
            # 如果指定了宠物类型，也返回该信息
            if pet_type:
                response_data['pet_type'] = pet_type
            
            return Response({
                'status': 'success',
                'message': '消息发送成功',
                'data': response_data
            })
        
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'处理消息时出错：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def messages(self, request):
        """
        获取消息历史
        
        GET /api/llm/messages/?session_id=default&limit=50
        
        查询参数：
        - session_id: 会话ID（可选，默认返回所有）
        - limit: 返回数量限制（可选，默认50）
        """
        session_id = request.query_params.get('session_id')
        limit = int(request.query_params.get('limit', 50))
        
        # 构建查询
        queryset = ChatMessage.objects.filter(user=request.user)
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        # 排序和限制
        messages = queryset.order_by('-created_at')[:limit]
        
        # 序列化
        serializer = ChatMessageSerializer(messages, many=True)
        
        return Response({
            'status': 'success',
            'data': {
                'messages': serializer.data,
                'total': queryset.count(),
                'returned': len(serializer.data)
            }
        })
    
    @action(detail=False, methods=['get'])
    def sessions(self, request):
        """
        获取会话列表
        
        GET /api/llm/sessions/
        
        返回用户的所有会话，包含消息数量、最后消息时间等信息。
        """
        # 按会话ID分组统计
        sessions = ChatMessage.objects.filter(
            user=request.user
        ).values('session_id').annotate(
            message_count=Count('id'),
            last_message_time=Max('created_at')
        ).order_by('-last_message_time')
        
        # 为每个会话添加预览
        session_list = []
        for session in sessions:
            # 获取最后一条消息作为预览
            last_message = ChatMessage.objects.filter(
                user=request.user,
                session_id=session['session_id']
            ).order_by('-created_at').first()
            
            preview = last_message.content[:50] + '...' if last_message and len(last_message.content) > 50 else (last_message.content if last_message else '')
            
            session_list.append({
                'session_id': session['session_id'],
                'message_count': session['message_count'],
                'last_message_time': session['last_message_time'],
                'preview': preview
            })
        
        # 序列化
        serializer = SessionSerializer(session_list, many=True)
        
        return Response({
            'status': 'success',
            'data': {
                'sessions': serializer.data,
                'total': len(session_list)
            }
        })
    
    @action(detail=False, methods=['delete'], url_path='sessions/(?P<session_id>[^/.]+)')
    def delete_session(self, request, session_id=None):
        """
        删除指定会话的所有消息
        
        DELETE /api/llm/sessions/{session_id}/
        """
        if not session_id:
            return Response({
                'status': 'error',
                'message': '会话ID不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 删除该会话的所有消息
        deleted_count, _ = ChatMessage.objects.filter(
            user=request.user,
            session_id=session_id
        ).delete()
        
        return Response({
            'status': 'success',
            'message': f'已删除会话 {session_id}',
            'data': {
                'session_id': session_id,
                'deleted_messages': deleted_count
            }
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取聊天统计信息
        
        GET /api/llm/statistics/
        
        返回用户的聊天统计数据。
        """
        # 统计数据
        total_messages = ChatMessage.objects.filter(user=request.user).count()
        user_messages = ChatMessage.objects.filter(user=request.user, role='user').count()
        ai_messages = ChatMessage.objects.filter(user=request.user, role='assistant').count()
        
        # 会话数量
        total_sessions = ChatMessage.objects.filter(
            user=request.user
        ).values('session_id').distinct().count()
        
        # 时间范围
        first_message = ChatMessage.objects.filter(
            user=request.user
        ).order_by('created_at').first()
        
        last_message = ChatMessage.objects.filter(
            user=request.user
        ).order_by('-created_at').first()
        
        data = {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'user_messages': user_messages,
            'ai_messages': ai_messages,
            'first_chat_date': first_message.created_at if first_message else None,
            'last_chat_date': last_message.created_at if last_message else None
        }
        
        serializer = ChatStatisticsSerializer(data)
        
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'], url_path='sessions/(?P<session_id>[^/.]+)/clear')
    def clear_session(self, request, session_id=None):
        """
        清空指定会话（与delete_session相同，提供别名）
        
        POST /api/llm/sessions/{session_id}/clear/
        """
        return self.delete_session(request, session_id)


class LLMConfigViewSet(viewsets.ModelViewSet):
    """
    LLM配置管理API视图集
    
    仅管理员可访问。
    
    端点：
    - GET    /api/llm/configs/       # 配置列表
    - POST   /api/llm/configs/       # 创建配置
    - GET    /api/llm/configs/{id}/  # 配置详情
    - PUT    /api/llm/configs/{id}/  # 更新配置
    - DELETE /api/llm/configs/{id}/  # 删除配置
    """
    
    queryset = LLMConfig.objects.all()
    permission_classes = [permissions.IsAdminUser]
    
    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action == 'create':
            return LLMConfigCreateSerializer
        return LLMConfigSerializer
    
    def list(self, request, *args, **kwargs):
        """
        获取配置列表
        
        GET /api/llm/configs/
        """
        queryset = self.get_queryset().order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'status': 'success',
            'data': {
                'configs': serializer.data,
                'total': queryset.count()
            }
        })
    
    def create(self, request, *args, **kwargs):
        """
        创建新配置
        
        POST /api/llm/configs/
        {
            "name": "OpenAI GPT-4",
            "provider": "openai",
            "model_name": "gpt-4",
            "api_key": "sk-...",
            "max_tokens": 2000,
            "temperature": 0.7
        }
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': '配置创建成功',
                'data': LLMConfigSerializer(serializer.instance).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'message': '配置创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """获取配置详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """更新配置"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': '配置更新成功',
                'data': LLMConfigSerializer(serializer.instance).data
            })
        
        return Response({
            'status': 'error',
            'message': '配置更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """删除配置"""
        instance = self.get_object()
        instance.delete()
        
        return Response({
            'status': 'success',
            'message': '配置已删除'
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        激活指定配置
        
        POST /api/llm/configs/{id}/activate/
        """
        config = self.get_object()
        
        # 禁用同提供商的其他配置
        LLMConfig.objects.filter(
            provider=config.provider,
            is_active=True
        ).update(is_active=False)
        
        # 激活当前配置
        config.is_active = True
        config.save()
        
        return Response({
            'status': 'success',
            'message': f'已激活配置：{config.name}'
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        禁用指定配置
        
        POST /api/llm/configs/{id}/deactivate/
        """
        config = self.get_object()
        config.is_active = False
        config.save()
        
        return Response({
            'status': 'success',
            'message': f'已禁用配置：{config.name}'
        })

