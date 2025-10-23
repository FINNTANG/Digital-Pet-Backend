"""
用户账户相关的数据模型

这个文件定义了用户扩展信息和相关功能的数据模型。
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import uuid


class UserProfile(models.Model):
    """
    用户扩展信息模型
    
    Django的User模型只包含基本字段（用户名、邮箱、密码等）。
    这个模型用于存储额外的用户信息，通过一对一关系与User关联。
    
    设计理念：
    - 使用OneToOneField关联User，不修改Django内置模型
    - 包含常用的扩展字段（手机、头像、简介等）
    - 记录验证状态和统计信息
    """
    
    # === 关联关系 ===
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # 删除User时同时删除Profile
        related_name='profile',  # 反向查询名称：user.profile
        verbose_name='关联用户',
        help_text='关联到Django内置的User模型'
    )
    
    # === 联系方式 ===
    phone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        unique=True,  # 手机号唯一
        verbose_name='手机号',
        help_text='11位手机号码'
    )
    
    # === 个人信息 ===
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',  # 按年月分目录存储：avatars/2025/10/
        blank=True,
        null=True,
        verbose_name='头像',
        help_text='用户头像图片'
    )
    
    bio = models.TextField(
        blank=True,
        max_length=500,
        verbose_name='个人简介',
        help_text='个人简介，最多500字符'
    )
    
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='出生日期'
    )
    
    # 性别选项
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    ]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        verbose_name='性别'
    )
    
    # === 验证状态 ===
    email_verified = models.BooleanField(
        default=False,
        verbose_name='邮箱已验证',
        help_text='邮箱是否已通过验证'
    )
    
    phone_verified = models.BooleanField(
        default=False,
        verbose_name='手机已验证',
        help_text='手机号是否已通过验证'
    )
    
    # === 统计信息 ===
    login_count = models.IntegerField(
        default=0,
        verbose_name='登录次数',
        help_text='用户累计登录次数'
    )
    
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='最后登录IP',
        help_text='用户最后一次登录的IP地址'
    )
    
    # === 时间戳 ===
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        help_text='记录创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
        help_text='记录最后更新时间'
    )
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
        ordering = ['-created_at']  # 默认按创建时间倒序
        
        # 数据库索引优化
        indexes = [
            models.Index(fields=['phone']),  # 手机号索引（用于查询）
            models.Index(fields=['-created_at']),  # 创建时间索引
        ]
    
    def __str__(self):
        """字符串表示"""
        return f"{self.user.username}的资料"
    
    def increment_login_count(self):
        """
        增加登录计数
        
        每次用户登录时调用这个方法。
        使用update_fields优化，只更新login_count字段。
        """
        self.login_count += 1
        self.save(update_fields=['login_count'])
    
    def get_avatar_url(self):
        """
        获取头像URL
        
        返回头像的URL，如果没有头像则返回默认头像。
        """
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'  # 默认头像
    
    @property
    def age(self):
        """
        计算年龄
        
        根据出生日期计算年龄。
        使用@property装饰器，可以像访问属性一样调用：user.profile.age
        """
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None


class EmailVerification(models.Model):
    """
    邮箱验证令牌模型
    
    用于存储邮箱验证的临时令牌。
    
    工作流程：
    1. 用户注册后，系统生成一个唯一的验证令牌
    2. 将令牌发送到用户邮箱
    3. 用户点击邮件中的链接，携带令牌访问验证接口
    4. 系统验证令牌有效性，标记邮箱为已验证
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='用户',
        help_text='验证令牌所属的用户'
    )
    
    token = models.UUIDField(
        default=uuid.uuid4,  # 自动生成UUID
        unique=True,  # 令牌唯一
        editable=False,  # 不可编辑
        verbose_name='验证令牌',
        help_text='唯一的验证令牌'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    expires_at = models.DateTimeField(
        verbose_name='过期时间',
        help_text='令牌过期时间'
    )
    
    is_used = models.BooleanField(
        default=False,
        verbose_name='已使用',
        help_text='令牌是否已被使用'
    )
    
    class Meta:
        verbose_name = '邮箱验证'
        verbose_name_plural = '邮箱验证记录'
        ordering = ['-created_at']
        
        # 索引优化
        indexes = [
            models.Index(fields=['token']),  # 令牌索引（用于验证）
            models.Index(fields=['user', '-created_at']),  # 用户+时间索引
        ]
    
    def __str__(self):
        return f"{self.user.username}的邮箱验证 ({self.token})"
    
    def save(self, *args, **kwargs):
        """
        重写save方法，自动设置过期时间
        
        如果没有设置expires_at，自动设置为24小时后过期。
        """
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """
        检查令牌是否有效
        
        令牌有效的条件：
        1. 未被使用
        2. 未过期
        
        返回:
            bool: True表示令牌有效，False表示无效
        """
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """
        标记令牌为已使用
        
        验证成功后调用此方法。
        """
        self.is_used = True
        self.save(update_fields=['is_used'])


# ========== 信号处理器 ==========

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    信号处理器：创建User时自动创建UserProfile
    
    Django的信号机制：
    - post_save: 在模型保存后触发
    - sender=User: 只监听User模型
    - created=True: 只在创建时执行（更新时不执行）
    
    好处：
    - 无需手动创建UserProfile
    - 保证每个User都有对应的Profile
    - 代码解耦，维护方便
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    信号处理器：保存User时同时保存UserProfile
    
    确保User和UserProfile数据同步。
    """
    # 检查是否有profile（防止新创建的User还没有profile）
    if hasattr(instance, 'profile'):
        instance.profile.save()
