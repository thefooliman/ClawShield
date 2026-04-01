#!/usr/bin/env python3
"""
OpenClaw ClawShield Plugin

This plugin integrates ClawShield security into OpenClaw,
providing real-time risk assessment for click operations.

Installation:
1. Copy this file to your OpenClaw plugins directory
2. Configure OpenClaw to load this plugin
3. Restart OpenClaw or your automation scripts

Usage:
- As a standalone plugin for OpenClaw
- As a middleware in automation pipelines
- As a command-line wrapper for existing OpenClaw scripts
"""

import sys
import os
import time
from typing import Dict, List, Any, Optional

# Add ClawShield to Python path if not already installed
CLAWSHIELD_PATH = os.path.join(os.path.dirname(__file__), '..')
if CLAWSHIELD_PATH not in sys.path:
    sys.path.insert(0, CLAWSHIELD_PATH)

try:
    from src.integration.openclaw_integration import OpenClawMiddleware, OpenClawWrapper
    from src.core.risk_engine import RiskEngine
    from src.core.history_store import HistoryStore
    CLAWSHIELD_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ ClawShield not available: {e}")
    print("💡 Install ClawShield first: pip install -r requirements.txt")
    CLAWSHIELD_AVAILABLE = False


class ClawShieldOpenClawPlugin:
    """
    Official ClawShield plugin for OpenClaw.

    This plugin provides multiple integration levels:
    1. Pre-click risk assessment
    2. Real-time UI analysis
    3. Historical trust building
    4. Adaptive security policies
    """

    def __init__(self, config: Dict = None):
        """
        Initialize the ClawShield plugin.

        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self.name = "ClawShield Security Plugin"
        self.version = "1.0.0"
        self.enabled = self.config.get('enabled', True)
        self.log_level = self.config.get('log_level', 'INFO')

        # Initialize ClawShield components
        if CLAWSHIELD_AVAILABLE:
            self.middleware = OpenClawMiddleware()
            self.risk_engine = RiskEngine()
            self.history_store = HistoryStore()
            self._log("INFO", f"{self.name} v{self.version} initialized")
        else:
            self._log("ERROR", "ClawShield components not available")
            self.enabled = False

    def _log(self, level: str, message: str):
        """Log message with level prefix."""
        if level == "ERROR" or self.log_level == "DEBUG":
            print(f"[{level}] {self.name}: {message}")

    def before_action(self, action_type: str, params: Dict) -> Dict[str, Any]:
        """
        Called before any OpenClaw action.

        Args:
            action_type: Type of action (click, type, move, etc.)
            params: Action parameters

        Returns:
            Decision dictionary with allow/block flag
        """
        if not self.enabled:
            return {"allowed": True, "reason": "Plugin disabled"}

        self._log("DEBUG", f"Before {action_type}: {params}")

        # Special handling for click actions
        if action_type in ['click', 'mouse_click', 'tap']:
            x = params.get('x')
            y = params.get('y')
            button = params.get('button', 'left')

            if x is not None and y is not None:
                return self.before_click(x, y, button, params)
            else:
                self._log("WARN", f"Missing coordinates for {action_type}: {params}")

        # For non-click actions, allow by default
        return {"allowed": True, "reason": f"Non-critical action: {action_type}"}

    def before_click(self, x: int, y: int, button: str = "left",
                    context: Dict = None) -> Dict[str, Any]:
        """
        Security assessment before click execution.

        This is the main security checkpoint that:
        1. Analyzes the UI element at (x, y)
        2. Calculates multi-factor risk score
        3. Makes allow/block decision
        4. Provides detailed reasoning

        Args:
            x, y: Click coordinates
            button: Mouse button (left, right, middle)
            context: Additional context (source, timestamp, etc.)

        Returns:
            Decision dictionary with:
            - allowed: True/False
            - risk_score: 0.0-1.0
            - reasons: List of risk factors
            - recommendation: Suggested action
        """
        if not self.enabled or not CLAWSHIELD_AVAILABLE:
            return {"allowed": True, "risk_score": 0.0, "reason": "Plugin unavailable"}

        context = context or {}
        context.update({
            'plugin': self.name,
            'timestamp': time.time(),
            'button': button
        })

        self._log("INFO", f"🔍 Security assessment for click at ({x}, {y})")

        # Use ClawShield middleware for assessment
        try:
            result = self.middleware.on_click(x, y, context)

            # Enhance result with additional risk analysis
            if result.get('allowed', True):
                # Calculate detailed risk score
                risk_factors = self.risk_engine.assess_click(x, y, context)
                risk_score = risk_factors.get('total_score', 0.0)

                result.update({
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'recommendation': 'Proceed with caution' if risk_score > 0.3 else 'Safe to proceed'
                })

                if risk_score > 0.7:
                    self._log("WARN", f"⚠️ High risk click ({risk_score:.2f}) at ({x}, {y})")
                elif risk_score > 0.3:
                    self._log("INFO", f"⚠️ Medium risk click ({risk_score:.2f}) at ({x}, {y})")
                else:
                    self._log("INFO", f"✅ Low risk click ({risk_score:.2f}) at ({x}, {y})")

            return result

        except Exception as e:
            self._log("ERROR", f"Risk assessment failed: {e}")
            # Fail open: allow click when assessment fails
            return {
                "allowed": True,
                "risk_score": 0.5,  # Default medium risk
                "reason": f"Assessment failed: {str(e)}",
                "error": True
            }

    def after_action(self, action_type: str, params: Dict,
                    success: bool, result: Dict = None):
        """
        Called after OpenClaw action completion.

        Used for:
        - Recording successful actions for trust building
        - Updating risk models
        - Logging and analytics

        Args:
            action_type: Type of action performed
            params: Action parameters
            success: Whether action succeeded
            result: Optional result from before_action
        """
        if not self.enabled:
            return

        # Record click actions for historical trust
        if action_type in ['click', 'mouse_click', 'tap'] and success:
            x = params.get('x')
            y = params.get('y')

            if x is not None and y is not None and CLAWSHIELD_AVAILABLE:
                try:
                    # Record in history for trust building
                    self.history_store.record_click(x, y, True)

                    risk_score = result.get('risk_score', 0.5) if result else 0.5
                    self._log("DEBUG", f"📝 Recorded click at ({x}, {y}), risk: {risk_score:.2f}")
                except Exception as e:
                    self._log("ERROR", f"Failed to record click: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get plugin statistics and status."""
        stats = {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "clawshield_available": CLAWSHIELD_AVAILABLE,
            "config": self.config
        }

        if CLAWSHIELD_AVAILABLE:
            try:
                # Get risk engine stats
                risk_stats = self.risk_engine.get_stats()
                stats.update({
                    "risk_assessments": risk_stats.get('total_assessments', 0),
                    "average_risk_score": risk_stats.get('average_score', 0.0),
                    "high_risk_count": risk_stats.get('high_risk_count', 0)
                })
            except:
                pass

        return stats

    def configure(self, new_config: Dict):
        """Update plugin configuration."""
        old_enabled = self.enabled
        self.config.update(new_config)
        self.enabled = self.config.get('enabled', old_enabled)
        self.log_level = self.config.get('log_level', self.log_level)

        self._log("INFO", f"Configuration updated: enabled={self.enabled}, log_level={self.log_level}")


# Factory function for OpenClaw plugin system
def create_plugin(config: Dict = None) -> ClawShieldOpenClawPlugin:
    """
    Factory function for OpenClaw plugin system.

    OpenClaw typically calls this function to create plugin instances.

    Args:
        config: Plugin configuration from OpenClaw

    Returns:
        Initialized ClawShield plugin instance
    """
    return ClawShieldOpenClawPlugin(config)


# Command-line interface for testing
def main():
    """Test the plugin from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="ClawShield OpenClaw Plugin Tester")
    parser.add_argument('--test-click', nargs=2, type=int, metavar=('X', 'Y'),
                       help='Test click assessment at coordinates X Y')
    parser.add_argument('--config', type=str, help='Configuration file (JSON)')
    parser.add_argument('--stats', action='store_true', help='Show plugin statistics')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    # Load configuration if provided
    config = {}
    if args.config:
        import json
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return 1

    if args.debug:
        config['log_level'] = 'DEBUG'

    # Create and test plugin
    plugin = ClawShieldOpenClawPlugin(config)

    if args.test_click:
        x, y = args.test_click
        print(f"🧪 Testing click at ({x}, {y})...")

        result = plugin.before_click(x, y, "left", {"test": True})

        print("\n📊 Assessment Results:")
        print(f"  Allowed: {'✅ Yes' if result.get('allowed') else '❌ No'}")
        print(f"  Risk Score: {result.get('risk_score', 0.0):.2f}")
        print(f"  Reason: {result.get('reason', 'No reason provided')}")

        if result.get('risk_factors'):
            print(f"  Risk Factors: {result.get('risk_factors')}")

        # Simulate after-action
        plugin.after_action('click', {'x': x, 'y': y}, True, result)

    elif args.stats:
        stats = plugin.get_stats()
        print("\n📈 Plugin Statistics:")
        for key, value in stats.items():
            if key != 'config':  # Don't print full config
                print(f"  {key}: {value}")

    else:
        parser.print_help()

        # Show quick test example
        print("\n🚀 Quick Test Example:")
        print("  python openclaw_plugin_clawshield.py --test-click 100 200")
        print("  python openclaw_plugin_clawshield.py --stats")

    return 0


if __name__ == "__main__":
    sys.exit(main())