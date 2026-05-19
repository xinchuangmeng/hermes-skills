#!/usr/bin/env python3
"""
环境检查脚本
用于检查学习AI智能体所需的基础环境
"""

import subprocess
import sys

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def check_python():
    """检查Python安装"""
    print("🔍 检查Python安装...")
    success, output = run_command("python3 --version")
    if success:
        print(f"  ✅ Python版本: {output}")
        return True
    else:
        print("  ❌ Python未安装或不在PATH中")
        return False

def check_git():
    """检查Git安装"""
    print("🔍 检查Git安装...")
    success, output = run_command("git --version")
    if success:
        print(f"  ✅ Git版本: {output}")
        return True
    else:
        print("  ❌ Git未安装或不在PATH中")
        return False

def check_editor():
    """检查可用编辑器"""
    print("🔍 检查可用编辑器...")
    editors = ["code", "nano", "vim", "emacs"]
    available = []
    
    for editor in editors:
        success, _ = run_command(f"which {editor}")
        if success:
            available.append(editor)
    
    if available:
        print(f"  ✅ 可用编辑器: {', '.join(available)}")
        return True, available[0]  # 返回第一个可用的编辑器
    else:
        print("  ⚠️  未找到常用编辑器，建议安装VS Code或使用在线编辑器")
        return False, None

def create_learning_dir():
    """创建学习目录"""
    print("📁 创建学习目录...")
    import os
    home_dir = os.path.expanduser("~")
    learning_dir = os.path.join(home_dir, "ai-agent-learning", "day1")
    
    try:
        os.makedirs(learning_dir, exist_ok=True)
        print(f"  ✅ 学习目录已创建: {learning_dir}")
        return True, learning_dir
    except Exception as e:
        print(f"  ❌ 创建目录失败: {e}")
        return False, None

def main():
    print("="*50)
    print("AI智能体学习 - 环境检查")
    print("="*50)
    
    # 检查各项
    python_ok = check_python()
    git_ok = check_git()
    editor_ok, recommended_editor = check_editor()
    dir_ok, learning_dir = create_learning_dir()
    
    print("\n" + "="*50)
    print("检查结果汇总:")
    print("="*50)
    
    all_ok = python_ok and git_ok
    
    if all_ok:
        print("🎉 环境检查通过！可以开始学习。")
        
        # 提供下一步建议
        print("\n📋 下一步建议:")
        print(f"1. 进入学习目录: cd {learning_dir}")
        print(f"2. 使用编辑器: {recommended_editor or '任意文本编辑器'}")
        print("3. 创建第一个Python程序")
        print("4. 开始学习Python基础语法")
    else:
        print("⚠️  环境检查未通过，需要先安装缺失的组件:")
        if not python_ok:
            print("  - 安装Python 3.8+")
        if not git_ok:
            print("  - 安装Git")
        
        print("\n💡 安装建议:")
        print("  - Ubuntu/Debian: sudo apt-get install python3 git")
        print("  - macOS: brew install python3 git")
        print("  - Windows: 下载Python和Git安装包")
    
    print("\n" + "="*50)
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)