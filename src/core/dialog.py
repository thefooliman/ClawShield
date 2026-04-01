"""
跨平台对话框模块
提供统一的确认对话框接口，支持 macOS、Linux 和 Windows
"""

import platform
import subprocess
import sys
from typing import Optional

def show_confirmation_dialog(message: str, title: str = "ClawShield Security Alert") -> bool:
    """
    显示跨平台确认对话框

    Args:
        message: 显示给用户的消息
        title: 对话框标题

    Returns:
        True 如果用户点击"允许"，False 如果点击"阻止"或关闭对话框
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        return _show_macos_dialog(message, title)
    elif system == "Linux":
        return _show_linux_dialog(message, title)
    elif system == "Windows":
        return _show_windows_dialog(message, title)
    else:
        # 未知平台，回退到控制台
        print(f"⚠️ 不支持的系统: {system}")
        return _show_console_dialog(message, title)

def _show_macos_dialog(message: str, title: str) -> bool:
    """macOS 原生对话框 (osascript)"""
    try:
        # 转义消息中的特殊字符
        escaped_message = message.replace('"', '\\"').replace("'", "\\'")
        cmd = f'''osascript -e 'display dialog "{escaped_message}" buttons {{"Block", "Allow"}} default button "Block" with icon caution' '''

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # 30秒超时
        )

        return "Allow" in result.stdout
    except subprocess.TimeoutExpired:
        print("⏱️  对话框超时，默认阻止")
        return False
    except Exception as e:
        print(f"⚠️  macOS 对话框失败: {e}")
        return _show_console_dialog(message, title)

def _show_linux_dialog(message: str, title: str) -> bool:
    """Linux 对话框 (zenity/kdialog/tkinter 回退)"""
    # 尝试 zenity (GNOME)
    try:
        cmd = [
            'zenity', '--question',
            '--text', message,
            '--title', title,
            '--ok-label=Allow',
            '--cancel-label=Block',
            '--width=400',
            '--timeout=30'  # 30秒超时
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # 继续尝试下一个方法

    # 尝试 kdialog (KDE)
    try:
        cmd = [
            'kdialog', '--yesno', message,
            '--title', title,
            '--yes-label', 'Allow',
            '--no-label', 'Block',
            '--timeout', '30'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 尝试 tkinter (跨平台但需要 GUI)
    try:
        import tkinter as tk
        from tkinter import messagebox

        # 创建隐藏的根窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        root.attributes('-topmost', True)  # 置顶

        # 显示对话框
        result = messagebox.askyesno(
            title=title,
            message=message,
            default=messagebox.NO,  # 默认阻止
            icon=messagebox.WARNING
        )

        root.destroy()
        return result
    except Exception:
        pass

    # 所有 GUI 方法都失败，回退到控制台
    return _show_console_dialog(message, title)

def _show_windows_dialog(message: str, title: str) -> bool:
    """Windows 对话框"""
    try:
        import ctypes

        # MB_YESNO = 0x4, MB_ICONWARNING = 0x30
        # IDYES = 6, IDNO = 7
        result = ctypes.windll.user32.MessageBoxW(
            0,  # hWnd
            message,
            title,
            0x4 | 0x30  # MB_YESNO | MB_ICONWARNING
        )
        return result == 6  # IDYES
    except Exception:
        return _show_console_dialog(message, title)

def _show_console_dialog(message: str, title: str) -> bool:
    """控制台回退对话框"""
    print(f"\n{'='*60}")
    print(f"🛡️  {title}")
    print(f"{'='*60}")
    print(f"📝 {message}")
    print(f"{'='*60}")

    while True:
        try:
            response = input("\n允许此操作吗? (allow/block): ").lower().strip()
            if response in ['allow', 'a', 'y', 'yes']:
                return True
            elif response in ['block', 'b', 'n', 'no']:
                return False
            else:
                print("⚠️  请输入 'allow' 或 'block'")
        except KeyboardInterrupt:
            print("\n⏹️  操作被用户中断，默认阻止")
            return False
        except EOFError:
            print("\n📴 输入结束，默认阻止")
            return False

def show_info_dialog(message: str, title: str = "ClawShield Info") -> None:
    """显示信息对话框（无用户交互）"""
    system = platform.system()

    if system == "Darwin":  # macOS
        try:
            escaped_message = message.replace('"', '\\"')
            cmd = f'''osascript -e 'display dialog "{escaped_message}" buttons {{"OK"}} default button "OK"' '''
            subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        except:
            print(f"ℹ️  {title}: {message}")

    elif system == "Linux":
        # 尝试 zenity
        try:
            cmd = ['zenity', '--info', '--text', message, '--title', title, '--width=400']
            subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return
        except:
            pass

        # 尝试 kdialog
        try:
            cmd = ['kdialog', '--msgbox', message, '--title', title]
            subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return
        except:
            pass

        print(f"ℹ️  {title}: {message}")

    elif system == "Windows":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)  # MB_ICONINFORMATION
        except:
            print(f"ℹ️  {title}: {message}")

    else:
        print(f"ℹ️  {title}: {message}")

def test_dialog_system():
    """测试对话框系统"""
    print("🧪 测试对话框系统...")

    platforms = {
        "Darwin": "macOS",
        "Linux": "Linux",
        "Windows": "Windows"
    }

    current = platform.system()
    print(f"📱 当前系统: {platforms.get(current, current)}")
    print(f"🐍 Python: {sys.version}")

    # 测试信息对话框
    print("\n📋 测试信息对话框...")
    show_info_dialog("这是一个测试信息对话框", "对话框系统测试")

    # 测试确认对话框
    print("\n📋 测试确认对话框...")
    print("请观察对话框弹出（如果有）或按照控制台提示操作")

    result = show_confirmation_dialog(
        "这是一个测试确认对话框。\n请选择 '允许' 或 '阻止'。",
        "安全测试"
    )

    print(f"\n📊 测试结果: {'允许' if result else '阻止'}")
    print("✅ 对话框系统测试完成")

    return True

if __name__ == "__main__":
    test_dialog_system()