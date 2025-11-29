# LLM服务API快速测试指南

## 🚀 5分钟快速测试

### 前提条件
- ✅ 服务器已启动：`python manage.py runserver`
- ✅ 已有用户账号（或创建新账号）

## 📝 测试步骤

### 第1步：获取Access Token（1分钟）

**方式A：使用已有账号登录**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "你的用户名",
    "password": "你的密码"
  }'
```

**方式B：注册新账号**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!@#",
    "password_confirm": "Test123!@#"
  }'
```

**保存返回的Token**：
```json
{
  "status": "success",
  "data": {
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",  ← 复制这个
      "refresh": "..."
    }
  }
}
```

---

### 第2步：发送第一条消息（1分钟）

**替换`<TOKEN>`为实际的access token**

```bash
curl -X POST http://127.0.0.1:8000/api/llm/chat/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下自己"
  }'
```

**预期响应**：
```json
{
  "status": "success",
  "message": "消息发送成功",
  "data": {
    "user_message": "你好，请介绍一下自己",
    "ai_response": "这是一个演示回复...",
    "session_id": "default",
    "created_at": "2025-10-21T10:00:00Z"
  }
}
```

---

### 第3步：查看消息历史（30秒）

```bash
curl -X GET "http://127.0.0.1:8000/api/llm/messages/?limit=10" \
  -H "Authorization: Bearer <TOKEN>"
```

**预期响应**：
```json
{
  "status": "success",
  "data": {
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "你好，请介绍一下自己",
        ...
      },
      {
        "id": 2,
        "role": "assistant",
        "content": "这是一个演示回复...",
        ...
      }
    ],
    "total": 2,
    "returned": 2
  }
}
```

---

### 第4步：查看会话列表（30秒）

```bash
curl -X GET http://127.0.0.1:8000/api/llm/sessions/ \
  -H "Authorization: Bearer <TOKEN>"
```

**预期响应**：
```json
{
  "status": "success",
  "data": {
    "sessions": [
      {
        "session_id": "default",
        "message_count": 2,
        "last_message_time": "2025-10-21T10:00:00Z",
        "preview": "你好，请介绍一下自己..."
      }
    ],
    "total": 1
  }
}
```

---

### 第5步：查看统计信息（30秒）

```bash
curl -X GET http://127.0.0.1:8000/api/llm/statistics/ \
  -H "Authorization: Bearer <TOKEN>"
```

**预期响应**：
```json
{
  "status": "success",
  "data": {
    "total_sessions": 1,
    "total_messages": 2,
    "user_messages": 1,
    "ai_messages": 1,
    "first_chat_date": "2025-10-21T10:00:00Z",
    "last_chat_date": "2025-10-21T10:00:00Z"
  }
}
```

---

### 第6步：使用Swagger UI测试（2分钟）

**浏览器访问**：http://127.0.0.1:8000/api/docs/

1. 点击右上角"Authorize"按钮
2. 输入Token：`Bearer <your_access_token>`
3. 点击"Authorize"确认
4. 找到"llm"分组
5. 展开`POST /api/llm/chat/`
6. 点击"Try it out"
7. 输入消息内容
8. 点击"Execute"
9. 查看响应结果

**优势**：
- ✅ 可视化界面
- ✅ 自动格式化JSON
- ✅ 实时测试
- ✅ 查看完整文档

---

## 🧪 完整测试用例

### 测试1：发送多条消息

```bash
# 消息1
curl -X POST http://127.0.0.1:8000/api/llm/chat/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"message": "什么是Python？"}'

# 消息2
curl -X POST http://127.0.0.1:8000/api/llm/chat/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Python有哪些特点？"}'

# 消息3
curl -X POST http://127.0.0.1:8000/api/llm/chat/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"message": "谢谢你的解答！"}'
```

### 测试2：使用不同会话

```bash
# 会话1（默认）
curl -X POST http://127.0.0.1:8000/api/llm/chat/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "这是会话1的消息",
    "session_id": "default"
  }'

# 会话2（自定义）
curl -X POST http://127.0.0.1:8000/api/llm/chat/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "这是会话2的消息",
    "session_id": "session-2"
  }'

# 查看所有会话
curl -X GET http://127.0.0.1:8000/api/llm/sessions/ \
  -H "Authorization: Bearer <TOKEN>"
```

### 测试3：会话管理

```bash
# 查看特定会话的消息
curl -X GET "http://127.0.0.1:8000/api/llm/messages/?session_id=default" \
  -H "Authorization: Bearer <TOKEN>"

# 删除指定会话
curl -X DELETE http://127.0.0.1:8000/api/llm/sessions/default/ \
  -H "Authorization: Bearer <TOKEN>"

# 确认删除
curl -X GET http://127.0.0.1:8000/api/llm/sessions/ \
  -H "Authorization: Bearer <TOKEN>"
```

### 测试4：管理LLM配置（需要管理员Token）

```bash
# 获取管理员Token（使用超级用户账号）
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin_password"
  }'

# 创建LLM配置
curl -X POST http://127.0.0.1:8000/api/llm-configs/ \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "OpenAI GPT-4",
    "provider": "openai",
    "model_name": "gpt-4",
    "api_key": "sk-test-key",
    "max_tokens": 2000,
    "temperature": 0.7
  }'

# 查看所有配置
curl -X GET http://127.0.0.1:8000/api/llm-configs/ \
  -H "Authorization: Bearer <ADMIN_TOKEN>"

# 激活配置
curl -X POST http://127.0.0.1:8000/api/llm-configs/1/activate/ \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

---

## ✅ 验收标准

### 必须通过的测试
- [ ] ✅ 可以获取Token
- [ ] ✅ 可以发送消息
- [ ] ✅ 可以查看历史
- [ ] ✅ 可以查看会话列表
- [ ] ✅ 可以查看统计
- [ ] ✅ 可以删除会话
- [ ] ✅ Swagger UI可访问
- [ ] ✅ 管理员可以管理配置

### 预期响应格式
所有API应返回统一格式：
```json
{
  "status": "success" | "error",
  "message": "操作提示",
  "data": { ... }
}
```

---

## 🐛 常见问题

### Q1: 401 Unauthorized错误

**原因**：Token过期或无效

**解决**：
```bash
# 重新登录获取新Token
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Q2: 403 Forbidden错误

**原因**：访问需要管理员权限的接口

**解决**：使用管理员账号登录获取Token

### Q3: 500 Internal Server Error

**原因**：服务器内部错误

**解决**：
1. 检查服务器日志
2. 确认数据库正常
3. 验证LLM服务配置

### Q4: 404 Not Found

**原因**：URL路径错误

**解决**：检查URL是否正确，参考API文档

---

## 📊 性能测试（可选）

### 测试并发请求

```bash
# 安装ab工具（Apache Bench）
# Ubuntu: sudo apt-get install apache2-utils
# Mac: brew install apache2

# 并发测试（100个请求，10个并发）
ab -n 100 -c 10 \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -p message.json \
  http://127.0.0.1:8000/api/llm/chat/
```

**message.json**：
```json
{"message": "测试消息"}
```

---

## 🎯 下一步

### 测试通过后
1. ✅ 集成真实LangChain
2. ✅ 配置API密钥
3. ✅ 测试真实AI对话
4. ✅ 优化性能

### 如果测试失败
1. 检查服务器是否运行
2. 验证Token是否有效
3. 查看错误日志
4. 参考API文档

---

**准备好测试了吗？** 🚀

选择一种方式开始：
- 💻 使用curl命令行测试
- 🌐 使用Swagger UI可视化测试
- 📱 使用Postman测试

祝测试顺利！✨

















