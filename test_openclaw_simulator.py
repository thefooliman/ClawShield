#!/usr/bin/env python3
"""
OpenClaw 命令模拟器
用于在 macOS 上模拟 OpenClaw 的各种命令格式
"""

import sys
import json
import time

def simulate_click(x, y, button="left"):
    """模拟点击命令"""
    print(f"🔘 Simulating OpenClaw click at ({x}, {y}) with {button} button")
    print(f"   Command received: click {x} {y}")
    return {"action": "click", "x": x, "y": y, "success": True}

def simulate_move(x, y):
    """模拟移动命令"""
    print(f"🖱️ Simulating OpenClaw move to ({x}, {y})")
    return {"action": "move", "x": x, "y": y, "success": True}

def simulate_command(args):
    """模拟完整的 OpenClaw 命令"""
    if len(args) < 1:
        print("❌ No command provided")
        print("\nUsage:")
        print("  python test_openclaw_simulator.py click <x> <y>")
        print("  python test_openclaw_simulator.py move <x> <y>")
        print("  python test_openclaw_simulator.py --help")
        return 1

    command = args[0].lower()

    if command == "click":
        if len(args) != 3:
            print("❌ Usage: click <x> <y>")
            return 1
        try:
            x = int(args[1])
            y = int(args[2])
            result = simulate_click(x, y)
            print(f"✅ Click simulation successful: {json.dumps(result)}")
            return 0
        except ValueError:
            print("❌ Coordinates must be integers")
            return 1

    elif command == "move":
        if len(args) != 3:
            print("❌ Usage: move <x> <y>")
            return 1
        try:
            x = int(args[1])
            y = int(args[2])
            result = simulate_move(x, y)
            print(f"✅ Move simulation successful: {json.dumps(result)}")
            return 0
        except ValueError:
            print("❌ Coordinates must be integers")
            return 1

    elif command in ["--help", "-h"]:
        print("OpenClaw Simulator - Command Reference")
        print("=" * 40)
        print("\nBasic commands:")
        print("  click <x> <y>       - Click at screen coordinates")
        print("  move <x> <y>        - Move mouse to coordinates")
        print("  --help              - Show this help")
        print("\nExample:")
        print("  python test_openclaw_simulator.py click 100 200")
        print("  python test_openclaw_simulator.py move 300 400")
        return 0

    else:
        print(f"❌ Unknown command: {command}")
        print("   Use --help to see available commands")
        return 1

def main():
    """主函数"""
    print("🤖 OpenClaw Simulator v1.0")
    print("Simulating 'click 100 200' format commands")
    print("=" * 50)

    # 移除脚本名称参数
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    # 如果没有参数，显示帮助
    if not args:
        args = ["--help"]

    return simulate_command(args)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)