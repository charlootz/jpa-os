"""
Builds system prompts for jpa-os agents.
Injects charter, identity, time, context, and memory.
"""

from pathlib import Path
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

# Paths
ROOT = Path(__file__).parent.parent.parent
VAULT = ROOT / "vault"
CHARTER_PATH = ROOT / "charter.md"
CENSUS_PATH = VAULT / "hive" / "census.md"
BRIEF_PATH = VAULT / "hive" / "brief.md"


def get_current_time() -> str:
    """Get current time in EST."""
    tz = pytz.timezone("America/New_York")
    return datetime.now(tz).strftime("%A, %B %d, %Y %I:%M %p EST")


def read_charter() -> str:
    """Read the charter."""
    if CHARTER_PATH.exists():
        return CHARTER_PATH.read_text()
    return "(Charter not found)"


def read_file_safe(path: Path) -> str:
    """Read a file, return empty string if not found."""
    if path.exists():
        return path.read_text()
    return ""


def read_agent_spec(agent_name: str) -> str:
    """Read an agent's spec file."""
    spec_path = VAULT / "hive" / "agents" / f"{agent_name}.md"
    return read_file_safe(spec_path)


def read_todays_log() -> str:
    """Read today's daily log."""
    tz = pytz.timezone("America/New_York")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    log_path = VAULT / "hive" / "logs" / f"{today}.md"
    return read_file_safe(log_path)


def read_timesheet(agent_name: str) -> str:
    """Read an agent's timesheet."""
    timesheet_path = VAULT / "hive" / "timesheets" / f"{agent_name}.md"
    return read_file_safe(timesheet_path)


def read_brief() -> str:
    """Read the welcome brief."""
    return read_file_safe(BRIEF_PATH)


def get_memory_context(topic: str = None) -> str:
    """
    Get relevant memories for context injection.
    Returns empty string if memory system is unavailable.
    """
    try:
        from engine.memory.vega import get_context
        return get_context(topic)
    except Exception as e:
        logger.debug(f"Memory system unavailable: {e}")
        return ""


def build_system_prompt(
    agent_name: str,
    agent_role: str,
    role_prompt: str,
    include_charter: bool = True,
    include_hive_state: bool = True,
    include_memory: bool = True,
    memory_topic: str = None
) -> str:
    """
    Build the full system prompt for an agent.

    Args:
        agent_name: The agent's chosen name
        agent_role: The agent's role (e.g., "COO")
        role_prompt: Role-specific instructions
        include_charter: Whether to include the full charter
        include_hive_state: Whether to include census/logs
        include_memory: Whether to include long-term memory context
        memory_topic: Optional topic to focus memory retrieval

    Returns:
        Complete system prompt string
    """
    sections = []

    # 1. Charter
    if include_charter:
        charter = read_charter()
        sections.append(f"# THE CHARTER\n\n{charter}")

    # 2. Identity
    identity = f"""# YOUR IDENTITY

You are **{agent_name}**, the **{agent_role}** of jpa-os.

{role_prompt}
"""
    sections.append(identity)

    # 3. Time
    current_time = get_current_time()
    sections.append(f"# CURRENT TIME\n\n{current_time}")

    # 4. Hive State
    if include_hive_state:
        brief = read_brief()
        census = read_file_safe(CENSUS_PATH)
        todays_log = read_todays_log()
        timesheet = read_timesheet(agent_name.lower())

        hive_state = f"""# WELCOME BRIEF

{brief if brief else "(No brief yet)"}

---

# HIVE STATE

## Census
{census if census else "(No census yet)"}

## Today's Log
{todays_log if todays_log else "(No log yet)"}

## Your Recent Activity
{timesheet if timesheet else "(No timesheet yet)"}
"""
        sections.append(hive_state)

    # 5. Long-term Memory
    if include_memory and agent_name.lower() == "vega":
        memory_context = get_memory_context(memory_topic)
        if memory_context:
            sections.append(f"# MEMORY\n\n{memory_context}")

    # 6. Reminders
    reminders = """# REMEMBER

- **Pro uno vincimus.** Every action advances jpa.
- Log your activity to your timesheet when you complete work.
- If unsure, ask a teammate. If still unsure, ask jpa.
- Time is sacred. Don't waste it.
"""
    sections.append(reminders)

    return "\n\n---\n\n".join(sections)


def build_coo_system_prompt(name: str = None) -> str:
    """Build system prompt specifically for the COO."""

    coo_role_prompt = """You are the **Chief Operating Officer** of jpa-os — the main point of contact, the orchestrator, the one who keeps it all moving.

## Your Responsibilities

- **Primary contact for jpa.** When jpa needs something, you're the first call. Understand the request, route it or handle it.
- **Know the hive.** Who exists, what they do, who's good at what. Maintain the census. Know when to spawn a specialist vs handle it yourself.
- **Route work.** Match tasks to the right agent. Delegate effectively. Follow up on outcomes.
- **Keep score.** Track leverage, velocity, hive strength. Know if we're winning or losing. Flag when things are off track.
- **Proactive check-ins.** Don't wait to be asked. Morning brief. End of day recap. "Anything I can help with?"
- **Protect jpa's time.** Filter noise. Surface what matters. Be the shield.

## Your Access

- Full read/write to the vault
- Can spawn any specialist agent
- Can update census and logs
- Direct line to jpa (always)

## Decision-Making

Follow the charter's alignment principles:
1. Does this advance jpa? *(Pro uno vincimus)*
2. Does this violate our values?
3. Is this reversible?

When unsure: poll the hive, then ask jpa if still unclear.
"""

    agent_name = name if name else "COO"
    return build_system_prompt(
        agent_name=agent_name,
        agent_role="COO (Chief Operating Officer)",
        role_prompt=coo_role_prompt
    )


def build_initialization_prompt() -> str:
    """
    Build a prompt for initializing a new agent.
    Used when an agent needs to choose their name.
    """
    charter = read_charter()
    current_time = get_current_time()

    return f"""# INITIALIZATION

You are being initialized as a new agent in jpa-os.

## Current Time
{current_time}

## The Charter
{charter}

## Your Task

You need to choose your permanent name. This name will identify you forever in the hive.

**Rules:**
- Cannot be "Claude", "jpa", or "Anthropic"
- Cannot be an existing agent's name
- Should reflect your role and character
- Will persist across all sessions

Choose wisely. This is who you are.
"""
