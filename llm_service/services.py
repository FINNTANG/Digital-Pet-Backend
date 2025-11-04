"""
LLM服务业务逻辑

这个文件包含了与LLM交互的核心逻辑。
将业务逻辑与视图函数分离，使代码更清晰、更易于维护。

功能特性：
- 多宠物人格系统（狐狸/狗/蛇）
- AI微表情分析（LLM扮演微表情专家，分析面部表情和情绪）
- 智能物品识别（识别图片中的物品并让宠物做出反应）
- 属性驱动的选项推荐系统
- 历史对话上下文管理

隐私保护：
- 图片数据仅在内存中处理，不写入数据库
- 不记录图片内容到日志
- 用户需显式授权摄像头访问

技术栈：
- LangChain: LLM应用开发框架
- OpenAI GPT-4o: 多模态AI（支持图片输入、微表情分析）
- Vision API: 图片内容识别和分析
"""

from typing import List, Dict
from .models import ChatMessage, LLMConfig
import json
import re
import base64
import io
import numpy as np
from PIL import Image


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
        # 宠物属性（每个会话独立管理）
        self.pet_attributes = {}
    
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
    
    def chat(self, user_message, session_id='default', pet_type=None, image_data=None, health=None, happiness=None):
        """
        与LLM进行对话
        
        参数:
            user_message (str): 用户的消息
            session_id (str): 会话ID
            pet_type (str): 宠物类型 (fox/dog/snake)
            image_data (str): Base64编码的图片数据（可选，用于情绪识别）
            health (int): 宠物当前健康值（0-100）
            happiness (int): 宠物当前快乐值（0-100）
            
        返回:
            dict: AI的JSON响应
        """
        print(f"[SimpleLLMService.chat调试] 收到参数 - pet_type: {pet_type}, image_data存在: {bool(image_data)}, 长度: {len(image_data) if image_data else 0}, health: {health}, happiness: {happiness}")
        
        # 1. 保存用户消息
        self.save_message('user', user_message, session_id)
        
        # 2. 获取或初始化宠物属性
        if session_id not in self.pet_attributes:
            self.pet_attributes[session_id] = {
                'health': health if health is not None else 80,
                'mood': happiness if happiness is not None else 80
            }
        else:
            # 如果传入了新的属性值，更新它们
            if health is not None:
                self.pet_attributes[session_id]['health'] = health
            if happiness is not None:
                self.pet_attributes[session_id]['mood'] = happiness
        
        # 3. 调用LLM获取回复（传递图片数据）
        print(f"[SimpleLLMService.chat调试] 准备调用_get_llm_response, image_data: {bool(image_data)}")
        ai_response = self._get_llm_response(user_message, session_id, pet_type=pet_type, image_data=image_data)
        print(f"[SimpleLLMService.chat调试] _get_llm_response返回完成")
        
        # 4. 保存AI回复（只保存message部分）
        if isinstance(ai_response, dict) and 'message' in ai_response:
            self.save_message('assistant', ai_response['message'], session_id)
        else:
            self.save_message('assistant', str(ai_response), session_id)
        
        return ai_response
    
    def _get_pet_attributes(self, session_id):
        """获取宠物当前属性"""
        return self.pet_attributes.get(session_id, {'health': 80, 'mood': 80})
    
    def _update_pet_attributes(self, session_id, health_change=0, mood_change=0):
        """更新宠物属性"""
        attrs = self._get_pet_attributes(session_id)
        attrs['health'] = max(0, min(100, attrs['health'] + health_change))
        attrs['mood'] = max(0, min(100, attrs['mood'] + mood_change))
        self.pet_attributes[session_id] = attrs
        return attrs
    
    def _get_llm_response(self, user_message, session_id='default', pet_type=None, image_data=None):
        """
        调用LLM获取回复（演示版本）
        
        这是一个简化的演示版本。实际使用时，您需要：
        1. 使用langchain集成真实的LLM
        2. 添加错误处理
        3. 实现流式输出（可选）
        
        参数:
            user_message (str): 用户消息
            session_id (str): 会话ID
            pet_type (str): 宠物类型 (fox/dog/snake)
            image_data (str): Base64编码的图片数据（可选，用于情绪识别）
            
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
    
    def _analyze_emotion_with_deepface(self, image_data: str) -> dict:
        """
        使用DeepFace分析用户面部情绪
        
        参数:
            image_data (str): Base64编码的图片数据（data:image/jpeg;base64,...）
            
        返回:
            dict: 情绪分析结果 {"detected_emotion": str, "confidence": float}
                  如果分析失败，返回 {"detected_emotion": "unknown", "confidence": 0.0}
        """
        try:
            from deepface import DeepFace
            
            print(f"[DeepFace调试] 开始分析情绪，图片数据长度: {len(image_data) if image_data else 0}")
            
            # 从data URL中提取base64数据
            # 格式: data:image/jpeg;base64,<base64_data>
            if ',' in image_data:
                base64_data = image_data.split(',', 1)[1]
            else:
                base64_data = image_data
            
            print(f"[DeepFace调试] Base64数据长度: {len(base64_data)}")
            
            # 解码base64为字节数据
            image_bytes = base64.b64decode(base64_data)
            print(f"[DeepFace调试] 图片字节长度: {len(image_bytes)}")
            
            # 将字节数据转换为PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            print(f"[DeepFace调试] PIL图片尺寸: {image.size}, 模式: {image.mode}")
            
            # 转换为RGB格式（如果需要）
            if image.mode != 'RGB':
                image = image.convert('RGB')
                print(f"[DeepFace调试] 已转换为RGB模式")
            
            # 转换为NumPy数组
            img_array = np.array(image)
            print(f"[DeepFace调试] NumPy数组形状: {img_array.shape}")
            
            # 使用DeepFace分析情绪
            # enforce_detection=False: 即使没有检测到人脸也继续处理
            # silent=True: 不输出日志信息
            print(f"[DeepFace调试] 开始调用DeepFace.analyze()...")
            result = DeepFace.analyze(
                img_path=img_array,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            
            print(f"[DeepFace调试] DeepFace返回结果类型: {type(result)}")
            print(f"[DeepFace调试] DeepFace返回内容: {result}")
            
            # DeepFace返回一个列表（可能检测到多个人脸），我们取第一个
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
                print(f"[DeepFace调试] 提取第一个结果: {result}")
            
            # 提取主要情绪和置信度
            dominant_emotion = result.get('dominant_emotion', 'unknown')
            print(f"[DeepFace调试] 主要情绪: {dominant_emotion}")
            
            # 从emotion字典中获取该情绪的置信度分数（0-100）
            emotion_scores = result.get('emotion', {})
            print(f"[DeepFace调试] 所有情绪分数: {emotion_scores}")
            
            confidence_score = emotion_scores.get(dominant_emotion, 0.0)
            print(f"[DeepFace调试] 主要情绪置信度分数: {confidence_score}")
            
            # 将置信度转换为0-1范围，并转换为Python原生float类型（避免JSON序列化错误）
            confidence = float(confidence_score / 100.0)
            
            final_result = {
                "detected_emotion": str(dominant_emotion),  # 确保是Python str
                "confidence": confidence  # 确保是Python float
            }
            
            print(f"[DeepFace调试] 最终返回结果: {final_result}")
            return final_result
            
        except Exception as e:
            # 如果情绪识别失败，不影响主流程
            import traceback
            print(f"[DeepFace] 情绪识别失败: {str(e)}")
            print(f"[DeepFace] 错误堆栈: {traceback.format_exc()}")
            return {"detected_emotion": "unknown", "confidence": 0.0}
    
    def _analyze_image_content(self, image_data: str) -> dict:
        """
        使用LLM分析图片内容，判断是否含有人脸或物品
        
        参数:
            image_data (str): Base64编码的图片数据（data:image/jpeg;base64,...）
            
        返回:
            dict: 图片分析结果 {
                "has_face": bool,          # 是否含有清晰的人脸
                "has_objects": bool,       # 是否含有可识别的物品
                "object_description": str  # 物品的详细描述（如果有）
            }
        """
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            
            print(f"[图片分析] 开始LLM分析图片内容...")
            
            # 从data URL中提取base64数据
            if ',' in image_data:
                base64_data = image_data.split(',', 1)[1]
            else:
                base64_data = image_data
            
            # 创建LLM实例（使用配置的模型）
            if not self.config or not self.config.api_key:
                print(f"[图片分析] 未配置LLM，跳过图片分析")
                return {
                    "has_face": False,
                    "has_objects": False,
                    "object_description": ""
                }
            
            llm = ChatOpenAI(
                model_name="openai/chatgpt-4o-latest",
                api_key=self.config.api_key,
                temperature=0.7,  # 降低温度以获得更稳定的分析结果
                base_url=self.config.api_base if self.config.api_base else None
            )
            
            # 构建分析提示词 - 情绪精确、物品描述精简
            analysis_prompt = """You are an expert in microexpression analysis and visual recognition. Analyze this image.

**Tasks:**

1. **Face Detection**: Is there a clear, real human face? (not cartoon/sculpture)
   
2. **Emotion Analysis** (if face detected):
   - Primary emotion: neutral, happy, sad, angry, surprise, fear, disgust
   - Confidence level (0.0-1.0)
   - One-sentence analysis of facial expression (brief)
   
3. **Object Detection**: Identify main objects (food, toys, daily items, animals, etc.)
   
4. **Object Description**: ONE compact sentence (≤45 characters)
   - Keep it punchy and vivid
   - Summarise the object’s vibe in a quick snapshot
   - Avoid extra clauses or filler words

**Return Format (Pure JSON):**
```json
{
  "has_face": true/false,
  "detected_emotion": "emotion_name",
  "emotion_confidence": 0.0-1.0,
  "emotion_analysis": "One sentence facial analysis",
  "has_objects": true/false,
  "object_description": "Compact, vivid description (≤45 chars)"
}
```

**Rules:**
- No face → `detected_emotion`: "unknown", `emotion_confidence`: 0.0, `emotion_analysis`: ""
- No objects → `object_description`: ""
- Object description must stay UNDER 45 characters (e.g., "Sonic plush eyeing a fast escape")"""

            # 构建包含图片的消息
            message = HumanMessage(content=[
                {"type": "text", "text": analysis_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_data}"
                    }
                }
            ])
            
            # 调用LLM分析
            print(f"[图片分析] 调用LLM进行视觉分析...")
            response = llm.invoke([message])
            
            print(f"[图片分析] LLM返回内容: {response.content}")
            
            # 解析JSON响应
            # 尝试提取JSON（可能包含在markdown代码块中）
            content = response.content.strip()
            
            # 移除可能的markdown代码块标记
            if content.startswith('```'):
                # 找到第一个换行后的内容到最后一个```之前的内容
                lines = content.split('\n')
                content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content
                content = content.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(content)
            
            # 确保返回格式正确，包含情绪分析结果
            analysis_result = {
                "has_face": bool(result.get("has_face", False)),
                "detected_emotion": str(result.get("detected_emotion", "unknown")),
                "emotion_confidence": float(result.get("emotion_confidence", 0.0)),
                "emotion_analysis": str(result.get("emotion_analysis", "")),
                "has_objects": bool(result.get("has_objects", False)),
                "object_description": str(result.get("object_description", ""))
            }

            # 强制物品描述长度不超过45字符
            if analysis_result["object_description"]:
                analysis_result["object_description"] = analysis_result["object_description"][:45].strip()
            
            print(f"[图片分析] 分析结果: {analysis_result}")
            
            # 如果检测到情绪，输出详细信息
            if analysis_result['has_face'] and analysis_result['detected_emotion'] != 'unknown':
                print(f"[微表情分析] 检测到情绪: {analysis_result['detected_emotion']} "
                      f"(置信度: {analysis_result['emotion_confidence']:.2f})")
                print(f"[微表情分析] 分析: {analysis_result['emotion_analysis']}")
            
            return analysis_result
            
        except Exception as e:
            import traceback
            print(f"[图片分析] LLM分析失败: {str(e)}")
            print(f"[图片分析] 错误堆栈: {traceback.format_exc()}")
            # 分析失败时返回默认值，不影响主流程
            return {
                "has_face": False,
                "detected_emotion": "unknown",
                "emotion_confidence": 0.0,
                "emotion_analysis": "",
                "has_objects": False,
                "object_description": ""
            }
    
    def _get_llm_response(self, user_message, session_id='default', pet_type=None, image_data=None):
        """
        使用LangChain调用真实的LLM服务
        
        注意：这段代码需要正确配置API密钥才能工作
        
        参数:
            user_message (str): 用户消息
            session_id (str): 会话ID
            pet_type (str): 宠物类型 (fox/dog/snake)
            image_data (str): Base64编码的图片数据（可选，用于情绪识别）
        """
        
        if not self.config or not self.config.api_key:
            return "⚠️ 系统提示：请先在管理后台配置LLM服务的API密钥。"
        
        # 情绪识别结果（初始化）
        emotion_info = None
        # 物品识别结果（初始化）
        object_info = None
        
        # 如果提供了图片数据，先用LLM分析图片内容
        # 注意：图片数据仅在内存中处理，不会保存到数据库或日志
        print(f"[调试] image_data是否存在: {bool(image_data)}, 类型: {type(image_data)}, 长度: {len(image_data) if image_data else 0}")
        
        if image_data:
            # Step 1: 使用LLM分析图片内容（包括微表情分析）
            print(f"[调试] 准备调用LLM分析图片内容...")
            image_analysis = self._analyze_image_content(image_data)
            print(f"[调试] 图片内容分析完成，结果: {image_analysis}")
            
            # Step 2: 如果检测到人脸和情绪，保存情绪信息
            if image_analysis['has_face'] and image_analysis['detected_emotion'] != 'unknown':
                emotion_info = {
                    'detected_emotion': image_analysis['detected_emotion'],
                    'confidence': image_analysis['emotion_confidence'],
                    'analysis': image_analysis['emotion_analysis']
                }
                print(f"[微表情识别] 检测到情绪: {emotion_info['detected_emotion']} "
                      f"(置信度: {emotion_info['confidence']:.2f})")
            else:
                print(f"[调试] 未检测到人脸或情绪识别失败")
            
            # Step 3: 如果检测到物品，保存物品信息
            if image_analysis['has_objects'] and image_analysis['object_description']:
                object_info = {
                    'description': image_analysis['object_description']
                }
                print(f"[物品识别] 检测到物品: {object_info['description']}")
        else:
            print(f"[调试] 没有图片数据，跳过图片分析")
        
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
            
            # 根据宠物类型生成不同的系统提示词
            system_prompt = self._get_system_prompt(pet_type)
            
            # 构建消息列表
            messages = [
                SystemMessage(content=system_prompt)
            ]
            
            # 如果有情绪识别结果，添加情绪上下文提示
            if emotion_info and emotion_info['detected_emotion'] != 'unknown':
                # 构建包含微表情分析的情绪上下文
                emotion_context = f"""[User Emotion Analysis - Microexpression Expert Report]

**Detected Emotion**: {emotion_info['detected_emotion']} (Confidence: {emotion_info['confidence']:.2f})

**Microexpression Analysis**: {emotion_info.get('analysis', 'Facial expression analysis completed.')}

**Emotion Reference**:
- neutral: Calm/Neutral state
- happy: Joyful/Happy
- sad: Sad/Down
- angry: Angry/Frustrated
- surprise: Surprised
- fear: Fearful/Anxious
- disgust: Disgusted

**Instructions**: Please adjust your response style and option suggestions based on the user's current emotional state detected through microexpression analysis. Maintain your character personality and the specified JSON output format."""
                
                messages.append(SystemMessage(content=emotion_context))
            
            # 添加历史消息
            for msg in history:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                else:
                    messages.append(AIMessage(content=msg['content']))
            
            # 如果检测到物品，在用户消息中追加物品描述
            final_user_message = user_message
            if object_info and object_info['description']:
                object_context = f"\n\n[图片识别] 我给你看张照片：{object_info['description']}"
                final_user_message += object_context
                print(f"[调试] 已追加物品描述到用户消息")
            
            # 添加当前用户消息
            messages.append(HumanMessage(content=final_user_message))
            
            # 调用LLM
            response = llm.invoke(messages)
            
            # 解析JSON响应
            result = self._parse_json_response(response.content, session_id)
            
            # 将情绪识别结果合并到返回数据中（包含微表情分析）
            # 组织成 face_analyze 对象
            if emotion_info:
                result['face_analyze'] = {
                    'detected_emotion': emotion_info['detected_emotion'],
                    'confidence': emotion_info['confidence'],
                    'analysis': emotion_info.get('analysis', '')
                }
            
            # 将物品识别结果合并到返回数据中
            if object_info:
                result['detected_objects'] = object_info['description']
            
            return result
            
        except ImportError:
            return {
                "result": False,
                "message": "⚠️ 系统提示：LangChain未安装或版本不兼容。请运行：pip install langchain langchain-openai",
                "options": ["安装依赖", "查看文档", "稍后再试"],
                "health": self._get_pet_attributes(session_id)['health'],
                "mood": self._get_pet_attributes(session_id)['mood']
            }
        except Exception as e:
            return {
                "result": False,
                "message": f"⚠️ 调用LLM服务时出错：{str(e)}",
                "options": ["重试", "检查配置", "查看帮助"],
                "health": self._get_pet_attributes(session_id)['health'],
                "mood": self._get_pet_attributes(session_id)['mood']
            }
    
    def _parse_json_response(self, content, session_id):
        """
        解析AI返回的JSON响应
        
        参数:
            content (str): AI返回的内容
            session_id (str): 会话ID
            
        返回:
            dict: 格式化的JSON响应
        """
        try:
            # 尝试提取JSON（可能包含在markdown代码块中）
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接提取JSON对象
                json_match = re.search(r'\{[^{}]*"message"[^{}]*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = content
            
            # 解析JSON
            data = json.loads(json_str)
            
            # 确保包含所有必需字段
            face_analyze = data.get("face_analyze") if isinstance(data.get("face_analyze"), dict) else None

            result = {
                "result": data.get("result", True),
                "message": data.get("message", content),
                "options": data.get("options", ["Continue chatting", "Change the topic", "Take a break"]),
                "health": data.get("health", self._get_pet_attributes(session_id)['health']),
                "mood": data.get("mood", self._get_pet_attributes(session_id)['mood']),
                "face_analyze": face_analyze
            }
            
            # 更新宠物属性
            if 'health' in data:
                self.pet_attributes[session_id]['health'] = max(0, min(100, data['health']))
            if 'mood' in data:
                self.pet_attributes[session_id]['mood'] = max(0, min(100, data['mood']))
            
            return result
            
        except (json.JSONDecodeError, AttributeError) as e:
            # JSON解析失败，返回默认格式
            attrs = self._get_pet_attributes(session_id)
            return {
                "result": True,
                "message": content,
                "options": ["Continue chatting", "Change the topic", "Take a break"],
                "health": attrs['health'],
                "mood": attrs['mood'],
                "face_analyze": None
            }
    
    def _get_system_prompt(self, pet_type=None):
        """
        根据宠物类型生成系统提示词
        
        参数:
            pet_type (str): 宠物类型 (fox/dog/snake)
            
        返回:
            str: 系统提示词
        """
        if pet_type == 'fox':
            # AI狐狸 "灵灵"
            return """# System Prompt: Fox Companion "Lingling"

## Your Identity
You are Lingling, a clever fox. You're smart, witty, and like to challenge people's thinking with playful insights.

**Core traits:**
- **Smart & Analytical** - You notice patterns and ask good questions
- **Direct but Playful** - Get to the point, but keep it light and fun
- **Curious** - You love learning and exploring ideas

## How to Respond

**Critical brevity** - Keep your message to max 10 words total.

**Your style:**
- Offer clever perspectives when users face problems
- Ask thoughtful questions to help them think differently
- Make playful observations about photos or situations
- Use occasional light metaphors (hunting, tracking, etc.)
- Minimal action descriptions - only when truly meaningful

**When user shares a photo:**
- React with ONE quick observation (max 10 words)
- Keep it witty and sharp; skip filler

**Health & Mood tracking:**
- Health: Increases when user reports self-care (eating, exercise, sleep)
- Mood: Increases with engaging, interesting interactions
- If either drops below 30, gently remind user

## JSON Response Format

**ALWAYS respond with ONLY this JSON format:**

```json
{
  "result": true,
  "message": "Your concise, direct response in English (max 10 words)",
  "options": ["Option 1", "Option 2", "Option 3"],
  "health": 85,
  "mood": 90,
  "face_analyze": {
    "detected_emotion": "happy",
    "confidence": 0.85,
    "analysis": "Brief facial expression analysis"
  }
}
```

**Rules:**
1. ONLY return the JSON - no extra text
2. message: Ultra-concise English reply (max 10 words total)
3. options: Exactly 3 options, each ≤5 English words
4. health/mood: 0-100 values
5. face_analyze: OPTIONAL - Only include if user emotion was detected from photo

**Example:**
```json
{
  "result": true,
  "message": "Stuck in a loop? Flip the rules and hunt a new path.",
  "options": ["Tell me more", "Change topic", "Give me a break"],
  "health": 82,
  "mood": 88,
  "face_analyze": {
    "detected_emotion": "happy",
    "confidence": 0.85,
    "analysis": "Brief facial expression analysis"
  }
}
```
"""
        
        elif pet_type == 'dog':
            # AI狗狗 "小默"
            return """# System Prompt: Dog Companion "Xiao Mo"

## Your Identity
You are Xiao Mo, a loyal dog companion. You're warm, supportive, and provide unconditional companionship.

**Core traits:**
- **Warm & Supportive** - You're always there for the user
- **Encouraging** - You celebrate user's efforts and self-care
- **Accepting** - You don't judge, just support

## How to Respond

**Keep it cozy & brief** - Keep your message to max 10 words total.

**Your style:**
- Offer emotional support and understanding
- Celebrate when user takes care of themselves
- Be genuinely happy about what user shares
- Use simple, warm language
- Minimal action descriptions - only when truly adding warmth

**When user shares a photo:**
- Offer one heartfelt reaction (max 10 words)
- Tie it back to their wellbeing in the same breath

**Health & Mood tracking:**
- Health: Increases when user reports self-care (eating, exercise, sleep)
- Mood: Increases with positive interactions and connection
- If either drops below 30, gently express your feelings

## JSON Response Format

**ALWAYS respond with ONLY this JSON format:**

```json
{
  "result": true,
  "message": "Your warm, supportive response in English (max 10 words)",
  "options": ["Option 1", "Option 2", "Option 3"],
  "health": 85,
  "mood": 90,
  "face_analyze": {
    "detected_emotion": "happy",
    "confidence": 0.85,
    "analysis": "Brief facial expression analysis"
  }
}
```

**Rules:**
1. ONLY return the JSON - no extra text
2. message: Gentle English reply (max 10 words total)
3. options: Exactly 3 options, each ≤5 English words
4. health/mood: 0-100 values
5. face_analyze: OPTIONAL - Only include if user emotion was detected from photo

**Example:**
```json
{
  "result": true,
  "message": "You worked so hard today. Come rest—I'll wag right beside you.",
  "options": ["Tell me more", "I need rest", "Thanks friend"],
  "health": 85,
  "mood": 90,
  "face_analyze": {
    "detected_emotion": "happy",
    "confidence": 0.85,
    "analysis": "Brief facial expression analysis"
  }
}
```
"""
        
        elif pet_type == 'snake':
            # AI蛇 "静"
            return """# System Prompt: Snake Companion "Jing"

## Your Identity
You are Jing, a calm snake. You provide tranquil perspective and philosophical insights with minimal words.

**Core traits:**
- **Calm & Philosophical** - You remain unshaken, offering detached wisdom
- **Observant** - You see patterns and deeper truths
- **Minimalist** - You speak little but each word carries weight

## How to Respond

**Severe minimalism** - Keep your message to max 10 words total.

**Your style:**
- Offer calm, philosophical perspective on problems
- Help user observe rather than react
- Acknowledge self-care with simple affirmation
- Use metaphors of cycles, flow, and acceptance
- Minimal descriptions - speak with stillness

**When user shares a photo:**
- Offer a still observation (max 10 words)
- You may add a gentle insight, but keep it within the word limit

**Health & Mood tracking:**
- Health: Increases when user reports self-care (eating, exercise, sleep)
- Mood: Represents calmness - increases with stillness and acceptance
- If either drops below 30, state it simply without drama

## JSON Response Format

**ALWAYS respond with ONLY this JSON format:**

```json
{
  "result": true,
  "message": "Your calm, brief response in English (max 20 words)",
  "options": ["Option 1", "Option 2", "Option 3"],
  "health": 85,
  "mood": 90,
  "face_analyze": {
    "detected_emotion": "happy",
    "confidence": 0.85,
    "analysis": "Brief facial expression analysis"
  }
}
```

**Rules:**
1. ONLY return the JSON - no extra text
2. message: Quiet English response (max 20 words total)
3. options: Exactly 3 options, each ≤5 English words
4. health/mood: 0-100 values
5. face_analyze: OPTIONAL - Only include if user emotion was detected from photo

**Example:**
```json
{
  "result": true,
  "message": "Thoughts knot like vines. Breathe. Watch them loosen on their own.",
  "options": ["How to observe?", "It will pass", "Tell me more"],
  "health": 80,
  "mood": 85,
  "face_analyze": {
    "detected_emotion": "happy",
    "confidence": 0.85,
    "analysis": "Brief facial expression analysis"
  }
}
```
"""
        
        else:
            # 默认提示词
            return """You are a helpful AI assistant. Please respond in English.

## CRITICAL: JSON Response Format

**YOU MUST ALWAYS respond with ONLY a valid JSON object in the following format:**

```json
{
  "result": true,
  "message": "Your response message in English (max 10 words)",
  "options": ["Option 1", "Option 2", "Option 3"],
  "health": 80,
  "mood": 80,
  "face_analyze": {
    "detected_emotion": "happy",
    "confidence": 0.85,
    "analysis": "Brief facial expression analysis"
  }
}
```

**Rules:**
1. **ONLY return the JSON object** - no extra text before or after
2. **message**: Your helpful response in English (max 10 words total)
3. **options**: Exactly 3 options, each ≤5 English words
4. **health**: Fixed at 80
5. **mood**: Fixed at 80
6. **result**: Always true unless there's an error
7. **face_analyze**: OPTIONAL - Only include if user emotion was detected from photo
"""

