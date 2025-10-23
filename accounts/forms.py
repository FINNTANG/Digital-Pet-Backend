"""
用户账户相关的表单定义

这个文件包含了用户注册和登录需要的表单。
Django的表单系统可以帮助我们验证用户输入，确保数据的正确性。
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    """
    用户注册表单
    
    继承自Django内置的UserCreationForm，这样可以自动获得：
    - 密码强度验证
    - 密码确认功能
    - 用户名重复检查
    """
    
    # 额外添加邮箱字段（必填）
    email = forms.EmailField(
        label='邮箱地址',
        required=True,
        help_text='请输入有效的邮箱地址'
    )
    
    class Meta:
        """
        Meta类用于配置表单的基本信息
        """
        model = User  # 使用Django内置的User模型
        fields = ['username', 'email', 'password1', 'password2']  # 表单包含的字段
        labels = {
            'username': '用户名',
            'password1': '密码',
            'password2': '确认密码',
        }
        help_texts = {
            'username': '150个字符以内，只能包含字母、数字和@/./+/-/_符号',
        }
    
    def clean_email(self):
        """
        验证邮箱是否已被注册
        
        这个方法会在表单验证时自动调用。
        如果邮箱已存在，会抛出验证错误。
        """
        email = self.cleaned_data.get('email')
        
        # 检查邮箱是否已经被其他用户使用
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        
        return email


class UserLoginForm(forms.Form):
    """
    用户登录表单
    
    这是一个简单的登录表单，只需要用户名和密码。
    """
    
    username = forms.CharField(
        label='用户名',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': '请输入用户名'
        })
    )
    
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'placeholder': '请输入密码'
        })
    )


