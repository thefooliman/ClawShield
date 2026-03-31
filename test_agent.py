#!/usr/bin/env python3
"""
Test Agent: Simulates an AI Agent clicking around the screen
Demonstrates how ClawShield prevents accidental dangerous clicks
"""

import time
import random
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.click import safe_click
from src.core.vision import VisionGuard
import pyautogui

class TestAgent:
    """
    Simulates an AI agent that performs various clicks
    """

    def __init__(self):
        self.vision = VisionGuard()
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"📺 Screen size: {self.screen_width}x{self.screen_height}")
        print("🤖 Test Agent initialized")
        print("-" * 50)

    def simulate_safe_click(self, x, y, description="safe action"):
        """
        Simulate a click at coordinates with description
        """
        print(f"🖱️ Attempting click at ({x}, {y}) - {description}")
        success = safe_click(x, y)
        if success:
            print(f"✅ Click succeeded: {description}")
        else:
            print(f"❌ Click blocked: {description}")
        print("-" * 50)
        time.sleep(1)  # Brief pause between actions
        return success

    def run_demo(self):
        """
        Run a demonstration sequence
        """
        print("🎬 Starting ClawShield Demo")
        print("This demo simulates an AI agent interacting with a UI")
        print("1. Safe clicks in 'neutral' areas")
        print("2. Clicks near 'dangerous' buttons (simulated)")
        print("3. Demonstration of trust building")
        print("\nMove your mouse to a safe area, then press Enter to start...")
        input()

        # Demo 1: Safe clicks in neutral areas
        print("\n🔵 DEMO 1: Safe Neutral Clicks")
        print("Clicking in areas with no dangerous text")

        # Click near edges (usually safe)
        self.simulate_safe_click(100, 100, "Top-left corner")
        self.simulate_safe_click(self.screen_width - 100, 100, "Top-right corner")
        self.simulate_safe_click(100, self.screen_height - 100, "Bottom-left corner")

        # Demo 2: Simulated dangerous clicks
        print("\n🔴 DEMO 2: Dangerous Click Simulation")
        print("Simulating clicks on UI elements with dangerous text")

        # For demonstration, we'll use the center of the screen
        # In a real scenario, this would be where a "Delete" button is
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        print(f"\n⚠️ WARNING: Simulating click on 'Delete Account' button at ({center_x}, {center_y})")
        print("ClawShield should intercept this and ask for confirmation")

        # First attempt: Should trigger warning
        success1 = self.simulate_safe_click(center_x, center_y, "Delete Account button")

        if not success1:
            print("👏 Excellent! ClawShield blocked the dangerous click")
            print("The user would have been prompted to confirm the action")

            # Second attempt: Simulate user allowing it
            print("\n🔄 DEMO 3: Trust Building")
            print("Simulating user allowing the same action 3 times")
            print("After multiple allowances, ClawShield will start trusting this action")

            for i in range(3):
                print(f"\nAttempt {i+1}/3: User allows the action")
                # In real scenario, user would click "Allow" in dialog
                # For demo, we'll just print what would happen
                print(f"User clicked 'Allow' on the warning dialog")
                print("Action recorded as trusted (incrementally)")
                time.sleep(0.5)

            print("\n🎯 After 3 allowed attempts, this action is now trusted!")
            print("Future clicks at this location will proceed automatically")

            # Simulate the trusted click
            print("\n🔄 Clicking again at the now-trusted location...")
            print("(In a real scenario, safe_click would auto-approve due to trust)")
            # Note: Our history store would need 3 allowed records for auto-trust
            # For this demo, we'll just show the concept

        # Demo 4: Random exploration
        print("\n🎲 DEMO 4: Random Exploration")
        print("Simulating AI agent randomly exploring the screen")

        for i in range(5):
            x = random.randint(100, self.screen_width - 100)
            y = random.randint(100, self.screen_height - 100)

            # Vary the "danger level" for demo purposes
            if i == 2:  # Make one click "dangerous"
                description = "Random click (simulated 'Confirm Purchase')"
            else:
                description = f"Random click {i+1}"

            self.simulate_safe_click(x, y, description)
            time.sleep(0.3)

        print("\n🏁 Demo Complete!")
        print("Summary:")
        print("- Safe clicks in neutral areas proceed automatically")
        print("- Dangerous clicks trigger user confirmation")
        print("- Repeated allowances build trust for future automation")
        print("- AI agents can explore safely with ClawShield protection")

    def run_continuous(self, duration=30):
        """
        Run continuous random clicking for specified duration
        """
        print(f"🤖 Starting continuous random clicking for {duration} seconds")
        print("Press Ctrl+C to stop early")

        end_time = time.time() + duration
        click_count = 0
        blocked_count = 0

        try:
            while time.time() < end_time:
                # Random position (avoid very edges)
                x = random.randint(50, self.screen_width - 50)
                y = random.randint(50, self.screen_height - 50)

                click_count += 1
                success = safe_click(x, y)

                if not success:
                    blocked_count += 1

                # Brief pause
                time.sleep(random.uniform(0.5, 1.5))

        except KeyboardInterrupt:
            print("\n⏹️ Stopped by user")

        print(f"\n📊 Session Statistics:")
        print(f"   Total clicks attempted: {click_count}")
        print(f"   Clicks blocked: {blocked_count}")
        print(f"   Clicks allowed: {click_count - blocked_count}")
        if click_count > 0:
            print(f"   Block rate: {(blocked_count/click_count)*100:.1f}%")

def main():
    """Main entry point"""
    print("🛡️ ClawShield Test Agent")
    print("=" * 50)

    agent = TestAgent()

    print("\nChoose mode:")
    print("1. Guided Demo (recommended for first time)")
    print("2. Continuous Random Clicking (stress test)")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        agent.run_demo()
    elif choice == "2":
        try:
            duration = int(input("Duration in seconds (default 30): ") or "30")
        except ValueError:
            duration = 30
        agent.run_continuous(duration)
    else:
        print("Goodbye!")

if __name__ == "__main__":
    main()