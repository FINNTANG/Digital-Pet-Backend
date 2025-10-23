# AI 宠物 JSON 响应结构说明

## 📋 概述

AI 宠物系统现在返回固定的 JSON 结构，包含：
- ✅ **回复消息** (message)
- ✅ **交互选项** (options)
- ✅ **健康值** (health)
- ✅ **情绪值** (mood)
- ✅ **状态标识** (result)

---

## 📦 JSON 响应格式

### 标准格式

```json
{
  "result": true,
  "message": "宠物的回复内容（包含动作描述）",
  "options": ["选项1", "选项2", "选项3"],
  "health": 85,
  "mood": 90
}
```

### 字段说明

| 字段 | 类型 | 范围/值 | 说明 |
|------|------|---------|------|
| **result** | boolean | true/false | 执行状态，true表示成功 |
| **message** | string | - | AI宠物的回复消息，包含动作描述 |
| **options** | array | 3个元素 | 供用户选择的交互选项（每个≤10汉字）|
| **health** | integer | 0-100 | 宠物的健康/元气值 |
| **mood** | integer | 0-100 | 宠物的情绪/平静值 |

---

## 🎭 不同宠物类型的示例

### 🦊 狐狸 "灵灵"

```json
{
  "result": true,
  "message": "*耳朵抖了抖*... 你的思绪又绕成一团毛线了。这样可抓不到'老鼠'（问题）呢～",
  "options": ["那你有什么高见？", "换个话题吧", "让我静静"],
  "health": 82,
  "mood": 88
}
```

**属性含义:**
- `health`: 灵力、敏捷度、活力
- `mood`: 好奇心、玩乐欲、信任度

---

### 🐕 狗狗 "小默"

```json
{
  "result": true,
  "message": "*尾巴摇成旋风！* 哇！你回来了！我好想你！",
  "options": ["摸摸我的头", "和你玩游戏", "我们散步吧"],
  "health": 85,
  "mood": 95
}
```

**属性含义:**
- `health`: 身体活力、能量
- `mood`: 快乐、安全感、情感连接

---

### 🐍 蛇 "静"

```json
{
  "result": true,
  "message": "*Sss...* 你的心跳... 太快了。这只是'感觉'，不是'事实'。",
  "options": ["如何才能'观察'？", "它终将过去", "我就是很焦虑"],
  "health": 80,
  "mood": 85
}
```

**属性含义:**
- `health`: 元气、生命能量、鳞片光泽
- `mood`: 平静、禅定、内心平衡

---

### 🤖 默认助手

```json
{
  "result": true,
  "message": "我理解你的问题。让我帮你分析一下...",
  "options": ["继续", "换个话题", "结束"],
  "health": 80,
  "mood": 80
}
```

**属性含义:**
- `health`: 固定值 80
- `mood`: 固定值 80

---

## 🔄 API 响应结构

### REST API (`/api/llm/chat/`)

**请求:**
```json
{
  "message": "你好",
  "session_id": "session_123",
  "pet_type": "fox"
}
```

**响应:**
```json
{
  "status": "success",
  "message": "消息发送成功",
  "data": {
    "user_message": "你好",
    "ai_response": "*歪头，耳朵直立*... 哦？找我？有什么新鲜事吗？",
    "session_id": "session_123",
    "pet_type": "fox",
    "created_at": "2025-10-23T10:30:00Z",
    "result": true,
    "options": ["分享个八卦", "问你个问题", "就看看你"],
    "health": 85,
    "mood": 88
  }
}
```

### Web 视图 (`/llm/send_message/`)

**请求:**
```json
{
  "message": "你好",
  "session_id": "default",
  "pet_type": "dog"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "result": true,
    "message": "*汪！* 我在我在！*尾巴狂摇*",
    "options": ["玩接球游戏", "今天怎么样？", "摸摸下巴"],
    "health": 90,
    "mood": 95
  },
  "response": "*汪！* 我在我在！*尾巴狂摇*"
}
```

---

## 🎯 属性值变化规则

### Health (健康/元气) 变化

| 触发条件 | 变化 | 说明 |
|---------|------|------|
| 用户报告吃饭 | +5~10 | "我吃饭了" / "我吃了顿好的" |
| 用户报告运动 | +5~10 | "我运动了" / "我散步了" |
| 用户报告休息 | +5~10 | "我准备睡了" / "我刚午休了" |
| 长时间未互动 | -2~-5 | 24小时以上无互动 |
| 用户报告不良习惯 | -3~-8 | "熬夜了" / "没吃饭" |

### Mood (情绪/平静) 变化

| 触发条件 | 变化 | 说明 |
|---------|------|------|
| 积极互动 | +3~8 | 玩游戏、分享开心事 |
| 共情陪伴 | +5~10 | 被抚摸、温暖对话 |
| 有趣互动 | +5~10 | 猜谜、新知识、幽默 |
| 用户倾诉焦虑 | -2~-5 | 负面情绪（狐狸和蛇较少下降）|
| 被忽视 | -3~-8 | 长时间无互动 |

### 属性范围限制

- **最小值**: 0 （极度虚弱/低落）
- **最大值**: 100 （完美状态）
- **初始值**: 80 （良好状态）
- **警戒线**: < 30 （需要关注）

---

## 💻 后端实现

### 1. Services 层 (`services.py`)

#### 属性管理

```python
class SimpleLLMService:
    def __init__(self, user=None):
        self.user = user
        self.config = self._get_active_config()
        # 宠物属性（每个会话独立管理）
        self.pet_attributes = {}
    
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
```

#### JSON 解析

```python
def _parse_json_response(self, content, session_id):
    """解析AI返回的JSON响应"""
    try:
        # 提取JSON（可能包含在markdown代码块中）
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_match = re.search(r'\{[^{}]*"message"[^{}]*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = content
        
        # 解析JSON
        data = json.loads(json_str)
        
        # 确保包含所有必需字段
        result = {
            "result": data.get("result", True),
            "message": data.get("message", content),
            "options": data.get("options", ["继续聊天", "换个话题", "休息一下"]),
            "health": data.get("health", self._get_pet_attributes(session_id)['health']),
            "mood": data.get("mood", self._get_pet_attributes(session_id)['mood'])
        }
        
        # 更新宠物属性
        if 'health' in data:
            self.pet_attributes[session_id]['health'] = max(0, min(100, data['health']))
        if 'mood' in data:
            self.pet_attributes[session_id]['mood'] = max(0, min(100, data['mood']))
        
        return result
        
    except (json.JSONDecodeError, AttributeError):
        # JSON解析失败，返回默认格式
        attrs = self._get_pet_attributes(session_id)
        return {
            "result": True,
            "message": content,
            "options": ["继续聊天", "换个话题", "休息一下"],
            "health": attrs['health'],
            "mood": attrs['mood']
        }
```

### 2. 系统提示词修改

每个宠物的系统提示词末尾都添加了：

```
## V. CRITICAL: JSON Response Format

**YOU MUST ALWAYS respond with ONLY a valid JSON object in the following format:**

```json
{
  "result": true,
  "message": "Your response message in Chinese with action descriptions",
  "options": ["选项1 (≤10字)", "选项2 (≤10字)", "选项3 (≤10字)"],
  "health": 85,
  "mood": 90
}
```

**Rules:**
1. **ONLY return the JSON object** - no extra text before or after
2. **message**: Your personality-driven response in Chinese, with *action descriptions*
3. **options**: Exactly 3 options, each ≤10 Chinese characters
4. **health**: Current health value (0-100), adjust based on user's self-care
5. **mood**: Current emotion value (0-100), adjust based on interaction quality
6. **result**: Always true unless there's an error
```

### 3. Views 层修改

#### `views.py`

```python
# 获取AI回复（传递宠物类型参数）
ai_response = llm_service.chat(user_message, session_id, pet_type=pet_type)

# 返回成功响应（ai_response 已经是包含完整信息的字典）
if isinstance(ai_response, dict):
    return JsonResponse({
        'success': True,
        'data': ai_response,
        # 为了向后兼容，保留response字段
        'response': ai_response.get('message', str(ai_response))
    })
```

#### `api_views.py`

```python
# 构建响应数据
if isinstance(ai_response, dict):
    # AI返回的是完整的JSON结构
    response_data = {
        'user_message': user_message,
        'ai_response': ai_response.get('message', ''),
        'session_id': session_id,
        'created_at': last_message.created_at if last_message else timezone.now(),
        # 添加完整的AI响应数据
        'result': ai_response.get('result', True),
        'options': ai_response.get('options', []),
        'health': ai_response.get('health', 80),
        'mood': ai_response.get('mood', 80)
    }
```

---

## 📝 使用示例

### Python 客户端

```python
import requests

API_URL = "http://127.0.0.1:8000/api/llm/chat/"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

data = {
    "message": "我今天吃了健康的午餐",
    "pet_type": "dog",
    "session_id": "my_session"
}

response = requests.post(API_URL, json=data, headers=headers)
result = response.json()

# 访问数据
print(f"AI回复: {result['data']['ai_response']}")
print(f"选项: {result['data']['options']}")
print(f"健康值: {result['data']['health']}")
print(f"情绪值: {result['data']['mood']}")
```

### JavaScript 客户端

```javascript
fetch('/api/llm/chat/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: '我今天运动了',
    pet_type: 'fox',
    session_id: 'my_session'
  })
})
.then(response => response.json())
.then(data => {
  console.log('AI回复:', data.data.ai_response);
  console.log('选项:', data.data.options);
  console.log('健康值:', data.data.health);
  console.log('情绪值:', data.data.mood);
  
  // 显示选项按钮
  data.data.options.forEach(option => {
    console.log(`[${option}]`);
  });
});
```

---

## ✅ 向后兼容性

### 旧格式支持

如果 AI 返回的不是 JSON 格式（纯文本），系统会自动包装成标准格式：

```json
{
  "result": true,
  "message": "纯文本回复内容",
  "options": ["继续聊天", "换个话题", "休息一下"],
  "health": 80,
  "mood": 80
}
```

### Web 视图兼容

为了向后兼容，Web 视图响应中保留了 `response` 字段：

```json
{
  "success": true,
  "data": {
    "result": true,
    "message": "...",
    "options": [...],
    "health": 85,
    "mood": 90
  },
  "response": "..."  // 兼容字段，包含纯文本消息
}
```

---

## 🎉 功能优势

1. **统一格式**: 所有宠物类型返回相同结构
2. **易于解析**: 标准 JSON 格式，便于客户端处理
3. **交互增强**: 提供选项引导用户互动
4. **状态可视化**: 健康值和情绪值可实时显示
5. **游戏化**: 属性变化增加趣味性
6. **向后兼容**: 不影响现有功能

---

## 🔧 修改的文件

- ✅ `llm_service/services.py` - 添加属性管理和 JSON 解析
- ✅ `llm_service/views.py` - 修改响应格式
- ✅ `llm_service/api_views.py` - 修改 API 响应格式
- ✅ 所有系统提示词 - 添加 JSON 输出要求

---

## 🚀 下一步建议

1. **前端UI**: 在聊天界面显示健康值和情绪值进度条
2. **选项按钮**: 将 options 渲染成可点击的按钮
3. **属性持久化**: 将属性值保存到数据库
4. **属性可视化**: 用图表展示属性变化趋势
5. **成就系统**: 根据属性值解锁成就
6. **提醒功能**: 当属性值过低时提醒用户

---

## 📚 相关文档

- [宠物类型聊天功能说明.md](./宠物类型聊天功能说明.md)
- [聊天页面宠物选择功能说明.md](./聊天页面宠物选择功能说明.md)
- [真实LLM集成完成报告.md](./真实LLM集成完成报告.md)
