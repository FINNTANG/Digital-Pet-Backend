"""
LLM服务业务逻辑

这个文件包含了与LLM交互的核心逻辑。
将业务逻辑与视图函数分离，使代码更清晰、更易于维护。
"""

from typing import List, Dict
from .models import ChatMessage, LLMConfig


class SimpleLLMService:
    """
    简单的LLM服务类
    
    这是一个简化版的LLM服务，用于演示基本功能。
    实际使用时，您需要：
    1. 安装langchain: pip install langchain
    2. 安装LLM提供商的SDK（如openai）
    3. 配置API密钥
    """
    
    def __init__(self, user=None):
        """
        初始化LLM服务
        
        参数:
            user: 当前用户对象（可选）
        """
        self.user = user
        self.config = self._get_active_config()
    
    def _get_active_config(self):
        """
        获取当前启用的LLM配置
        
        返回:
            LLMConfig对象或None
        """
        try:
            # 获取第一个启用的配置
            return LLMConfig.objects.filter(is_active=True).first()
        except:
            return None
    
    def get_chat_history(self, session_id='default', limit=10):
        """
        获取聊天历史
        
        参数:
            session_id (str): 会话ID
            limit (int): 返回的消息数量限制
            
        返回:
            List[Dict]: 聊天消息列表
        """
        if not self.user:
            return []
        
        # 查询数据库获取历史消息
        messages = ChatMessage.objects.filter(
            user=self.user,
            session_id=session_id
        ).order_by('created_at')[:limit]
        
        # 转换为字典格式
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at
            }
            for msg in messages
        ]
    
    def save_message(self, role, content, session_id='default'):
        """
        保存消息到数据库
        
        参数:
            role (str): 消息角色（'user' 或 'assistant'）
            content (str): 消息内容
            session_id (str): 会话ID
            
        返回:
            ChatMessage对象
        """
        if not self.user:
            return None
        
        message = ChatMessage.objects.create(
            user=self.user,
            role=role,
            content=content,
            session_id=session_id
        )
        return message
    
    def chat(self, user_message, session_id='default'):
        """
        与LLM进行对话
        
        参数:
            user_message (str): 用户的消息
            session_id (str): 会话ID
            
        返回:
            str: AI的回复
        """
        # 1. 保存用户消息
        self.save_message('user', user_message, session_id)
        
        # 2. 调用LLM获取回复（这里使用简单的演示版本）
        ai_response = self._get_llm_response(user_message, session_id)
        
        # 3. 保存AI回复
        self.save_message('assistant', ai_response, session_id)
        
        return ai_response
    
    def _get_llm_response(self, user_message, session_id='default'):
        """
        调用LLM获取回复（演示版本）
        
        这是一个简化的演示版本。实际使用时，您需要：
        1. 使用langchain集成真实的LLM
        2. 添加错误处理
        3. 实现流式输出（可选）
        
        参数:
            user_message (str): 用户消息
            session_id (str): 会话ID
            
        返回:
            str: AI的回复
        """
        
        # 检查是否有配置
        if not self.config:
            return "⚠️ 系统提示：LLM服务未配置。请在管理后台添加LLM配置。"
        
        # 演示版本：返回简单的回复
        # TODO: 集成真实的LLM服务
        demo_response = f"""
这是一个演示回复。

您的消息：{user_message}

当前配置：
- 提供商：{self.config.get_provider_display()}
- 模型：{self.config.model_name}

要使用真实的LLM服务，请按以下步骤操作：

1. 安装必要的库：
   pip install langchain langchain-openai

2. 在管理后台配置API密钥

3. 取消注释下面的代码并删除这个演示版本

## 真实LLM集成示例代码（需要取消注释）：

```python
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# 创建LLM实例
llm = ChatOpenAI(
    model_name=self.config.model_name,
    api_key=self.config.api_key,
    temperature=self.config.temperature,
    max_tokens=self.config.max_tokens
)

# 获取历史消息
history = self.get_chat_history(session_id, limit=5)

# 构建消息列表
messages = [
    SystemMessage(content="你是一个有帮助的AI助手。")
]

for msg in history:
    if msg['role'] == 'user':
        messages.append(HumanMessage(content=msg['content']))
    else:
        messages.append(AIMessage(content=msg['content']))

messages.append(HumanMessage(content=user_message))

# 调用LLM
response = llm.invoke(messages)
return response.content
```
        """
        
        return demo_response


class LangChainLLMService(SimpleLLMService):
    """
    基于LangChain的LLM服务（完整版）
    
    这个类继承自SimpleLLMService，实现了真实的LLM集成。
    使用前请确保已安装：pip install langchain langchain-openai
    """
    
    def _get_llm_response(self, user_message, session_id='default'):
        """
        使用LangChain调用真实的LLM服务
        
        注意：这段代码需要正确配置API密钥才能工作
        """
        
        if not self.config or not self.config.api_key:
            return "⚠️ 系统提示：请先在管理后台配置LLM服务的API密钥。"
        
        try:
            # 导入LangChain相关模块
            # 注意：这些导入可能会失败，如果未安装相应的包
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            
            # 创建LLM实例
            llm = ChatOpenAI(
                model_name=self.config.model_name,
                api_key=self.config.api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                base_url=self.config.api_base if self.config.api_base else None
            )
            
            # 获取历史消息（最近5条）
            history = self.get_chat_history(session_id, limit=5)
            
            # 构建消息列表
            messages = [
                SystemMessage(content="你是一个有帮助的AI助手，请用中文回答用户的问题。")
            ]
            
            # 添加历史消息
            for msg in history:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                else:
                    messages.append(AIMessage(content=msg['content']))
            
            # 添加当前用户消息
            messages.append(HumanMessage(content=user_message))
            
            # 调用LLM
            response = llm.invoke(messages)
            return response.content
            
        except ImportError:
            return """
⚠️ 系统提示：LangChain未安装或版本不兼容。

请运行以下命令安装必要的依赖：
pip install langchain langchain-openai

然后重启Django服务器。
            """
        except Exception as e:
            return f"⚠️ 调用LLM服务时出错：{str(e)}\n\n请检查API密钥和网络连接是否正常。"

