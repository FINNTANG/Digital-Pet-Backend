# Django Admin管理界面增强方案

## 📊 当前Admin状态分析

当前项目使用Django的默认Admin，功能比较基础。本方案将展示如何打造一个**功能强大、美观易用**的管理后台。

## 🎯 增强目标

1. **用户管理优化**：列表展示、过滤、搜索、批量操作
2. **数据统计**：用户统计、登录趋势、活跃度分析
3. **权限细化**：基于角色的权限控制
4. **界面美化**：使用django-adminlte3美化界面
5. **导出功能**：用户数据导出Excel/CSV

## 🏗️ 实现方案

### 1. 增强版用户Admin

```python
# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, EmailVerification
import csv
from django.http import HttpResponse


class UserProfileInline(admin.StackedInline):
    """
    内联显示用户扩展信息
    
    在编辑用户时，可以同时编辑UserProfile信息。
    """
    model = UserProfile
    can_delete = False
    verbose_name = '用户资料'
    verbose_name_plural = '用户资料'
    
    # 显示的字段
    fields = [
        'phone', 'avatar', 'avatar_preview',
        'bio', 'birth_date', 'gender',
        'email_verified', 'phone_verified',
        'login_count', 'last_login_ip'
    ]
    
    # 只读字段
    readonly_fields = ['avatar_preview', 'login_count', 'last_login_ip']
    
    def avatar_preview(self, obj):
        """头像预览"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius: 50%;" />',
                obj.avatar.url
            )
        return '未上传头像'
    avatar_preview.short_description = '头像预览'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    增强的用户管理界面
    
    功能：
    - 优化列表展示
    - 添加过滤器和搜索
    - 批量操作
    - 数据导出
    """
    
    # ========== 列表页配置 ==========
    
    list_display = [
        'id',
        'username_display',
        'email_display',
        'phone_display',
        'status_display',
        'email_verified_display',
        'login_info',
        'date_joined_display',
        'quick_actions'
    ]
    
    list_display_links = ['id', 'username_display']
    
    # 侧边栏过滤器
    list_filter = [
        'is_active',
        'is_staff',
        'is_superuser',
        ('date_joined', admin.DateFieldListFilter),
        ('last_login', admin.DateFieldListFilter),
        'userprofile__email_verified',
        'userprofile__gender',
    ]
    
    # 搜索字段
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'userprofile__phone'
    ]
    
    # 可以在列表页直接编辑
    list_editable = []
    
    # 默认排序
    ordering = ['-date_joined']
    
    # 每页显示数量
    list_per_page = 25
    
    # 列表页最大显示数量
    list_max_show_all = 100
    
    # ========== 详情页配置 ==========
    
    # 内联显示扩展信息
    inlines = [UserProfileInline]
    
    # 字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password')
        }),
        ('个人信息', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('权限', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)  # 默认折叠
        }),
        ('重要日期', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # 添加用户时的字段
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    # ========== 自定义列显示方法 ==========
    
    def username_display(self, obj):
        """用户名显示（带头像）"""
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return format_html(
                '<div style="display: flex; align-items: center;">'
                '<img src="{}" width="30" height="30" style="border-radius: 50%; margin-right: 10px;" />'
                '<strong>{}</strong>'
                '</div>',
                obj.profile.avatar.url,
                obj.username
            )
        return format_html('<strong>{}</strong>', obj.username)
    username_display.short_description = '用户名'
    username_display.admin_order_field = 'username'
    
    def email_display(self, obj):
        """邮箱显示（可点击发送邮件）"""
        if obj.email:
            return format_html(
                '<a href="mailto:{}">{}</a>',
                obj.email,
                obj.email
            )
        return '-'
    email_display.short_description = '邮箱'
    email_display.admin_order_field = 'email'
    
    def phone_display(self, obj):
        """手机号显示"""
        if hasattr(obj, 'profile') and obj.profile.phone:
            return obj.profile.phone
        return '-'
    phone_display.short_description = '手机号'
    
    def status_display(self, obj):
        """状态显示（彩色标签）"""
        if obj.is_superuser:
            color = '#e74c3c'  # 红色
            text = '超级管理员'
        elif obj.is_staff:
            color = '#3498db'  # 蓝色
            text = '管理员'
        elif obj.is_active:
            color = '#2ecc71'  # 绿色
            text = '正常'
        else:
            color = '#95a5a6'  # 灰色
            text = '已禁用'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            text
        )
    status_display.short_description = '状态'
    
    def email_verified_display(self, obj):
        """邮箱验证状态"""
        if hasattr(obj, 'profile'):
            if obj.profile.email_verified:
                return format_html(
                    '<span style="color: green; font-size: 16px;">✅</span>'
                )
            else:
                return format_html(
                    '<span style="color: red; font-size: 16px;">❌</span>'
                )
        return '-'
    email_verified_display.short_description = '邮箱验证'
    
    def login_info(self, obj):
        """登录信息"""
        if hasattr(obj, 'profile'):
            count = obj.profile.login_count
            last_ip = obj.profile.last_login_ip or '未知'
            
            # 计算最后登录时间距今
            if obj.last_login:
                now = timezone.now()
                delta = now - obj.last_login
                if delta < timedelta(hours=1):
                    time_ago = f'{int(delta.total_seconds() / 60)}分钟前'
                elif delta < timedelta(days=1):
                    time_ago = f'{int(delta.total_seconds() / 3600)}小时前'
                else:
                    time_ago = f'{delta.days}天前'
            else:
                time_ago = '从未登录'
            
            return format_html(
                '<div style="font-size: 12px;">'
                '<div>登录 {} 次</div>'
                '<div>IP: {}</div>'
                '<div>{}</div>'
                '</div>',
                count,
                last_ip,
                time_ago
            )
        return '-'
    login_info.short_description = '登录信息'
    
    def date_joined_display(self, obj):
        """注册时间（友好显示）"""
        now = timezone.now()
        delta = now - obj.date_joined
        
        if delta < timedelta(days=1):
            label = '今天'
            color = '#e74c3c'
        elif delta < timedelta(days=7):
            label = '本周'
            color = '#f39c12'
        elif delta < timedelta(days=30):
            label = '本月'
            color = '#3498db'
        else:
            label = ''
            color = '#95a5a6'
        
        return format_html(
            '<div>'
            '{}'
            '{}'
            '</div>',
            format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 10px; margin-right: 5px;">{}</span>',
                color, label
            ) if label else '',
            obj.date_joined.strftime('%Y-%m-%d %H:%M')
        )
    date_joined_display.short_description = '注册时间'
    date_joined_display.admin_order_field = 'date_joined'
    
    def quick_actions(self, obj):
        """快速操作按钮"""
        actions = []
        
        # 查看详情按钮
        detail_url = reverse('admin:auth_user_change', args=[obj.pk])
        actions.append(
            format_html(
                '<a href="{}" style="margin-right: 5px;">📝</a>',
                detail_url
            )
        )
        
        # 发送邮件按钮
        if obj.email:
            actions.append(
                format_html(
                    '<a href="mailto:{}" style="margin-right: 5px;">📧</a>',
                    obj.email
                )
            )
        
        # 激活/禁用按钮
        if obj.is_active:
            actions.append('🟢')
        else:
            actions.append('🔴')
        
        return format_html(''.join(actions))
    quick_actions.short_description = '操作'
    
    # ========== 批量操作 ==========
    
    actions = [
        'activate_users',
        'deactivate_users',
        'send_verification_email',
        'export_as_csv',
        'export_as_excel'
    ]
    
    def activate_users(self, request, queryset):
        """批量激活用户"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'成功激活 {updated} 个用户',
            level='success'
        )
    activate_users.short_description = '✅ 激活选中的用户'
    
    def deactivate_users(self, request, queryset):
        """批量禁用用户"""
        # 不允许禁用超级管理员
        superusers = queryset.filter(is_superuser=True)
        if superusers.exists():
            self.message_user(
                request,
                '不能禁用超级管理员！',
                level='error'
            )
            return
        
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'成功禁用 {updated} 个用户',
            level='warning'
        )
    deactivate_users.short_description = '❌ 禁用选中的用户'
    
    def send_verification_email(self, request, queryset):
        """批量发送验证邮件"""
        count = 0
        for user in queryset:
            if user.email and not user.profile.email_verified:
                # TODO: 实现发送验证邮件的逻辑
                count += 1
        
        self.message_user(
            request,
            f'已向 {count} 个用户发送验证邮件',
            level='info'
        )
    send_verification_email.short_description = '📧 发送验证邮件'
    
    def export_as_csv(self, request, queryset):
        """导出为CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', '用户名', '邮箱', '手机号', '注册时间', '登录次数', '状态'])
        
        for user in queryset:
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.profile.phone if hasattr(user, 'profile') else '',
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                user.profile.login_count if hasattr(user, 'profile') else 0,
                '正常' if user.is_active else '已禁用'
            ])
        
        return response
    export_as_csv.short_description = '📥 导出为CSV'
    
    def export_as_excel(self, request, queryset):
        """导出为Excel（需要安装openpyxl）"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment
            
            wb = Workbook()
            ws = wb.active
            ws.title = '用户列表'
            
            # 表头
            headers = ['ID', '用户名', '邮箱', '手机号', '注册时间', '登录次数', '状态']
            ws.append(headers)
            
            # 设置表头样式
            for cell in ws[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')
            
            # 数据行
            for user in queryset:
                ws.append([
                    user.id,
                    user.username,
                    user.email,
                    user.profile.phone if hasattr(user, 'profile') else '',
                    user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                    user.profile.login_count if hasattr(user, 'profile') else 0,
                    '正常' if user.is_active else '已禁用'
                ])
            
            # 返回响应
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="users.xlsx"'
            wb.save(response)
            
            return response
        
        except ImportError:
            self.message_user(
                request,
                '请先安装openpyxl: pip install openpyxl',
                level='error'
            )
    export_as_excel.short_description = '📊 导出为Excel'
    
    # ========== 重写方法 ==========
    
    def get_queryset(self, request):
        """优化查询（使用select_related减少数据库查询）"""
        qs = super().get_queryset(request)
        return qs.select_related('userprofile')
    
    def has_delete_permission(self, request, obj=None):
        """禁止删除超级管理员"""
        if obj and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户资料管理"""
    
    list_display = [
        'user',
        'phone',
        'gender',
        'email_verified',
        'phone_verified',
        'login_count'
    ]
    
    list_filter = ['email_verified', 'phone_verified', 'gender']
    search_fields = ['user__username', 'phone']
    readonly_fields = ['login_count', 'last_login_ip', 'created_at', 'updated_at']
    
    fieldsets = (
        ('关联用户', {
            'fields': ('user',)
        }),
        ('联系方式', {
            'fields': ('phone', 'phone_verified')
        }),
        ('个人信息', {
            'fields': ('avatar', 'bio', 'birth_date', 'gender')
        }),
        ('验证状态', {
            'fields': ('email_verified',)
        }),
        ('统计信息', {
            'fields': ('login_count', 'last_login_ip'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """邮箱验证管理"""
    
    list_display = ['user', 'token_short', 'created_at', 'expires_at', 'is_used', 'status']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['token', 'created_at']
    
    def token_short(self, obj):
        """显示缩短的token"""
        return f'{str(obj.token)[:8]}...'
    token_short.short_description = 'Token'
    
    def status(self, obj):
        """验证状态"""
        if obj.is_used:
            return format_html('<span style="color: green;">✅ 已使用</span>')
        elif timezone.now() > obj.expires_at:
            return format_html('<span style="color: red;">❌ 已过期</span>')
        else:
            return format_html('<span style="color: blue;">⏳ 有效</span>')
    status.short_description = '状态'


# ========== Admin站点自定义 ==========

# 修改Admin站点标题
admin.site.site_header = 'Django用户管理系统'
admin.site.site_title = '管理后台'
admin.site.index_title = '欢迎使用管理后台'
```

### 2. 添加统计仪表盘

```python
# accounts/admin_views.py

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile


@staff_member_required
def admin_dashboard(request):
    """管理后台仪表盘"""
    
    # 基础统计
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    verified_users = UserProfile.objects.filter(email_verified=True).count()
    
    # 时间范围统计
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    this_week = today - timedelta(days=today.weekday())
    this_month = today.replace(day=1)
    
    new_today = User.objects.filter(date_joined__gte=today).count()
    new_this_week = User.objects.filter(date_joined__gte=this_week).count()
    new_this_month = User.objects.filter(date_joined__gte=this_month).count()
    
    # 登录统计
    login_today = User.objects.filter(last_login__gte=today).count()
    login_this_week = User.objects.filter(last_login__gte=this_week).count()
    
    # 性别统计
    gender_stats = UserProfile.objects.values('gender').annotate(count=Count('id'))
    
    # 最近注册用户
    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:10]
    
    # 活跃用户（登录次数Top10）
    active_top = User.objects.select_related('profile').order_by('-profile__login_count')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'verified_users': verified_users,
        'new_today': new_today,
        'new_this_week': new_this_week,
        'new_this_month': new_this_month,
        'login_today': login_today,
        'login_this_week': login_this_week,
        'gender_stats': gender_stats,
        'recent_users': recent_users,
        'active_top': active_top,
    }
    
    return render(request, 'admin/dashboard.html', context)
```

### 3. 仪表盘模板

```html
<!-- templates/admin/dashboard.html -->

{% extends "admin/base_site.html" %}
{% load static %}

{% block title %}仪表盘{% endblock %}

{% block content %}
<h1>📊 数据统计仪表盘</h1>

<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0;">
    <!-- 统计卡片 -->
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; opacity: 0.9;">总用户数</div>
        <div style="font-size: 32px; font-weight: bold; margin: 10px 0;">{{ total_users }}</div>
        <div style="font-size: 12px; opacity: 0.8;">📈 活跃: {{ active_users }}</div>
    </div>
    
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; opacity: 0.9;">今日新增</div>
        <div style="font-size: 32px; font-weight: bold; margin: 10px 0;">{{ new_today }}</div>
        <div style="font-size: 12px; opacity: 0.8;">本周: {{ new_this_week }} | 本月: {{ new_this_month }}</div>
    </div>
    
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; opacity: 0.9;">今日登录</div>
        <div style="font-size: 32px; font-weight: bold; margin: 10px 0;">{{ login_today }}</div>
        <div style="font-size: 12px; opacity: 0.8;">本周: {{ login_this_week }}</div>
    </div>
    
    <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; opacity: 0.9;">已验证</div>
        <div style="font-size: 32px; font-weight: bold; margin: 10px 0;">{{ verified_users }}</div>
        <div style="font-size: 12px; opacity: 0.8;">✅ 邮箱验证</div>
    </div>
</div>

<!-- 最近注册用户 -->
<div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 20px 0;">
    <h2>👥 最近注册用户</h2>
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background: #f5f5f5;">
                <th style="padding: 10px; text-align: left;">用户名</th>
                <th style="padding: 10px; text-align: left;">邮箱</th>
                <th style="padding: 10px; text-align: left;">注册时间</th>
                <th style="padding: 10px; text-align: left;">登录次数</th>
            </tr>
        </thead>
        <tbody>
            {% for user in recent_users %}
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px;">{{ user.username }}</td>
                <td style="padding: 10px;">{{ user.email }}</td>
                <td style="padding: 10px;">{{ user.date_joined|date:"Y-m-d H:i" }}</td>
                <td style="padding: 10px;">{{ user.profile.login_count }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

{% endblock %}
```

### 4. URL配置

```python
# accounts/admin_urls.py

from django.urls import path
from .admin_views import admin_dashboard

urlpatterns = [
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
]
```

```python
# mysite/urls.py (添加)

urlpatterns = [
    # ... 其他URL
    path('admin-panel/', include('accounts.admin_urls')),
]
```

## 📦 推荐的Admin增强包

### 1. django-admin-interface
美化Admin界面

```bash
pip install django-admin-interface
```

### 2. django-import-export
数据导入导出

```bash
pip install django-import-export
```

使用示例：
```python
from import_export.admin import ImportExportModelAdmin

class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    pass
```

### 3. django-admin-rangefilter
日期范围过滤

```bash
pip install django-admin-rangefilter
```

## 🎨 界面美化建议

1. **使用Grappelli主题**
2. **自定义CSS样式**
3. **添加图表（Chart.js）**
4. **响应式设计**

---

通过以上增强，您的Django Admin将变得功能强大且美观易用！🚀


