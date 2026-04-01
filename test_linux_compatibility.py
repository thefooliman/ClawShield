#!/usr/bin/env python3
"""
Linux 兼容性测试脚本
测试 ClawShield 在 Linux 环境中的基本功能
"""

import sys
import os
import platform

def test_imports():
    """测试所有必要的导入"""
    print("🔍 测试 Python 导入...")

    imports = [
        ("cv2", "opencv-python"),
        ("pytesseract", "pytesseract"),
        ("pyautogui", "pyautogui"),
        ("requests", "requests"),
        ("PIL", "Pillow"),
    ]

    all_passed = True
    for module_name, package_name in imports:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name} ({package_name})")
        except ImportError as e:
            print(f"  ❌ {module_name} ({package_name}): {e}")
            all_passed = False

    # 测试项目模块
    print("\n🔍 测试项目模块导入...")
    project_modules = [
        ("src.core.dialog", "跨平台对话框"),
        ("src.core.click", "安全点击"),
        ("src.core.risk_engine", "风险引擎"),
        ("src.core.history_store", "历史存储"),
        ("src.core.vision", "视觉守卫"),
    ]

    for module_path, description in project_modules:
        try:
            # 将项目根目录添加到 Python 路径
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            __import__(module_path)
            print(f"  ✅ {description} ({module_path})")
        except ImportError as e:
            print(f"  ❌ {description} ({module_path}): {e}")
            all_passed = False

    return all_passed

def test_platform_specific():
    """测试平台特定功能"""
    print(f"\n📱 平台信息: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {platform.python_version()}")

    system = platform.system()

    if system == "Linux":
        print("🐧 检测到 Linux 系统")

        # 检查 GUI 工具
        print("🔧 检查 GUI 工具...")
        import subprocess

        tools = ["zenity", "kdialog", "xmessage"]
        for tool in tools:
            try:
                subprocess.run([tool, "--version"], capture_output=True, timeout=2)
                print(f"  ✅ {tool} 可用")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                print(f"  ⚠️  {tool} 不可用")

        # 检查 Tesseract
        try:
            result = subprocess.run(["tesseract", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"  ✅ Tesseract: {version_line}")
            else:
                print(f"  ⚠️  Tesseract 返回错误")
        except FileNotFoundError:
            print(f"  ❌ Tesseract 未安装")

    elif system == "Darwin":
        print("🍎 检测到 macOS 系统")
    elif system == "Windows":
        print("🪟 检测到 Windows 系统")
    else:
        print(f"❓ 未知系统: {system}")

    return True

def test_dialog_system():
    """测试对话框系统"""
    print("\n💬 测试对话框系统...")

    try:
        # 导入对话框模块
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.core.dialog import show_confirmation_dialog, show_info_dialog

        # 测试信息对话框（无阻塞）
        print("📋 测试信息对话框...")
        show_info_dialog("这是 Linux 兼容性测试信息", "测试对话框")

        # 测试确认对话框（在控制台中）
        print("📋 测试确认对话框（控制台模式）...")
        print("   请按照提示输入 'allow' 或 'block'")

        # 模拟一个简单的测试，不实际弹出对话框
        # 在实际测试中，对话框可能会显示或回退到控制台
        result = show_confirmation_dialog(
            "测试确认对话框\n请选择 '允许' 或 '阻止'。",
            "兼容性测试"
        )

        print(f"   对话框结果: {'允许' if result else '阻止'}")
        return True

    except Exception as e:
        print(f"  ❌ 对话框测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_openclaw_integration():
    """测试 OpenClaw 集成组件"""
    print("\n🤖 测试 OpenClaw 集成组件...")

    try:
        # 检查集成模块
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # 尝试导入集成模块
        try:
            from src.integration.openclaw_integration import OpenClawWrapper
            print("  ✅ OpenClawWrapper 可用")

            # 测试命令解析
            wrapper = OpenClawWrapper(openclaw_path="echo")
            test_commands = [
                ["click", "100", "200"],
                ["mouse", "click", "300", "400"],
            ]

            for cmd in test_commands:
                clicks = wrapper._extract_clicks(cmd)
                print(f"    命令 '{' '.join(cmd)}': 找到 {len(clicks)} 个点击")

        except ImportError as e:
            print(f"  ⚠️  OpenClaw 集成模块: {e}")
            return False

        return True

    except Exception as e:
        print(f"  ❌ OpenClaw 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🧪 ClawShield Linux 兼容性测试")
    print("=" * 50)

    # 运行所有测试
    tests = [
        ("导入测试", test_imports),
        ("平台测试", test_platform_specific),
        ("对话框测试", test_dialog_system),
        ("OpenClaw 集成测试", test_openclaw_integration),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"🧪 {test_name}")
        print(f"{'='*40}")

        try:
            success = test_func()
            results.append((test_name, success))
            status = "✅ 通过" if success else "❌ 失败"
            print(f"\n{status}: {test_name}")
        except KeyboardInterrupt:
            print(f"\n⏹️ 测试被中断: {test_name}")
            results.append((test_name, False))
            break
        except Exception as e:
            print(f"\n💥 测试异常: {test_name} - {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # 显示测试总结
    print(f"\n{'='*50}")
    print("📊 测试总结")
    print(f"{'='*50}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")

    print(f"\n🎯 通过率: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n✨ 所有兼容性测试通过！")
        print("\n🚀 下一步:")
        print("   1. 运行完整测试: python test_openclaw_integration_macos.py")
        print("   2. 测试包装器模式: ./clawshield run --wrap openclaw 'click 100 200'")
        print("   3. 运行演示: ./clawshield demo")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        print("   请检查依赖安装: ./scripts/install_linux.sh")

    return 0 if passed == total else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试框架错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)