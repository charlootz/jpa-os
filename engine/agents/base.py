"""
Base agent wrapper around claude-agent-sdk.
Injects context into every call.
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
from engine.context import build_context

async def run_agent(task: str, project: str = None, tools: list = None) -> str:
    """
    Run an agent with full context injection.
    
    Args:
        task: What you want the agent to do
        project: Optional project name for focused context
        tools: Optional list of tools to allow (default: none)
    
    Returns:
        The agent's response
    """
    context = build_context(task, project)
    
    # Combine context with task into a single prompt
    prompt = f"""
{context}

Based on the above context, help with this task. Be direct and actionable.
"""
    
    allowed_tools = tools or []
    
    result_text = ""
    
    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            model="claude-opus-4-5-20251101",
            system_prompt={"type": "preset", "preset": "claude_code"},
            setting_sources=["project"]  # loads CLAUDE.md   
)
    ):
        if hasattr(message, 'result'):
            result_text = message.result
    
    return result_text


def run(task: str, project: str = None, tools: list = None) -> str:
    """Sync wrapper for run_agent."""
    return asyncio.run(run_agent(task, project, tools))