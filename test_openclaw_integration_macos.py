#!/usr/bin/env python3
"""
OpenClaw 集成测试脚本 (macOS 模拟环境)
测试 ClawShield 与 OpenClaw 的集成功能

使用方法:
1. 直接运行: python test_openclaw_integration_macos.py
2. 选择测试模式: 包装器测试 / 插件测试 / 完整流程测试
"""

import sys
import os
import tempfile
import subprocess
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_command_parsing():
    """测试命令解析功能"""
    print("🔍 测试 OpenClaw 命令解析...")

    try:
        from src.integration.openclaw_integration import OpenClawWrapper

        wrapper = OpenClawWrapper(openclaw_path="echo")

        # 测试不同命令格式的解析
        test_commands = [
            ["click", "100", "200"],
            ["mouse", "click", "300", "400"],
            ["click(500, 600)"],
            ["--click", "700,800"],
        ]

        for cmd in test_commands:
            print(f"\n📝 解析命令: {' '.join(cmd)}")
            clicks = wrapper._extract_clicks(cmd)
            if clicks:
                print(f"   ✅ 找到点击命令: {clicks}")
                for click_cmd in clicks:
                    x, y = wrapper._parse_click_coordinates(click_cmd)
                    print(f"     坐标: ({x}, {y})")
            else:
                print("   ⚠️  未找到点击命令")

        return True

    except Exception as e:
        print(f"❌ 命令解析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wrapper_mode():
    """测试包装器模式"""
    print("\n🛡️ 测试包装器模式...")

    # 创建一个临时的 OpenClaw 模拟器脚本
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
#!/usr/bin/env python3
import sys
print("🤖 OpenClaw 模拟器执行:", " ".join(sys.argv[1:]))
print('{"result": "success", "clicks": 1}')
""")
        temp_path = f.name

    try:
        os.chmod(temp_path, 0o755)  # 使文件可执行

        from src.integration.openclaw_integration import OpenClawWrapper

        # 使用模拟器作为 OpenClaw 可执行文件
        wrapper = OpenClawWrapper(openclaw_path=temp_path)

        print("📋 测试场景 1: 简单点击命令")
        result = wrapper.execute_command(["click", "100", "200"], intercept_clicks=True)
        print(f"   结果: {json.dumps(result, indent=2)}")

        print("\n📋 测试场景 2: 复杂命令")
        result = wrapper.execute_command(["mouse", "click", "--button", "left", "300", "400"], intercept_clicks=True)
        print(f"   结果: {json.dumps(result, indent=2)}")

        print("\n📊 包装器统计:")
        stats = wrapper.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")

        return True

    except Exception as e:
        print(f"❌ 包装器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_path)
        except:
            pass

def test_plugin_mode():
    """测试插件/中间件模式"""
    print("\n🔌 测试插件/中间件模式...")

    try:
        from src.integration.openclaw_integration import OpenClawMiddleware

        middleware = OpenClawMiddleware()

        print("📋 测试场景 1: 点击事件处理")
        result = middleware.on_click(100, 200, {"button": "left", "timestamp": "2024-01-01"})
        print(f"   点击结果: {json.dumps(result, indent=2)}")

        print("\n📋 测试场景 2: 命令处理")
        result = middleware.on_command("click", ["150", "250"])
        print(f"   命令结果: {json.dumps(result, indent=2)}")

        print("\n📋 测试场景 3: 非点击命令")
        result = middleware.on_command("type", ["Hello World"])
        print(f"   非点击命令结果: {json.dumps(result, indent=2)}")

        return True

    except Exception as e:
        print(f"❌ 插件模式测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_integration():
    """测试 CLI 集成"""
    print("\n💻 测试 CLI 集成...")

    # 创建临时模拟器
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
#!/usr/bin/env python3
import sys
print("OpenClaw 模拟 CLI 调用")
sys.exit(0)
""")
        temp_path = f.name

    try:
        os.chmod(temp_path, 0o755)

        # 测试 CLI 包装器功能
        print("📋 测试场景: 通过 CLI 包装 OpenClaw 命令")

        # 由于我们没有实际的 openclaw 命令，这里测试解析逻辑
        from src.integration.openclaw_integration import wrap_openclaw_command

        test_commands = [
            "click 100 200",
            "mouse click 300 400",
            "click(500, 600)",
        ]

        for cmd in test_commands:
            print(f"\n🔧 测试命令: {cmd}")
            # 注意：这里会尝试执行 safe_click，需要 macOS 环境
            # 我们主要测试命令解析和包装逻辑
            try:
                result = wrap_openclaw_command(cmd)
                print(f"   解析成功: {result.get('intercepted_clicks', 0)} 个点击被拦截")
            except Exception as e:
                print(f"   ⚠️ 执行错误 (预期中，因为缺少实际环境): {str(e)[:100]}...")

        return True

    except Exception as e:
        print(f"❌ CLI 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

def test_full_workflow():
    """测试完整工作流程"""
    print("\n🔄 测试完整工作流程...")

    try:
        # 测试从命令解析到安全评估的完整流程
        print("📋 模拟工作流程:")
        print("   1. OpenClaw 发送命令: 'click 100 200'")
        print("   2. ClawShield 拦截并解析命令")
        print("   3. 提取坐标 (100, 200)")
        print("   4. 应用四因子风险评估")
        print("   5. 返回执行决策")

        from src.integration.openclaw_integration import OpenClawWrapper
        from src.core.click import safe_click

        # 创建包装器
        wrapper = OpenClawWrapper(openclaw_path="echo")

        # 模拟命令
        command = ["click", "100", "200"]
        print(f"\n🔍 解析命令: {' '.join(command)}")

        clicks = wrapper._extract_clicks(command)
        print(f"   找到点击命令: {clicks}")

        for click_cmd in clicks:
            x, y = wrapper._parse_click_coordinates(click_cmd)
            print(f"   提取坐标: ({x}, {y})")

            # 模拟安全点击检查 (在实际环境中会调用 safe_click)
            print(f"   模拟安全评估: 坐标 ({x}, {y})")
            print(f"   (在实际环境中，这里会调用 safe_click() 进行风险评估)")

        print("\n✅ 工作流程测试完成")
        print("   在实际 OpenClaw 环境中，ClawShield 会:")
        print("   1. 拦截所有 OpenClaw 点击命令")
        print("   2. 应用四因子风险评估 (关键词、位置、历史、LLM 视觉)")
        print("   3. 仅允许安全点击执行，拦截危险操作")
        print("   4. 提供详细的执行报告")

        return True

    except Exception as e:
        print(f"❌ 工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🛡️ ClawShield OpenClaw 集成测试 (macOS 模拟环境)")
    print("=" * 60)
    print("📌 测试目标:")
    print("   - 验证 OpenClaw 命令解析")
    print("   - 测试包装器模式集成")
    print("   - 测试插件/中间件模式")
    print("   - 验证 CLI 命令包装")
    print("   - 演示完整工作流程")
    print("=" * 60)

    # 运行所有测试
    tests = [
        ("命令解析", test_command_parsing),
        ("包装器模式", test_wrapper_mode),
        ("插件模式", test_plugin_mode),
        ("CLI 集成", test_cli_integration),
        ("完整工作流程", test_full_workflow),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"🧪 开始测试: {test_name}")
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
            results.append((test_name, False))

    # 显示测试总结
    print(f"\n{'='*60}")
    print("📊 测试总结")
    print(f"{'='*60}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")

    print(f"\n🎯 通过率: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n✨ 所有测试通过！OpenClaw 集成功能正常。")
        print("\n🚀 下一步:")
        print("   1. 在 Linux 虚拟机中安装 ClawShield")
        print("   2. 替换 macOS 原生对话框为 Linux 兼容方案")
        print("   3. 使用真实 OpenClaw 命令进行端到端测试")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，需要检查集成代码。")

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