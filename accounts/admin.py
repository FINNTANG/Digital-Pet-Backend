"""
用户账户的Django Admin管理界面配置

这个文件定义了如何在Django管理后台显示和管理用户相关数据。
包含详细的列表展示、过滤器、搜索、批量操作等功能。
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, EmailVerification
import csv
from django.http import HttpResponse


# ========== 内联管理器 ==========

class UserProfileInline(admin.StackedInline):
    """
    UserProfile内联管理器
    
    在User的编辑页面中，内联显示UserProfile信息。
    这样可以在一个页面同时编辑User和Profile。
    """
    model = UserProfile
    can_delete = False  # 不允许删除Profile
    verbose_name = '用户资料'
    verbose_name_plural = '用户资料'
    
    fields = [
        'phone', 'avatar', 'avatar_preview',
        'bio', 'birth_date', 'gender',
        'email_verified', 'phone_verified',
        'login_count', 'last_login_ip'
    ]
    
    readonly_fields = ['avatar_preview', 'login_count', 'last_login_ip']
    
    def avatar_preview(self, obj):
        """
        头像预览
        
        在管理界面显示头像的缩略图。
        """
        if obj.avatar:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url
            )
        return '未上传头像'
    avatar_preview.short_description = '头像预览'


# ========== 用户管理器 ==========

class UserAdmin(BaseUserAdmin):
    """
    增强的用户管理界面
    
    功能特色：
    - 丰富的列表展示（头像、状态、登录信息）
    - 强大的过滤和搜索
    - 实用的批量操作
    - 数据导出功能
    """
    
    # ===== 列表页配置 =====
    
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
        'profile__email_verified',
        'profile__gender',
    ]
    
    # 搜索字段
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'profile__phone'
    ]
    
    # 默认排序
    ordering = ['-date_joined']
    
    # 每页显示数量
    list_per_page = 25
    
    # ===== 详情页配置 =====
    
    inlines = [UserProfileInline]
    
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
            'classes': ('collapse',)
        }),
        ('重要日期', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    # ===== 自定义列显示 =====
    
    def username_display(self, obj):
        """用户名显示（带头像）"""
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return format_html(
                '<div style="display: flex; align-items: center;">'
                '<img src="{}" width="30" height="30" '
                'style="border-radius: 50%; margin-right: 10px; object-fit: cover;" />'
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
            color = '#e74c3c'
            text = '超级管理员'
        elif obj.is_staff:
            color = '#3498db'
            text = '管理员'
        elif obj.is_active:
            color = '#2ecc71'
            text = '正常'
        else:
            color = '#95a5a6'
            text = '已禁用'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 12px; font-weight: bold;">{}</span>',
            color,
            text
        )
    status_display.short_description = '状态'
    
    def email_verified_display(self, obj):
        """邮箱验证状态"""
        if hasattr(obj, 'profile'):
            if obj.profile.email_verified:
                return format_html('<span style="color: green; font-size: 16px;">✅</span>')
            else:
                return format_html('<span style="color: red; font-size: 16px;">❌</span>')
        return '-'
    email_verified_display.short_description = '邮箱验证'
    
    def login_info(self, obj):
        """登录信息"""
        if hasattr(obj, 'profile'):
            count = obj.profile.login_count
            last_ip = obj.profile.last_login_ip or '未知'
            
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
        detail_url = reverse('admin:auth_user_change', args=[obj.pk])
        return format_html(
            '<a href="{}" title="编辑">📝</a>',
            detail_url
        )
    quick_actions.short_description = '操作'
    
    # ===== 批量操作 =====
    
    actions = [
        'activate_users',
        'deactivate_users',
        'export_as_csv',
        'export_as_excel'
    ]
    
    def activate_users(self, request, queryset):
        """批量激活用户"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个用户', level='success')
    activate_users.short_description = '✅ 激活选中的用户'
    
    def deactivate_users(self, request, queryset):
        """批量禁用用户"""
        superusers = queryset.filter(is_superuser=True)
        if superusers.exists():
            self.message_user(request, '不能禁用超级管理员！', level='error')
            return
        
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功禁用 {updated} 个用户', level='warning')
    deactivate_users.short_description = '❌ 禁用选中的用户'
    
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
        """导出为Excel"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment
            
            wb = Workbook()
            ws = wb.active
            ws.title = '用户列表'
            
            headers = ['ID', '用户名', '邮箱', '手机号', '注册时间', '登录次数', '状态']
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')
            
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
            
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="users.xlsx"'
            wb.save(response)
            
            return response
        
        except ImportError:
            self.message_user(request, '请先安装openpyxl: pip install openpyxl', level='error')
    export_as_excel.short_description = '📊 导出为Excel'
    
    # ===== 查询优化 =====
    
    def get_queryset(self, request):
        """优化查询，使用select_related减少数据库查询"""
        qs = super().get_queryset(request)
        return qs.select_related('profile')
    
    def has_delete_permission(self, request, obj=None):
        """禁止删除超级管理员"""
        if obj and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)


# ========== 用户资料管理器 ==========

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户资料管理界面"""
    
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


# ========== 邮箱验证管理器 ==========

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """邮箱验证管理界面"""
    
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

# 取消默认的User注册，使用我们自定义的UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 修改Admin站点标题
admin.site.site_header = 'Django用户管理系统'
admin.site.site_title = '管理后台'
admin.site.index_title = '欢迎使用管理后台'
