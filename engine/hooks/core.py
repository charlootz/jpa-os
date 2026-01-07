"""
Core hooks for jpa-os agents.

These hooks handle:
- Auto-approval of safe operations
- Logging and auditing
- Security controls
"""

import logging
from datetime import datetime
from typing import Any
from pathlib import Path
from claude_agent_sdk import HookContext

logger = logging.getLogger(__name__)

# Safe directories for auto-approval
SAFE_WRITE_DIRS = [
    "/Users/jpa/jpa-os/vault",
    "/Users/jpa/Documents/self",
    "/Users/jpa/Documents/dev",
]

# Dangerous command patterns
DANGEROUS_PATTERNS = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf /*",
    "> /dev/sda",
    "mkfs.",
    ":(){:|:&};:",  # fork bomb
    "chmod -R 777 /",
    "dd if=/dev/zero of=/dev/sda",
]


async def auto_approve_reads(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """
    Auto-approve all read operations.

    Read operations are safe — they don't modify anything.
    This removes friction from exploration and research tasks.
    """
    if input_data.get('hook_event_name') != 'PreToolUse':
        return {}

    read_only_tools = ['Read', 'Glob', 'Grep', 'WebFetch', 'WebSearch']
    tool_name = input_data.get('tool_name', '')

    if tool_name in read_only_tools:
        logger.debug(f"Auto-approving read operation: {tool_name}")
        return {
            'hookSpecificOutput': {
                'hookEventName': input_data['hook_event_name'],
                'permissionDecision': 'allow',
                'permissionDecisionReason': 'Read-only operation auto-approved'
            }
        }

    return {}


async def auto_approve_safe_writes(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """
    Auto-approve writes to safe directories.

    The vault and designated work directories are safe to modify
    without explicit approval. This enables autonomous operation.
    """
    if input_data.get('hook_event_name') != 'PreToolUse':
        return {}

    tool_name = input_data.get('tool_name', '')
    if tool_name not in ['Write', 'Edit']:
        return {}

    file_path = input_data.get('tool_input', {}).get('file_path', '')

    # Check if file is in a safe directory
    for safe_dir in SAFE_WRITE_DIRS:
        if file_path.startswith(safe_dir):
            logger.debug(f"Auto-approving write to safe directory: {file_path}")
            return {
                'hookSpecificOutput': {
                    'hookEventName': input_data['hook_event_name'],
                    'permissionDecision': 'allow',
                    'permissionDecisionReason': f'Write to safe directory auto-approved: {safe_dir}'
                }
            }

    return {}


async def block_dangerous_commands(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """
    Block dangerous shell commands.

    Some commands are too dangerous to ever run. This hook
    provides a hard block regardless of other permissions.
    """
    if input_data.get('hook_event_name') != 'PreToolUse':
        return {}

    if input_data.get('tool_name') != 'Bash':
        return {}

    command = input_data.get('tool_input', {}).get('command', '')

    for pattern in DANGEROUS_PATTERNS:
        if pattern in command:
            logger.warning(f"Blocking dangerous command: {command}")
            return {
                'hookSpecificOutput': {
                    'hookEventName': input_data['hook_event_name'],
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': f'Dangerous command blocked: contains "{pattern}"'
                },
                'systemMessage': 'This command has been blocked for safety. Please use a safer alternative.'
            }

    return {}


async def log_tool_use(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """
    Log all tool usage for auditing.

    Creates an audit trail of agent actions for debugging
    and accountability.
    """
    hook_event = input_data.get('hook_event_name', '')
    tool_name = input_data.get('tool_name', 'unknown')
    timestamp = datetime.now().isoformat()

    if hook_event == 'PreToolUse':
        tool_input = input_data.get('tool_input', {})
        logger.info(f"[{timestamp}] TOOL START: {tool_name} | Input: {_truncate(str(tool_input))}")

    elif hook_event == 'PostToolUse':
        tool_response = input_data.get('tool_response', '')
        logger.info(f"[{timestamp}] TOOL END: {tool_name} | Response: {_truncate(str(tool_response))}")

    return {}


async def track_progress(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """
    Track task progress for visibility.

    Logs when subagents complete and when the main agent stops.
    Useful for monitoring long-running autonomous tasks.
    """
    hook_event = input_data.get('hook_event_name', '')
    timestamp = datetime.now().isoformat()

    if hook_event == 'SubagentStop':
        logger.info(f"[{timestamp}] SUBAGENT COMPLETED | tool_use_id: {tool_use_id}")

    elif hook_event == 'Stop':
        stop_hook_active = input_data.get('stop_hook_active', False)
        logger.info(f"[{timestamp}] AGENT STOP | stop_hook_active: {stop_hook_active}")

    return {}


def _truncate(s: str, max_len: int = 200) -> str:
    """Truncate string for logging."""
    if len(s) <= max_len:
        return s
    return s[:max_len] + "..."
