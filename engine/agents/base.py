"""
Base agent wrapper around claude-agent-sdk.
Injects charter, identity, and context into every call.

Supports two modes:
1. query() - One-shot queries (simple, no hooks)
2. ClaudeSDKClient - Continuous conversation with hooks (autonomous mode)
"""

import asyncio
import logging
from pathlib import Path
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    AssistantMessage,
    TextBlock,
    ResultMessage,
    HookMatcher,
)
from engine.agents.system_prompt import build_coo_system_prompt, build_system_prompt

logger = logging.getLogger(__name__)

# Default directories agents can access
ROOT = Path(__file__).parent.parent.parent
DEFAULT_ADD_DIRS = [
    str(ROOT / "vault"),
    "/Users/jpa/Documents/self",
    "/Users/jpa/Documents/hiring",
    "/Users/jpa/Documents/dev",
]

# Default tools for COO
COO_TOOLS = [
    "Read", "Write", "Edit", "Bash", "Glob", "Grep",
    "WebSearch", "WebFetch", "Task", "TodoWrite"
]


def get_default_hooks() -> dict:
    """
    Get the default hooks configuration for autonomous operation.

    Returns hooks that:
    - Auto-approve read operations
    - Auto-approve writes to safe directories
    - Block dangerous commands
    - Log tool usage
    - Track progress
    """
    from engine.hooks.core import (
        auto_approve_reads,
        auto_approve_safe_writes,
        block_dangerous_commands,
        log_tool_use,
        track_progress,
    )
    from engine.hooks.autonomous import (
        check_for_more_work,
        log_stop_reason,
    )

    return {
        'PreToolUse': [
            # Security first: block dangerous commands
            HookMatcher(matcher='Bash', hooks=[block_dangerous_commands]),
            # Auto-approve safe operations
            HookMatcher(matcher='Read|Glob|Grep|WebFetch|WebSearch', hooks=[auto_approve_reads]),
            HookMatcher(matcher='Write|Edit', hooks=[auto_approve_safe_writes]),
            # Log everything
            HookMatcher(hooks=[log_tool_use]),
        ],
        'PostToolUse': [
            HookMatcher(hooks=[log_tool_use]),
        ],
        'Stop': [
            HookMatcher(hooks=[check_for_more_work, log_stop_reason]),
        ],
        'SubagentStop': [
            HookMatcher(hooks=[track_progress]),
        ],
    }


async def run_vega(task: str, stream_callback=None) -> str:
    """
    Run Vega (the COO) with full context injection.

    Uses simple query() mode - good for one-shot tasks.

    Args:
        task: What you want Vega to do
        stream_callback: Optional callback for streaming text output

    Returns:
        Vega's response
    """
    system_prompt = build_coo_system_prompt(name="Vega")

    result_text = ""

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            model="claude-opus-4-5-20251101",
            system_prompt=system_prompt,
            allowed_tools=COO_TOOLS,
            permission_mode="acceptEdits",
            cwd=str(ROOT),
            add_dirs=DEFAULT_ADD_DIRS,
            setting_sources=["project"],
        )
    ):
        # Stream text as it comes in
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    if stream_callback:
                        stream_callback(block.text)

        # Capture final result
        if hasattr(message, 'result'):
            result_text = message.result

    return result_text


async def run_vega_autonomous(
    initial_task: str,
    stream_callback=None,
    max_continuation_turns: int = 5,
) -> str:
    """
    Run Vega in autonomous mode with hooks.

    Uses ClaudeSDKClient for:
    - Continuous conversation
    - Hook support for auto-approval
    - Ability to continue working on pending tasks

    Args:
        initial_task: The initial task to work on
        stream_callback: Optional callback for streaming text output
        max_continuation_turns: Max times to continue after completing a task

    Returns:
        Final response from Vega
    """
    system_prompt = build_coo_system_prompt(name="Vega")
    hooks = get_default_hooks()

    options = ClaudeAgentOptions(
        model="claude-opus-4-5-20251101",
        system_prompt=system_prompt,
        allowed_tools=COO_TOOLS,
        permission_mode="acceptEdits",
        cwd=str(ROOT),
        add_dirs=DEFAULT_ADD_DIRS,
        setting_sources=["project"],
        hooks=hooks,
    )

    result_text = ""
    continuation_count = 0

    async with ClaudeSDKClient(options=options) as client:
        # Send initial task
        await client.query(initial_task)

        while continuation_count < max_continuation_turns:
            # Process response
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            if stream_callback:
                                stream_callback(block.text)

                if isinstance(message, ResultMessage):
                    result_text = message.result or ""

                    # Check if agent wants to continue
                    # (The Stop hook may have injected a system message about pending work)
                    if _has_pending_work():
                        continuation_count += 1
                        logger.info(f"Autonomous continuation #{continuation_count}")
                        await client.query(
                            "Continue with the next pending task from the work queue."
                        )
                    else:
                        # No more work, exit the loop
                        continuation_count = max_continuation_turns

    return result_text


async def run_vega_streaming(task: str):
    """
    Run Vega and yield text chunks as they stream in.

    Args:
        task: What you want Vega to do

    Yields:
        Text chunks as they arrive
    """
    system_prompt = build_coo_system_prompt(name="Vega")

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            model="claude-opus-4-5-20251101",
            system_prompt=system_prompt,
            allowed_tools=COO_TOOLS,
            permission_mode="acceptEdits",
            cwd=str(ROOT),
            add_dirs=DEFAULT_ADD_DIRS,
            setting_sources=["project"],
        )
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    yield block.text


async def run_agent(
    task: str,
    agent_name: str = "Vega",
    agent_role: str = "COO",
    role_prompt: str = "",
    tools: list = None,
    stream_callback=None,
    autonomous: bool = False,
) -> str:
    """
    Run any agent with full context injection.

    Args:
        task: What you want the agent to do
        agent_name: The agent's name
        agent_role: The agent's role
        role_prompt: Role-specific instructions
        tools: List of allowed tools
        stream_callback: Optional callback for streaming text output
        autonomous: If True, use autonomous mode with hooks

    Returns:
        The agent's response
    """
    if agent_name == "Vega" and agent_role == "COO":
        if autonomous:
            return await run_vega_autonomous(task, stream_callback)
        return await run_vega(task, stream_callback)

    system_prompt = build_system_prompt(
        agent_name=agent_name,
        agent_role=agent_role,
        role_prompt=role_prompt
    )

    allowed_tools = tools or COO_TOOLS
    result_text = ""

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            model="claude-opus-4-5-20251101",
            system_prompt=system_prompt,
            allowed_tools=allowed_tools,
            permission_mode="acceptEdits",
            cwd=str(ROOT),
            add_dirs=DEFAULT_ADD_DIRS,
            setting_sources=["project"],
        )
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    if stream_callback:
                        stream_callback(block.text)

        if hasattr(message, 'result'):
            result_text = message.result

    return result_text


def run(task: str, stream_callback=None) -> str:
    """Sync wrapper to run Vega."""
    return asyncio.run(run_vega(task, stream_callback))


def run_autonomous(task: str, stream_callback=None) -> str:
    """Sync wrapper to run Vega in autonomous mode."""
    return asyncio.run(run_vega_autonomous(task, stream_callback))


def _has_pending_work() -> bool:
    """Check if there's pending work in the queue."""
    work_queue = ROOT / "vault" / "hive" / "work_queue.md"
    if not work_queue.exists():
        return False

    try:
        content = work_queue.read_text()
        # Simple check: are there unchecked items?
        return '- [ ]' in content
    except Exception:
        return False
