"""
OpenClaw integration module for ClawShield.

This module provides integration with OpenClaw for intercepting
and securing click commands from autonomous agents.
"""

from .openclaw_integration import (
    OpenClawWrapper,
    OpenClawMiddleware,
    wrap_openclaw_command,
)

__all__ = [
    'OpenClawWrapper',
    'OpenClawMiddleware',
    'wrap_openclaw_command',
]

__version__ = '1.0.0'