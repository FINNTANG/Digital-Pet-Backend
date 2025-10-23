"""
用户账户相关的视图函数

视图函数的作用是：
1. 接收用户的HTTP请求（request）
2. 处理业务逻辑（比如保存数据到数据库）
3. 返回HTTP响应（通常是渲染的HTML页面）
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm


def register_view(request):
    """
    用户注册视图
    
    功能说明：
    - GET请求：显示空的注册表单
    - POST请求：处理提交的注册数据，创建新用户
    """
    
    # 检查请求方法
    if request.method == 'POST':
        # 用户提交了表单，使用POST数据创建表单实例
        form = UserRegisterForm(request.POST)
        
        # 验证表单数据是否有效
        if form.is_valid():
            # 保存新用户到数据库
            user = form.save()
            
            # 获取用户名用于显示欢迎消息
            username = form.cleaned_data.get('username')
            
            # 显示成功消息
            messages.success(request, f'账号创建成功！欢迎 {username}！')
            
            # 自动登录新注册的用户
            login(request, user)
            
            # 重定向到首页
            return redirect('home')
    else:
        # GET请求，创建空表单
        form = UserRegisterForm()
    
    # 渲染注册页面，传入表单对象
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    用户登录视图
    
    功能说明：
    - 验证用户名和密码
    - 登录成功后跳转到首页或之前访问的页面
    """
    
    # 如果用户已经登录，直接跳转到首页
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        
        if form.is_valid():
            # 获取用户输入的用户名和密码
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # 使用Django的authenticate函数验证用户
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # 验证成功，登录用户
                login(request, user)
                messages.success(request, f'欢迎回来，{username}！')
                
                # 获取用户登录前想要访问的页面（如果有的话）
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect('home')
            else:
                # 验证失败，显示错误消息
                messages.error(request, '用户名或密码错误')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required  # 这个装饰器确保只有登录用户才能访问
def logout_view(request):
    """
    用户登出视图
    
    功能说明：
    - 清除用户的登录状态
    - 跳转到登录页面
    """
    
    # 执行登出操作
    logout(request)
    messages.info(request, '您已成功登出')
    
    # 跳转到登录页面
    return redirect('login')


@login_required  # 只有登录用户才能查看个人中心
def profile_view(request):
    """
    个人中心视图
    
    功能说明：
    - 显示当前登录用户的基本信息
    """
    
    # request.user 是当前登录的用户对象
    return render(request, 'accounts/profile.html', {'user': request.user})


def home_view(request):
    """
    首页视图
    
    显示项目的主页面
    """
    return render(request, 'accounts/home.html')
