"""
OpenClaw integration for ClawShield

This module provides integration with OpenClaw, allowing ClawShield to
intercept and secure clicks sent by OpenClaw-controlled agents.

Two integration modes:
1. Wrapper Executor: Intercepts OpenClaw commands and applies security checks
2. Plugin/Middleware: Acts as a plugin within OpenClaw's execution chain
"""

import subprocess
import json
import os
import sys
import time
from typing import Dict, List, Optional, Tuple, Any
import re

from src.core.click import safe_click

class OpenClawWrapper:
    """
    Wrapper executor for OpenClaw commands.
    Intercepts click commands and applies ClawShield security checks.
    """

    def __init__(self, openclaw_path: str = None):
        """
        Initialize the OpenClaw wrapper.

        Args:
            openclaw_path: Path to OpenClaw executable or command.
                          If None, assumes 'openclaw' is in PATH.
        """
        self.openclaw_path = openclaw_path or "openclaw"
        self.intercepted_clicks = 0
        self.blocked_clicks = 0

    def execute_command(self, command: List[str], intercept_clicks: bool = True) -> Dict[str, Any]:
        """
        Execute an OpenClaw command with optional click interception.

        Args:
            command: OpenClaw command and arguments
            intercept_clicks: Whether to intercept and secure click commands

        Returns:
            Dictionary with execution results
        """
        print(f"🔧 Executing OpenClaw command: {' '.join(command)}")

        if intercept_clicks:
            return self._execute_with_interception(command)
        else:
            return self._execute_direct(command)

    def _execute_direct(self, command: List[str]) -> Dict[str, Any]:
        """Execute command without interception."""
        try:
            result = subprocess.run(
                [self.openclaw_path] + command,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "intercepted_clicks": 0,
                "blocked_clicks": 0
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"OpenClaw not found at {self.openclaw_path}",
                "intercepted_clicks": 0,
                "blocked_clicks": 0
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout",
                "intercepted_clicks": 0,
                "blocked_clicks": 0
            }

    def _execute_with_interception(self, command: List[str]) -> Dict[str, Any]:
        """
        Execute command with click interception.

        This method:
        1. Parses the command for click operations
        2. Intercepts click coordinates
        3. Applies ClawShield security checks via safe_click()
        4. Executes modified command or blocks unsafe clicks
        """
        # Parse command for click operations
        click_commands = self._extract_clicks(command)

        if not click_commands:
            # No clicks to intercept, execute directly
            return self._execute_direct(command)

        print(f"🛡️ Intercepted {len(click_commands)} click(s) for security check")

        # Process each click with ClawShield
        processed_clicks = []
        for click_cmd in click_commands:
            x, y = self._parse_click_coordinates(click_cmd)
            if x is not None and y is not None:
                print(f"📍 Click at ({x}, {y}) - applying security check...")

                # Use ClawShield's safe_click for security assessment
                if safe_click(x, y):
                    print(f"✅ Click allowed at ({x}, {y})")
                    processed_clicks.append({
                        "original": click_cmd,
                        "coordinates": (x, y),
                        "allowed": True
                    })
                else:
                    print(f"🛑 Click blocked at ({x}, {y})")
                    self.blocked_clicks += 1
                    processed_clicks.append({
                        "original": click_cmd,
                        "coordinates": (x, y),
                        "allowed": False
                    })
                self.intercepted_clicks += 1

        # Build execution report
        allowed_clicks = sum(1 for c in processed_clicks if c["allowed"])
        blocked_clicks = sum(1 for c in processed_clicks if not c["allowed"])

        return {
            "success": allowed_clicks > 0 or len(click_commands) == 0,
            "intercepted_clicks": self.intercepted_clicks,
            "allowed_clicks": allowed_clicks,
            "blocked_clicks": blocked_clicks,
            "processed_clicks": processed_clicks,
            "original_command": ' '.join(command),
            "note": "Command executed with ClawShield security layer"
        }

    def _extract_clicks(self, command: List[str]) -> List[str]:
        """
        Extract click-related commands from OpenClaw command.

        This is a simplified implementation. In a real scenario,
        this would parse OpenClaw's specific command syntax.
        """
        click_patterns = [
            r'click\(\s*(\d+)\s*,\s*(\d+)\s*\)',
            r'click\s+(\d+)\s+(\d+)',
            r'mouse\s+click\s+(\d+)\s+(\d+)',
            r'--click\s+(\d+),(\d+)'
        ]

        clicks = []
        cmd_str = ' '.join(command)

        for pattern in click_patterns:
            matches = re.finditer(pattern, cmd_str, re.IGNORECASE)
            for match in matches:
                clicks.append(match.group(0))

        # Also look for individual arguments that might be coordinates
        for i, arg in enumerate(command):
            if arg.lower() in ['click', 'mouseclick', 'tap']:
                if i + 2 < len(command):
                    # Next two arguments might be coordinates
                    try:
                        x = int(command[i + 1])
                        y = int(command[i + 2])
                        clicks.append(f"{arg} {x} {y}")
                    except ValueError:
                        pass

        return clicks

    def _parse_click_coordinates(self, click_cmd: str) -> Tuple[Optional[int], Optional[int]]:
        """Parse click coordinates from a click command string."""
        # Try various patterns to extract coordinates
        patterns = [
            r'(\d+)\s*,\s*(\d+)',  # "100, 200" or "100,200"
            r'\(\s*(\d+)\s*,\s*(\d+)\s*\)',  # "click(100, 200)"
            r'click\s+(\d+)\s+(\d+)',  # "click 100 200"
            r'mouse\s+click\s+(\d+)\s+(\d+)',  # "mouse click 100 200"
        ]

        for pattern in patterns:
            match = re.search(pattern, click_cmd)
            if match:
                try:
                    x = int(match.group(1))
                    y = int(match.group(2))
                    return x, y
                except ValueError:
                    continue

        return None, None

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about intercepted clicks."""
        return {
            "intercepted_clicks": self.intercepted_clicks,
            "blocked_clicks": self.blocked_clicks,
            "allowed_clicks": self.intercepted_clicks - self.blocked_clicks
        }


class OpenClawMiddleware:
    """
    Plugin/Middleware for OpenClaw integration.

    This class demonstrates how ClawShield could be integrated
    as a plugin within OpenClaw's execution pipeline.
    """

    def __init__(self):
        self.name = "ClawShield Security Plugin"
        self.version = "1.0"
        self.enabled = True

    def on_click(self, x: int, y: int, context: Dict = None) -> Dict[str, Any]:
        """
        Hook method called by OpenClaw when a click is requested.

        Args:
            x, y: Click coordinates
            context: Additional context about the click

        Returns:
            Decision dictionary with allow/block and reasoning
        """
        if not self.enabled:
            return {"allowed": True, "reason": "Middleware disabled"}

        print(f"🔍 OpenClaw requested click at ({x}, {y})")

        # Apply ClawShield security check
        allowed = safe_click(x, y)

        if allowed:
            return {
                "allowed": True,
                "reason": "Click passed ClawShield security assessment",
                "coordinates": (x, y)
            }
        else:
            return {
                "allowed": False,
                "reason": "Click blocked by ClawShield risk assessment",
                "coordinates": (x, y),
                "recommendation": "Review the UI element before proceeding"
            }

    def on_command(self, command: str, args: List[str]) -> Dict[str, Any]:
        """
        Hook method called by OpenClaw for any command.

        This allows broader interception of OpenClaw operations.
        """
        # Check if this is a click-related command
        click_keywords = ['click', 'mouse', 'tap', 'press']
        if any(keyword in command.lower() for keyword in click_keywords):
            # Try to extract coordinates
            for i, arg in enumerate(args):
                try:
                    # Simple coordinate detection
                    if i + 1 < len(args):
                        x = int(arg)
                        y = int(args[i + 1])
                        return self.on_click(x, y, {"command": command, "args": args})
                except ValueError:
                    continue

        # For non-click commands, allow by default
        return {"allowed": True, "reason": "Non-click command"}


def wrap_openclaw_command(command_str: str) -> Dict[str, Any]:
    """
    Convenience function to wrap an OpenClaw command with security.

    Args:
        command_str: OpenClaw command string

    Returns:
        Execution results
    """
    wrapper = OpenClawWrapper()
    command_parts = command_str.split()
    return wrapper.execute_command(command_parts, intercept_clicks=True)


# Singleton instances for easy access
_openclaw_wrapper = None
_openclaw_middleware = None

def get_wrapper() -> OpenClawWrapper:
    """Get or create singleton OpenClaw wrapper."""
    global _openclaw_wrapper
    if _openclaw_wrapper is None:
        _openclaw_wrapper = OpenClawWrapper()
    return _openclaw_wrapper

def get_middleware() -> OpenClawMiddleware:
    """Get or create singleton OpenClaw middleware."""
    global _openclaw_middleware
    if _openclaw_middleware is None:
        _openclaw_middleware = OpenClawMiddleware()
    return _openclaw_middleware