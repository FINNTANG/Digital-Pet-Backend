# Django用户管理与LLM服务

一个对Python新手友好的Django项目，集成了用户管理系统和LLM（大语言模型）聊天服务。

## 📋 项目特点

- ✨ **新手友好**：代码简洁清晰，包含详细的中文注释
- 🔐 **用户管理**：完整的注册、登录、登出功能
- 🤖 **LLM服务**：基于LangChain的AI聊天功能
- 🎨 **美观界面**：现代化的UI设计，良好的用户体验
- 📝 **聊天历史**：自动保存对话记录
- 🛡️ **安全可靠**：使用Django内置的安全机制

## 🚀 快速开始

### 1. 环境要求

- Python 3.8 或更高版本
- pip（Python包管理工具）

### 2. 安装依赖

```bash
# 安装项目依赖
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
# 创建数据库表
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建管理员账号

```bash
# 创建超级用户（用于访问管理后台）
python manage.py createsuperuser
```

按提示输入用户名、邮箱和密码。

### 5. 运行开发服务器

```bash
# 启动服务器
python manage.py runserver
```

服务器启动后，在浏览器中访问：http://127.0.0.1:8000/

## 📱 功能使用

### 用户管理

1. **注册账号**：访问 http://127.0.0.1:8000/accounts/register/ 创建新账号
2. **登录系统**：访问 http://127.0.0.1:8000/accounts/login/ 登录
3. **个人中心**：查看和管理个人信息
4. **登出系统**：安全退出登录状态

### LLM聊天服务

1. **开始聊天**：登录后点击"AI聊天"进入聊天界面
2. **查看历史**：查看所有历史对话记录
3. **新建会话**：开始一个新的对话会话
4. **清空历史**：删除当前会话的消息

### 管理后台

访问 http://127.0.0.1:8000/admin/ 使用超级用户账号登录管理后台。

在管理后台可以：
- 管理用户账号
- 查看和删除聊天消息
- **配置LLM服务**（重要！）

## ⚙️ LLM服务配置

### 演示模式

项目默认使用演示模式，会返回模拟的AI回复。要使用真实的LLM服务，需要进行以下配置：

### 配置真实的LLM服务

1. **在管理后台添加LLM配置**
   - 访问：http://127.0.0.1:8000/admin/llm_service/llmconfig/
   - 点击"增加 LLM配置"
   - 填写以下信息：
     - 配置名称：例如 "OpenAI配置"
     - 提供商：选择您使用的LLM提供商
     - 模型名称：例如 "gpt-3.5-turbo"
     - API密钥：您的API密钥
     - 是否启用：勾选

2. **修改服务类（可选）**
   
   如果要使用真实的LLM服务，需要修改 `llm_service/services.py`：
   
   ```python
   # 在 llm_service/views.py 中，将：
   llm_service = SimpleLLMService(user=request.user)
   
   # 改为：
   llm_service = LangChainLLMService(user=request.user)
   ```

3. **环境变量配置（推荐）**
   
   为了安全，建议使用环境变量存储API密钥：
   
   创建 `.env` 文件：
   ```
   OPENAI_API_KEY=your-api-key-here
   ```
   
   然后在 `settings.py` 中加载：
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
   ```

### 支持的LLM提供商

- **OpenAI**：GPT-3.5、GPT-4等
- **Azure OpenAI**：Azure托管的OpenAI服务
- **Anthropic**：Claude系列模型
- **本地模型**：Ollama等本地部署的模型

## 📂 项目结构

```
django/
├── mysite/                    # 项目配置目录
│   ├── settings.py            # 全局配置
│   ├── urls.py                # 主URL路由
│   └── wsgi.py                # WSGI配置
├── accounts/                  # 用户管理应用
│   ├── models.py              # 数据模型
│   ├── views.py               # 视图函数
│   ├── forms.py               # 表单定义
│   ├── urls.py                # URL路由
│   └── templates/             # HTML模板
│       └── accounts/
├── llm_service/               # LLM服务应用
│   ├── models.py              # 数据模型
│   ├── views.py               # 视图函数
│   ├── services.py            # LLM业务逻辑
│   ├── admin.py               # 管理后台配置
│   ├── urls.py                # URL路由
│   └── templates/             # HTML模板
│       └── llm_service/
├── db.sqlite3                 # SQLite数据库
├── manage.py                  # Django管理脚本
├── requirements.txt           # 项目依赖
├── README.md                  # 项目说明
└── SPECKIT.CONSTITUTION.md    # 项目宪章
```

## 🎓 学习指南

### 对新手的建议

如果您是Python/Django新手，建议按以下顺序学习代码：

1. **先看模型（models.py）**：了解数据结构
2. **再看视图（views.py）**：理解业务逻辑
3. **然后看模板（templates/）**：学习前端展示
4. **最后看URL（urls.py）**：理解路由配置

### 代码注释说明

- 每个文件开头都有整体说明
- 每个类和函数都有详细的文档字符串
- 复杂的逻辑都有行内注释
- 关键概念都有额外的解释

### 推荐的学习资源

- [Django官方文档（中文）](https://docs.djangoproject.com/zh-hans/5.2/)
- [LangChain官方文档](https://python.langchain.com/)
- [Python官方教程（中文）](https://docs.python.org/zh-cn/3/tutorial/)

## 🔧 开发指南

### 添加新功能

1. 在相应的应用中创建/修改文件
2. 更新数据库（如果修改了models.py）：
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. 测试功能是否正常工作

### 代码风格

项目遵循以下代码规范：
- 使用有意义的变量名和函数名
- 添加详细的中文注释
- 保持代码简洁，避免过度抽象
- 详见 `SPECKIT.CONSTITUTION.md`

## 🐛 常见问题

### Q: 安装依赖时出错？

A: 确保使用Python 3.8+版本，并尝试更新pip：
```bash
pip install --upgrade pip
```

### Q: 数据库迁移失败？

A: 删除 `db.sqlite3` 和 `migrations/` 文件夹中的迁移文件（保留 `__init__.py`），然后重新迁移：
```bash
python manage.py makemigrations
python manage.py migrate
```

### Q: LLM服务不工作？

A: 检查以下几点：
1. 是否安装了 `langchain` 和 `langchain-openai`
2. 是否在管理后台配置了API密钥
3. API密钥是否有效
4. 网络连接是否正常

### Q: 如何使用本地LLM模型？

A: 可以使用Ollama等本地模型，需要：
1. 安装Ollama：https://ollama.ai/
2. 安装对应的LangChain集成：`pip install langchain-community`
3. 修改 `services.py` 中的LLM初始化代码

## 📝 更新日志

### v1.0 (2025-10-21)
- ✨ 初始版本发布
- 🔐 实现用户注册、登录、登出功能
- 🤖 集成LangChain LLM服务
- 📝 实现聊天历史记录功能
- 🎨 创建美观的用户界面

## 📄 许可证

本项目仅供学习使用。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

如有问题，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件

---

**祝您使用愉快！如果这个项目对您有帮助，请给它一个Star ⭐️**


