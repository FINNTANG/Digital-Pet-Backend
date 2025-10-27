# Django 用户管理与 LLM 服务

一个对 Python 新手友好的 Django 项目，集成了用户管理系统和 LLM（大语言模型）聊天服务。

## 📋 项目特点

- ✨ **新手友好**：代码简洁清晰，包含详细的中文注释
- 🔐 **用户管理**：完整的注册、登录、登出功能
- 🤖 **LLM 服务**：基于 LangChain 的 AI 聊天功能
- 🎨 **美观界面**：现代化的 UI 设计，良好的用户体验
- 📝 **聊天历史**：自动保存对话记录
- 🛡️ **安全可靠**：使用 Django 内置的安全机制

## 🚀 快速开始

### 方式一：Docker 部署（推荐）⭐

**最简单的部署方式，3 步完成！**

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 2. 一键启动（Windows）
.\deploy.ps1

# 或者（Linux/Mac）
chmod +x deploy.sh && ./deploy.sh

# 3. 访问应用
# http://localhost
```

📖 详细说明请查看：
- [快速启动指南](QUICK_START.md) - 3 分钟快速上手
- [完整部署文档](DOCKER_DEPLOYMENT.md) - 详细的生产环境部署指南

### 方式二：传统部署

#### 1. 环境要求

- Python 3.8 或更高版本
- pip（Python 包管理工具）

#### 2. 安装依赖

```bash
# 安装项目依赖
pip install -r requirements.txt
```

#### 3. 初始化数据库

```bash
# 创建数据库表
python manage.py makemigrations
python manage.py migrate
```

#### 4. 创建管理员账号

```bash
# 创建超级用户（用于访问管理后台）
python manage.py createsuperuser
```

按提示输入用户名、邮箱和密码。

#### 5. 运行开发服务器

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

### LLM 聊天服务

1. **开始聊天**：登录后点击"AI 聊天"进入聊天界面
2. **查看历史**：查看所有历史对话记录
3. **新建会话**：开始一个新的对话会话
4. **清空历史**：删除当前会话的消息

### 管理后台

访问 http://127.0.0.1:8000/admin/ 使用超级用户账号登录管理后台。

在管理后台可以：

- 管理用户账号
- 查看和删除聊天消息
- **配置 LLM 服务**（重要！）

## ⚙️ LLM 服务配置

### 演示模式

项目默认使用演示模式，会返回模拟的 AI 回复。要使用真实的 LLM 服务，需要进行以下配置：

### 配置真实的 LLM 服务

1. **在管理后台添加 LLM 配置**

   - 访问：http://127.0.0.1:8000/admin/llm_service/llmconfig/
   - 点击"增加 LLM 配置"
   - 填写以下信息：
     - 配置名称：例如 "OpenAI 配置"
     - 提供商：选择您使用的 LLM 提供商
     - 模型名称：例如 "gpt-3.5-turbo"
     - API 密钥：您的 API 密钥
     - 是否启用：勾选

2. **修改服务类（可选）**

   如果要使用真实的 LLM 服务，需要修改 `llm_service/services.py`：

   ```python
   # 在 llm_service/views.py 中，将：
   llm_service = SimpleLLMService(user=request.user)

   # 改为：
   llm_service = LangChainLLMService(user=request.user)
   ```

3. **环境变量配置（推荐）**

   为了安全，建议使用环境变量存储 API 密钥：

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

### 支持的 LLM 提供商

- **OpenAI**：GPT-3.5、GPT-4 等
- **Azure OpenAI**：Azure 托管的 OpenAI 服务
- **Anthropic**：Claude 系列模型
- **本地模型**：Ollama 等本地部署的模型

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

如果您是 Python/Django 新手，建议按以下顺序学习代码：

1. **先看模型（models.py）**：了解数据结构
2. **再看视图（views.py）**：理解业务逻辑
3. **然后看模板（templates/）**：学习前端展示
4. **最后看 URL（urls.py）**：理解路由配置

### 代码注释说明

- 每个文件开头都有整体说明
- 每个类和函数都有详细的文档字符串
- 复杂的逻辑都有行内注释
- 关键概念都有额外的解释

### 推荐的学习资源

- [Django 官方文档（中文）](https://docs.djangoproject.com/zh-hans/5.2/)
- [LangChain 官方文档](https://python.langchain.com/)
- [Python 官方教程（中文）](https://docs.python.org/zh-cn/3/tutorial/)

## 🔧 开发指南

### 添加新功能

1. 在相应的应用中创建/修改文件
2. 更新数据库（如果修改了 models.py）：
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

A: 确保使用 Python 3.8+版本，并尝试更新 pip：

```bash
pip install --upgrade pip
```

### Q: 数据库迁移失败？

A: 删除 `db.sqlite3` 和 `migrations/` 文件夹中的迁移文件（保留 `__init__.py`），然后重新迁移：

```bash
python manage.py makemigrations
python manage.py migrate
```

### Q: LLM 服务不工作？

A: 检查以下几点：

1. 是否安装了 `langchain` 和 `langchain-openai`
2. 是否在管理后台配置了 API 密钥
3. API 密钥是否有效
4. 网络连接是否正常

### Q: 如何使用本地 LLM 模型？

A: 可以使用 Ollama 等本地模型，需要：

1. 安装 Ollama：https://ollama.ai/
2. 安装对应的 LangChain 集成：`pip install langchain-community`
3. 修改 `services.py` 中的 LLM 初始化代码

## 📝 更新日志

### v1.0 (2025-10-21)

- ✨ 初始版本发布
- 🔐 实现用户注册、登录、登出功能
- 🤖 集成 LangChain LLM 服务
- 📝 实现聊天历史记录功能
- 🎨 创建美观的用户界面

## 📄 许可证

本项目仅供学习使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件

---

**祝您使用愉快！如果这个项目对您有帮助，请给它一个 Star ⭐️**
