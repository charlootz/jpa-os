"""
Autonomous operation hooks for jpa-os.

These hooks enable agents to work independently for extended periods
without requiring constant human prompting.
"""

import logging
from datetime import datetime
from typing import Any
from pathlib import Path
from claude_agent_sdk import HookContext

logger = logging.getLogger(__name__)

# Path to the work queue file
WORK_QUEUE_PATH = Path("/Users/jpa/jpa-os/vault/hive/work_queue.md")


async def check_for_more_work(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """
    Check if there's more work to do when agent stops.

    This hook fires on Stop events and checks the work queue
    for pending tasks. If work exists, it signals the agent
    to continue.

    Note: The actual continuation logic needs to be handled
    by the calling code since hooks can't directly restart
    the agent. This hook adds context about pending work.
    """
    if input_data.get('hook_event_name') != 'Stop':
        return {}

    # Check for pending work
    pending_work = _get_pending_work()

    if pending_work:
        logger.info(f"Stop hook: Found {len(pending_work)} pending tasks")
        return {
            'systemMessage': f"""
AUTONOMOUS MODE: You have pending tasks in the work queue.
Before fully stopping, please review and address these items:

{_format_work_items(pending_work)}

If you've completed your current task and these items need attention,
continue working on them. Otherwise, acknowledge completion.
"""
        }

    logger.info("Stop hook: No pending work, agent can stop")
    return {}


async def log_stop_reason(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """
    Log when and why the agent stops.

    Creates an audit trail of agent lifecycle events.
    """
    if input_data.get('hook_event_name') != 'Stop':
        return {}

    timestamp = datetime.now().isoformat()
    session_id = input_data.get('session_id', 'unknown')
    stop_hook_active = input_data.get('stop_hook_active', False)

    logger.info(
        f"[{timestamp}] AGENT STOPPING | "
        f"session: {session_id} | "
        f"stop_hook_active: {stop_hook_active}"
    )

    # Log to timesheet
    _log_to_timesheet(timestamp, "Agent session ended")

    return {}


def _get_pending_work() -> list[dict]:
    """
    Read pending work items from the queue.

    Returns a list of pending tasks if the queue exists.
    """
    if not WORK_QUEUE_PATH.exists():
        return []

    try:
        content = WORK_QUEUE_PATH.read_text()
        # Simple parsing: look for unchecked items
        pending = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- [ ]'):
                pending.append({
                    'task': line[5:].strip(),
                    'status': 'pending'
                })
        return pending
    except Exception as e:
        logger.error(f"Error reading work queue: {e}")
        return []


def _format_work_items(items: list[dict]) -> str:
    """Format work items for display."""
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item['task']}")
    return '\n'.join(lines)


def _log_to_timesheet(timestamp: str, note: str):
    """Append to Vega's timesheet."""
    timesheet_path = Path("/Users/jpa/jpa-os/vault/hive/timesheets/vega.md")
    try:
        if timesheet_path.exists():
            with open(timesheet_path, 'a') as f:
                f.write(f"\n- **{timestamp}** — {note}")
    except Exception as e:
        logger.error(f"Error writing to timesheet: {e}")
