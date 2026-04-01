#!/usr/bin/env python3
"""
ClawShield Command Line Interface

Usage:
    clawshield run --wrap openclaw [command...]
    clawshield test
    clawshield demo
    clawshield --help
"""

import argparse
import sys
import os
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_openclaw_wrapper(command: List[str]) -> int:
    """
    Run OpenClaw command with ClawShield security wrapper.

    Args:
        command: OpenClaw command and arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        from src.integration.openclaw_integration import wrap_openclaw_command

        if not command:
            print("❌ No OpenClaw command provided")
            print("\nExample usage:")
            print("  clawshield run --wrap openclaw click 100 200")
            print("  clawshield run --wrap openclaw 'click(100, 200)'")
            return 1

        # Join command parts back into a string for parsing
        command_str = ' '.join(command)
        print(f"🛡️ Wrapping OpenClaw command with ClawShield security...")
        print(f"📝 Command: {command_str}")

        result = wrap_openclaw_command(command_str)

        # Display results
        print("\n📊 Execution Results:")
        print(f"  Success: {'✅ Yes' if result.get('success') else '❌ No'}")
        print(f"  Intercepted clicks: {result.get('intercepted_clicks', 0)}")
        print(f"  Allowed clicks: {result.get('allowed_clicks', 0)}")
        print(f"  Blocked clicks: {result.get('blocked_clicks', 0)}")

        if 'processed_clicks' in result and result['processed_clicks']:
            print("\n🔍 Click Details:")
            for click in result['processed_clicks']:
                x, y = click.get('coordinates', (None, None))
                status = "✅ Allowed" if click.get('allowed') else "🛑 Blocked"
                print(f"    {status} at ({x}, {y})")

        if 'error' in result:
            print(f"\n⚠️ Error: {result['error']}")
            return 1

        return 0 if result.get('success', False) else 1

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

def run_test() -> int:
    """Run ClawShield tests."""
    print("🧪 Running ClawShield tests...")

    test_scripts = [
        "test_ollama_integration.py",
        "test_agent.py"
    ]

    all_passed = True

    for test_script in test_scripts:
        script_path = os.path.join(os.path.dirname(__file__), '..', test_script)
        if os.path.exists(script_path):
            print(f"\n📋 Running {test_script}...")
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    print(f"✅ {test_script} passed")
                else:
                    print(f"❌ {test_script} failed with code {result.returncode}")
                    if result.stderr:
                        print(f"Error output:\n{result.stderr[:500]}")
                    all_passed = False
            except Exception as e:
                print(f"❌ Failed to run {test_script}: {e}")
                all_passed = False
        else:
            print(f"⚠️ Test script not found: {test_script}")

    return 0 if all_passed else 1

def run_demo() -> int:
    """Run ClawShield demonstration."""
    print("🎬 Starting ClawShield demonstration...")

    try:
        # Import and run the demo from test_agent.py
        import subprocess
        script_path = os.path.join(os.path.dirname(__file__), '..', 'test_agent.py')

        if os.path.exists(script_path):
            print("\n🤖 Launching AI Agent Simulation Demo...")
            print("Press Ctrl+C to exit early\n")

            result = subprocess.run(
                [sys.executable, script_path],
                text=True
            )

            return result.returncode
        else:
            print(f"❌ Demo script not found: {script_path}")
            return 1

    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return 1

def run_sentinel() -> int:
    """Run the real-time protection sentinel."""
    print("🛡️ Starting ClawShield Sentinel (real-time protection)...")

    try:
        from src.main import main as sentinel_main

        print("\n🎯 Move your mouse to test the protection")
        print("📊 Risk assessment will display in real-time")
        print("🖱️ Press 'q' in the OpenCV window to quit\n")

        sentinel_main()
        return 0

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        return 1
    except Exception as e:
        print(f"❌ Sentinel error: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ClawShield - Hybrid AI Security Sentry for Autonomous Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clawshield run --wrap openclaw click 100 200
  clawshield run --wrap openclaw "click(100, 200)"
  clawshield test
  clawshield demo
  clawshield sentinel
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # 'run' command with --wrap option
    run_parser = subparsers.add_parser('run', help='Run a command with ClawShield protection')
    run_parser.add_argument('--wrap', choices=['openclaw'], required=True,
                          help='Wrap the command with security checks')
    run_parser.add_argument('command_args', nargs=argparse.REMAINDER,
                          help='Command to wrap (e.g., "click 100 200")')

    # 'test' command
    subparsers.add_parser('test', help='Run ClawShield tests')

    # 'demo' command
    subparsers.add_parser('demo', help='Run ClawShield demonstration')

    # 'sentinel' command
    subparsers.add_parser('sentinel', help='Run real-time protection sentinel')

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Execute command
    if args.command == 'run':
        if args.wrap == 'openclaw':
            return run_openclaw_wrapper(args.command_args)
        else:
            print(f"❌ Unsupported wrapper: {args.wrap}")
            return 1
    elif args.command == 'test':
        return run_test()
    elif args.command == 'demo':
        return run_demo()
    elif args.command == 'sentinel':
        return run_sentinel()
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1

if __name__ == '__main__':
    sys.exit(main())