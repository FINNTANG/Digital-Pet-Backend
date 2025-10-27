"""
LLM服务相关的视图函数

这个文件包含了LLM服务的所有视图函数。
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .services import LangChainLLMService
from .models import ChatMessage
import json


def chat_view(request):
    """
    聊天界面视图
    
    显示聊天界面，用户可以在这里与AI进行对话。
    支持游客访问（未登录用户也可以使用）。
    """
    
    # 获取会话ID（如果没有则使用默认值）
    session_id = request.GET.get('session_id', 'default')
    
    # 创建LLM服务实例（支持游客访问）
    user = request.user if request.user.is_authenticated else None
    llm_service = LangChainLLMService(user=user)
    
    # 获取聊天历史
    chat_history = llm_service.get_chat_history(session_id, limit=50)
    
    # 渲染模板
    context = {
        'session_id': session_id,
        'chat_history': chat_history,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'llm_service/chat.html', context)


@require_http_methods(["POST"])
def send_message(request):
    """
    发送消息API
    
    处理用户发送的消息，调用LLM服务获取回复。
    这是一个AJAX API，返回JSON格式的响应。
    支持游客访问（未登录用户也可以使用）。
    """
    
    try:
        # 获取POST数据
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        pet_type = data.get('pet_type')  # 获取宠物类型参数
        image_data = data.get('image_data')  # 获取图片数据（可选）
        
        print(f"[视图层调试] 收到请求 - message: {user_message[:50]}..., pet_type: {pet_type}")
        print(f"[视图层调试] image_data存在: {bool(image_data)}, 类型: {type(image_data)}, 长度: {len(image_data) if image_data else 0}")
        if image_data:
            print(f"[视图层调试] image_data前50字符: {image_data[:50]}")
        
        # 验证消息不为空
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': '消息不能为空'
            }, status=400)
        
        # 创建LLM服务实例（支持游客访问）
        user = request.user if request.user.is_authenticated else None
        llm_service = LangChainLLMService(user=user)
        
        # 获取AI回复（传递宠物类型参数和图片数据）
        print(f"[视图层调试] 准备调用llm_service.chat()...")
        ai_response = llm_service.chat(user_message, session_id, pet_type=pet_type, image_data=image_data)
        print(f"[视图层调试] llm_service.chat() 返回完成")
        
        # 返回成功响应（ai_response 已经是包含完整信息的字典）
        if isinstance(ai_response, dict):
            return JsonResponse({
                'success': True,
                'data': ai_response,
                # 为了向后兼容，保留response字段
                'response': ai_response.get('message', str(ai_response))
            })
        else:
            # 兼容旧格式
            return JsonResponse({
                'success': True,
                'message': user_message,
                'response': ai_response
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'服务器错误：{str(e)}'
        }, status=500)


def chat_history_view(request):
    """
    聊天历史视图
    
    显示用户的所有聊天会话和历史记录。
    只有登录用户才能查看历史记录，游客将看到提示信息。
    """
    
    # 检查用户是否登录
    if not request.user.is_authenticated:
        context = {
            'sessions': {},
            'total_messages': 0,
            'is_guest': True,
        }
        return render(request, 'llm_service/history.html', context)
    
    # 获取用户的所有聊天消息，按会话分组
    messages = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:100]
    
    # 按会话ID分组
    sessions = {}
    for msg in messages:
        if msg.session_id not in sessions:
            sessions[msg.session_id] = []
        sessions[msg.session_id].append(msg)
    
    context = {
        'sessions': sessions,
        'total_messages': messages.count(),
        'is_guest': False,
    }
    return render(request, 'llm_service/history.html', context)


def new_session(request):
    """
    创建新会话
    
    生成一个新的会话ID并跳转到聊天界面。
    支持游客访问。
    """
    import uuid
    
    # 生成唯一的会话ID
    new_session_id = str(uuid.uuid4())
    
    # 重定向到聊天界面
    return redirect(f'/llm/chat/?session_id={new_session_id}')


@require_http_methods(["POST"])
def clear_history(request):
    """
    清空聊天历史
    
    删除指定会话的所有消息。
    只有登录用户可以清空历史记录。
    """
    
    try:
        # 检查用户是否登录
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': '请先登录'
            }, status=401)
        
        data = json.loads(request.body)
        session_id = data.get('session_id', 'default')
        
        # 删除该会话的所有消息
        deleted_count = ChatMessage.objects.filter(
            user=request.user,
            session_id=session_id
        ).delete()[0]
        
        return JsonResponse({
            'success': True,
            'message': f'已删除 {deleted_count} 条消息'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
