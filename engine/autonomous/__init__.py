"""
Autonomous operation for jpa-os agents.

This module enables agents to work independently:
- Work queue for pending tasks
- Daemon for continuous operation
- Integration with hooks for auto-approval
"""

from engine.autonomous.queue import WorkQueue
from engine.autonomous.daemon import AutonomousDaemon

__all__ = ["WorkQueue", "AutonomousDaemon"]
