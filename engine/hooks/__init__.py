"""
Hooks for jpa-os agents.

Hooks intercept agent execution to add:
- Auto-approval for safe operations
- Logging and auditing
- Security controls
- Autonomous continuation logic
"""

from engine.hooks.core import (
    auto_approve_reads,
    auto_approve_safe_writes,
    log_tool_use,
    block_dangerous_commands,
    track_progress,
)

from engine.hooks.autonomous import (
    check_for_more_work,
    log_stop_reason,
)

__all__ = [
    # Core hooks
    "auto_approve_reads",
    "auto_approve_safe_writes",
    "log_tool_use",
    "block_dangerous_commands",
    "track_progress",
    # Autonomous hooks
    "check_for_more_work",
    "log_stop_reason",
]
