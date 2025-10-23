# 项目宪章 - Django用户管理与LLM服务

## 项目概述
本项目是一个基于Django 5.2的Web应用，提供用户管理和LLM（大语言模型）服务功能。

## 核心原则

### 1. 代码风格 - 对新手友好
- **清晰的命名**：使用有意义的变量名和函数名，避免缩写
- **详细的注释**：每个函数和类都有中文注释，说明其作用
- **简单的结构**：避免过度抽象，优先使用直观的代码组织方式
- **逐步引导**：代码中包含学习提示，帮助理解Django概念

### 2. 项目结构
```
django/
├── mysite/              # 项目配置目录
│   ├── settings.py      # 全局配置
│   ├── urls.py          # 主URL路由
│   └── wsgi.py          # WSGI配置
├── accounts/            # 用户管理应用
│   ├── models.py        # 数据模型
│   ├── views.py         # 视图函数
│   ├── urls.py          # URL路由
│   ├── forms.py         # 表单定义
│   └── templates/       # HTML模板
├── llm_service/         # LLM服务应用
│   ├── models.py        # 聊天记录等模型
│   ├── views.py         # LLM服务视图
│   ├── urls.py          # URL路由
│   ├── services.py      # LLM业务逻辑
│   └── templates/       # HTML模板
└── requirements.txt     # 项目依赖
```

### 3. 功能规范

#### 用户管理（accounts应用）
- **用户注册**：简单的注册表单，包含用户名、邮箱、密码
- **用户登录**：基于Django内置认证系统
- **用户登出**：一键登出功能
- **个人中心**：查看和编辑用户信息

#### LLM服务（llm_service应用）
- **聊天界面**：简洁的对话界面
- **对话历史**：保存用户的对话记录
- **流式输出**：支持流式响应（可选）
- **模型配置**：可配置不同的LLM提供商

### 4. 技术栈
- **后端框架**：Django 5.2
- **数据库**：SQLite（开发环境）
- **LLM框架**：LangChain
- **前端**：Django模板 + 基础CSS（Bootstrap可选）
- **Python版本**：3.8+

### 5. 代码规范

#### 命名约定
- **变量名**：使用小写字母和下划线，如 `user_name`
- **函数名**：使用动词开头，如 `get_user_info()`
- **类名**：使用驼峰命名，如 `ChatMessage`
- **常量**：使用大写字母，如 `MAX_MESSAGE_LENGTH`

#### 注释规范
```python
# 函数注释示例
def register_user(username, email, password):
    """
    注册新用户
    
    参数:
        username (str): 用户名
        email (str): 邮箱地址
        password (str): 密码
        
    返回:
        User: 创建的用户对象
        
    说明:
        这个函数会创建一个新用户并保存到数据库。
        密码会自动加密存储，保证安全性。
    """
    # 实现代码...
```

#### 视图函数规范
```python
# 简单清晰的视图函数
def home(request):
    """主页视图"""
    # 1. 获取数据
    # 2. 处理逻辑
    # 3. 返回响应
    return render(request, 'home.html', context)
```

### 6. 安全规范
- 密码使用Django内置的加密机制
- 使用CSRF保护
- 环境变量存储敏感信息（API密钥等）
- 登录状态检查使用装饰器

### 7. 开发流程
1. 先实现核心功能，再优化
2. 每个功能独立测试
3. 保持代码简单，避免过早优化
4. 及时添加注释和文档

### 8. 学习资源
- Django官方文档：https://docs.djangoproject.com/
- LangChain文档：https://python.langchain.com/
- Python基础教程：https://docs.python.org/zh-cn/3/tutorial/

## 版本历史
- v1.0 (2025-10-21): 初始版本，定义项目基本规范


