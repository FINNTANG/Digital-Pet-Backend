#!/usr/bin/env python
"""
项目初始化脚本

这个脚本会帮助您快速设置项目：
1. 安装依赖
2. 运行数据库迁移
3. 创建超级用户
4. 启动开发服务器
"""

import os
import sys
import subprocess


def run_command(command, description):
    """运行命令并显示进度"""
    print(f"\n{'='*60}")
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    print('='*60)
    
    result = subprocess.run(command, shell=True)
    
    if result.returncode != 0:
        print(f"\n❌ 错误: {description} 失败")
        return False
    else:
        print(f"\n✅ 成功: {description} 完成")
        return True


def main():
    """主函数"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       Django用户管理与LLM服务 - 项目初始化脚本           ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: Python {sys.version}")
        return
    
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    
    # 步骤1: 安装依赖
    print("\n" + "="*60)
    choice = input("是否安装项目依赖？(y/n): ").lower()
    if choice == 'y':
        if not run_command("pip install -r requirements.txt", "安装项目依赖"):
            return
    else:
        print("⏭️ 跳过依赖安装")
    
    # 步骤2: 数据库迁移
    print("\n" + "="*60)
    print("准备执行数据库迁移...")
    
    if not run_command("python manage.py makemigrations", "创建迁移文件"):
        return
    
    if not run_command("python manage.py migrate", "应用数据库迁移"):
        return
    
    # 步骤3: 创建超级用户
    print("\n" + "="*60)
    choice = input("是否创建超级用户账号（用于访问管理后台）？(y/n): ").lower()
    if choice == 'y':
        print("\n请按提示输入超级用户信息：")
        run_command("python manage.py createsuperuser", "创建超级用户")
    else:
        print("⏭️ 跳过创建超级用户（可以稍后使用 'python manage.py createsuperuser' 创建）")
    
    # 完成
    print("\n" + "="*60)
    print("""
    ✨ 初始化完成！
    
    接下来您可以：
    
    1. 启动开发服务器：
       python manage.py runserver
    
    2. 在浏览器中访问：
       - 主页: http://127.0.0.1:8000/
       - 管理后台: http://127.0.0.1:8000/admin/
    
    3. 使用功能：
       - 注册新账号
       - 登录系统
       - 使用AI聊天功能
    
    4. 配置LLM服务（可选）：
       - 在管理后台添加LLM配置
       - 详见README.md文档
    
    📖 更多信息请查看 README.md 文件
    """)
    
    print("="*60)
    choice = input("\n是否立即启动开发服务器？(y/n): ").lower()
    if choice == 'y':
        print("\n启动服务器中... (按 Ctrl+C 停止)")
        run_command("python manage.py runserver", "启动开发服务器")
    else:
        print("\n再见！您可以随时使用 'python manage.py runserver' 启动服务器")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 操作被用户取消")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {str(e)}")


