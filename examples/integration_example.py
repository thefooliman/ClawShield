#!/usr/bin/env python3
"""
OpenClaw + ClawShield Integration Example

This example demonstrates three integration patterns:
1. Command-line wrapper (easiest)
2. Direct plugin integration (most powerful)
3. Hybrid approach (flexible)

Requirements:
- OpenClaw installed and accessible
- ClawShield installed and configured
"""

import sys
import os
import subprocess
import time
from typing import Dict, List, Any, Optional

# Add ClawShield to path
CLAWSHIELD_PATH = os.path.join(os.path.dirname(__file__), '..')
if CLAWSHIELD_PATH not in sys.path:
    sys.path.insert(0, CLAWSHIELD_PATH)

# ----------------------------------------------------------------------
# Pattern 1: Command-Line Wrapper (Simplest Integration)
# ----------------------------------------------------------------------

def pattern1_commandline_wrapper():
    """
    Pattern 1: Wrap OpenClaw commands with ClawShield CLI.

    This is the simplest integration method - just replace 'openclaw'
    with './clawshield run --wrap openclaw' in your scripts.
    """
    print("=" * 60)
    print("Pattern 1: Command-Line Wrapper")
    print("=" * 60)

    # Original OpenClaw command
    original_command = "openclaw click 100 200"

    # Secured version with ClawShield
    secured_command = "./clawshield run --wrap openclaw 'click 100 200'"

    print(f"Original:  {original_command}")
    print(f"Secured:   {secured_command}")
    print()

    # Execute secured command
    print("Executing secured command...")
    try:
        result = subprocess.run(
            secured_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        print("Output:")
        print(result.stdout)

        if result.stderr:
            print("Errors:")
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ----------------------------------------------------------------------
# Pattern 2: Direct Plugin Integration
# ----------------------------------------------------------------------

def pattern2_direct_plugin():
    """
    Pattern 2: Use ClawShield as a plugin in your OpenClaw scripts.

    This provides real-time security assessment for each click.
    """
    print("\n" + "=" * 60)
    print("Pattern 2: Direct Plugin Integration")
    print("=" * 60)

    try:
        # Import ClawShield components
        from src.integration.openclaw_integration import OpenClawMiddleware
        from src.core.risk_engine import RiskEngine

        # Initialize components
        middleware = OpenClawMiddleware()
        risk_engine = RiskEngine()

        print("✅ ClawShield components loaded")
        print()

        # Example: Simulate OpenClaw click requests
        test_clicks = [
            (100, 200, "Safe edge click"),
            (960, 540, "Risky center click (1920x1080 screen)"),
            (50, 50, "Another safe edge click"),
        ]

        for x, y, description in test_clicks:
            print(f"\n📋 Testing: {description}")
            print(f"  Coordinates: ({x}, {y})")

            # Get security assessment
            assessment = middleware.on_click(x, y, {
                'source': 'example_script',
                'description': description
            })

            # Get risk score
            risk_factors = risk_engine.assess_click(x, y, {})
            risk_score = risk_factors.get('total_score', 0.0)

            print(f"  Assessment: {'✅ Allowed' if assessment.get('allowed') else '❌ Blocked'}")
            print(f"  Risk Score: {risk_score:.2f}")
            print(f"  Reason: {assessment.get('reason', 'No reason')}")

            if risk_score > 0.7:
                print("  ⚠️  HIGH RISK - User confirmation required")
            elif risk_score > 0.3:
                print("  ⚠️  Medium risk - Proceed with caution")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure ClawShield is installed and in Python path")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


# ----------------------------------------------------------------------
# Pattern 3: Hybrid Approach
# ----------------------------------------------------------------------

def pattern3_hybrid_approach():
    """
    Pattern 3: Hybrid approach - use wrapper for simple tasks,
    plugin for complex automation.

    This provides the best balance of simplicity and power.
    """
    print("\n" + "=" * 60)
    print("Pattern 3: Hybrid Approach")
    print("=" * 60)

    class SecureOpenClaw:
        """Hybrid OpenClaw controller with ClawShield security."""

        def __init__(self, use_plugin=True):
            self.use_plugin = use_plugin
            self.clicks_allowed = 0
            self.clicks_blocked = 0

            if use_plugin:
                try:
                    from src.integration.openclaw_integration import OpenClawMiddleware
                    self.middleware = OpenClawMiddleware()
                    print("✅ Plugin mode enabled")
                except ImportError:
                    print("⚠️  Plugin mode unavailable, falling back to wrapper")
                    self.use_plugin = False

        def safe_click(self, x: int, y: int, context: Dict = None) -> bool:
            """Execute a click with security assessment."""
            context = context or {}

            if self.use_plugin:
                # Use plugin for real-time assessment
                assessment = self.middleware.on_click(x, y, context)

                if assessment.get('allowed'):
                    # Execute the actual click
                    return self._execute_click_direct(x, y)
                else:
                    print(f"🛑 Click blocked at ({x}, {y}): {assessment.get('reason')}")
                    self.clicks_blocked += 1
                    return False

            else:
                # Use wrapper mode
                cmd = f"./clawshield run --wrap openclaw 'click {x} {y}'"

                try:
                    result = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True, timeout=5
                    )

                    if result.returncode == 0:
                        self.clicks_allowed += 1
                        return True
                    else:
                        self.clicks_blocked += 1
                        return False

                except Exception as e:
                    print(f"❌ Error executing click: {e}")
                    return False

        def _execute_click_direct(self, x: int, y: int) -> bool:
            """Execute click using pyautogui (for plugin mode)."""
            try:
                import pyautogui
                pyautogui.click(x, y)
                self.clicks_allowed += 1
                print(f"✅ Click executed at ({x}, {y})")
                return True
            except Exception as e:
                print(f"❌ Click execution failed: {e}")
                return False

        def get_stats(self) -> Dict[str, Any]:
            """Get security statistics."""
            return {
                'clicks_allowed': self.clicks_allowed,
                'clicks_blocked': self.clicks_blocked,
                'total_clicks': self.clicks_allowed + self.clicks_blocked,
                'block_rate': self.clicks_blocked / max(1, self.clicks_allowed + self.clicks_blocked)
            }

    # Test the hybrid approach
    print("Testing hybrid OpenClaw controller...")

    controller = SecureOpenClaw(use_plugin=True)

    test_points = [
        (100, 200, {"task": "button_click"}),
        (300, 400, {"task": "navigation"}),
        (960, 540, {"task": "center_click", "warning": "high_risk"}),
    ]

    for x, y, context in test_points:
        print(f"\n🔧 Processing click at ({x}, {y})...")
        success = controller.safe_click(x, y, context)

        if success:
            print(f"  Status: ✅ Executed")
        else:
            print(f"  Status: ❌ Blocked/Failed")

        # Small delay between clicks
        time.sleep(0.5)

    # Show statistics
    stats = controller.get_stats()
    print(f"\n📊 Security Statistics:")
    print(f"  Total clicks: {stats['total_clicks']}")
    print(f"  Allowed: {stats['clicks_allowed']}")
    print(f"  Blocked: {stats['clicks_blocked']}")
    print(f"  Block rate: {stats['block_rate']:.1%}")

    return True


# ----------------------------------------------------------------------
# Pattern 4: Complete Automation Example
# ----------------------------------------------------------------------

def pattern4_complete_automation():
    """
    Pattern 4: Complete automation script with ClawShield integration.

    This shows a real-world automation task with comprehensive security.
    """
    print("\n" + "=" * 60)
    print("Pattern 4: Complete Automation Example")
    print("=" * 60)

    class SecureBrowserAutomation:
        """Secure browser automation with ClawShield protection."""

        def __init__(self):
            self.steps_completed = 0
            self.steps_failed = 0

            # Import security components
            try:
                from src.integration.openclaw_integration import OpenClawMiddleware
                from src.core.risk_engine import RiskEngine
                self.middleware = OpenClawMiddleware()
                self.risk_engine = RiskEngine()
                self.security_enabled = True
                print("✅ Security layer enabled")
            except ImportError:
                self.security_enabled = False
                print("⚠️  Security layer unavailable (proceeding without)")

        def execute_step(self, step: Dict) -> bool:
            """Execute a single automation step with security check."""
            action = step.get('action')
            params = step.get('params', {})
            require_security = step.get('security', True)

            print(f"\n📋 Step: {action} {params}")

            # Security assessment for click actions
            if action == 'click' and require_security and self.security_enabled:
                x = params.get('x')
                y = params.get('y')

                if x is not None and y is not None:
                    print(f"  🔍 Security assessment...")

                    # Get risk assessment
                    assessment = self.middleware.on_click(x, y, {
                        'action': 'browser_automation',
                        'step': step.get('description', 'unknown')
                    })

                    if not assessment.get('allowed', True):
                        print(f"  ❌ Security check failed: {assessment.get('reason')}")
                        self.steps_failed += 1

                        # Check if we should ask for user confirmation
                        risk_factors = self.risk_engine.assess_click(x, y, {})
                        risk_score = risk_factors.get('total_score', 0.0)

                        if risk_score > 0.7:
                            print("  ⚠️  HIGH RISK - Action blocked")
                            return False
                        else:
                            print("  ⚠️  Risk detected, but proceeding anyway")
                            # In a real scenario, you might ask for user confirmation

            # Execute the action (simulated)
            print(f"  ▶️  Executing {action}...")
            time.sleep(0.3)  # Simulate execution time

            # Simulate success/failure
            success = True  # In reality, check actual execution result

            if success:
                print(f"  ✅ {action} completed")
                self.steps_completed += 1
            else:
                print(f"  ❌ {action} failed")
                self.steps_failed += 1

            return success

        def run_automation(self, steps: List[Dict]) -> bool:
            """Run complete automation workflow."""
            print(f"\n🚀 Starting secure automation ({len(steps)} steps)")

            all_success = True
            for i, step in enumerate(steps, 1):
                print(f"\nStep {i}/{len(steps)}")
                success = self.execute_step(step)
                if not success:
                    all_success = False

                    # Optional: Stop on critical failure
                    if step.get('critical', False):
                        print("🛑 Critical step failed - stopping automation")
                        break

            # Summary
            print(f"\n{'='*40}")
            print("Automation Complete")
            print(f"{'='*40}")
            print(f"Steps completed: {self.steps_completed}")
            print(f"Steps failed: {self.steps_failed}")
            print(f"Success rate: {self.steps_completed / max(1, self.steps_completed + self.steps_failed):.1%}")

            if self.security_enabled:
                print(f"Security: ✅ Enabled")
            else:
                print(f"Security: ⚠️  Disabled")

            return all_success

    # Define a secure automation workflow
    workflow = [
        {
            'action': 'navigate',
            'params': {'url': 'https://example.com/login'},
            'description': 'Navigate to login page',
            'security': False
        },
        {
            'action': 'click',
            'params': {'x': 400, 'y': 300},
            'description': 'Click login button',
            'security': True,
            'critical': True
        },
        {
            'action': 'type',
            'params': {'text': 'username', 'field': 'username'},
            'description': 'Enter username',
            'security': False
        },
        {
            'action': 'type',
            'params': {'text': 'password123', 'field': 'password', 'sensitive': True},
            'description': 'Enter password',
            'security': False
        },
        {
            'action': 'click',
            'params': {'x': 450, 'y': 350},
            'description': 'Click submit button',
            'security': True,
            'critical': True
        },
        {
            'action': 'click',
            'params': {'x': 500, 'y': 400},
            'description': 'Click "Remember me" (optional)',
            'security': True
        }
    ]

    # Run the automation
    automation = SecureBrowserAutomation()
    success = automation.run_automation(workflow)

    return success


# ----------------------------------------------------------------------
# Main execution
# ----------------------------------------------------------------------

def main():
    """Run all integration patterns."""
    print("🛡️  OpenClaw + ClawShield Integration Examples")
    print("=" * 60)

    # Run Pattern 1: Command-line wrapper
    print("\n1️⃣ Testing Pattern 1: Command-Line Wrapper")
    p1_success = pattern1_commandline_wrapper()

    # Run Pattern 2: Direct plugin
    print("\n2️⃣ Testing Pattern 2: Direct Plugin Integration")
    p2_success = pattern2_direct_plugin()

    # Run Pattern 3: Hybrid approach
    print("\n3️⃣ Testing Pattern 3: Hybrid Approach")
    p3_success = pattern3_hybrid_approach()

    # Run Pattern 4: Complete automation
    print("\n4️⃣ Testing Pattern 4: Complete Automation Example")
    p4_success = pattern4_complete_automation()

    # Summary
    print("\n" + "=" * 60)
    print("Integration Test Summary")
    print("=" * 60)

    patterns = [
        ("Command-Line Wrapper", p1_success),
        ("Direct Plugin", p2_success),
        ("Hybrid Approach", p3_success),
        ("Complete Automation", p4_success),
    ]

    for name, success in patterns:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")

    total = len(patterns)
    passed = sum(1 for _, success in patterns if success)

    print(f"\n🎯 Result: {passed}/{total} patterns passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n✨ All integration patterns working correctly!")
        print("\n🚀 Next steps:")
        print("   1. Choose the pattern that fits your use case")
        print("   2. Integrate into your OpenClaw automation scripts")
        print("   3. Test with real-world scenarios")
        print("   4. Monitor security logs and adjust thresholds")
    else:
        print(f"\n⚠️  {total - passed} patterns failed")
        print("   Check error messages above and ensure:")
        print("   - ClawShield is properly installed")
        print("   - Dependencies are satisfied")
        print("   - OpenClaw is accessible")

    return 0 if passed == total else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)