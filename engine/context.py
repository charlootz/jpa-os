"""
Builds context for agents from config and state.
"""

import yaml
from pathlib import Path
from datetime import datetime
import pytz

from engine.tools.vault import get_recent_meetings, search_meetings, read_file

def load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

def get_current_time() -> str:
    tz = pytz.timezone("America/New_York")
    return datetime.now(tz).strftime("%A, %B %d, %Y %I:%M %p ET")

def build_context(task: str, project: str = None) -> str:
    """Build the full context string for an agent."""
    config = load_config()
    
    # Format projects
    projects_str = ""
    for name, proj in config.get("projects", {}).items():
        status = proj.get("status", "unknown")
        desc = proj.get("description", "")
        projects_str += f"\n### {name} [{status}]\n{desc}\n"
    
    # Format people
    people_str = ""
    for person in config.get("people", []):
        people_str += f"- {person['name']} ({person['role']}): {person.get('notes', '')}\n"
    if not people_str:
        people_str = "(none defined yet)"
    
    # Active project context
    project_context = ""
    if project and project in config.get("projects", {}):
        proj = config["projects"][project]
        project_context = f"""
## Active Project: {project}
Status: {proj.get('status')}
Description: {proj.get('description')}
Repo: {proj.get('repo')}
Channels: {', '.join(proj.get('slack_channels', []))}
"""

    context = f"""
# CURRENT TIME
{get_current_time()}

# MISSION
{config.get('mission', '')}

# WHO YOU ARE HELPING
Name: {config['me']['name']}
Role: {config['me']['role']}
Timezone: {config['me']['timezone']}

# SCORE
Current: {config['score']['current']}
Streak: {config['score']['streak']} days
Thresholds: <{config['score']['thresholds']['losing']} losing | {config['score']['thresholds']['winning']}+ winning | {config['score']['thresholds']['dominant']}+ dominant

# PROJECTS
{projects_str}
{project_context}

# KEY PEOPLE
{people_str}

# TASK
{task}

# RECENT MEETINGS
{get_recent_meetings(3)}

# REMEMBER
Every action should increase the score.
If your suggestion doesn't move the number, reconsider.
Protect the streak. Hunt for leverage. Ship > perfect.
"""
    return context.strip()


def build_context_with_search(task: str, search_query: str = None, project: str = None) -> str:
    """Build context with optional meeting search."""
    base = build_context(task, project)
    
    if search_query:
        search_results = search_meetings(search_query)
        base += f"\n\n# MEETING SEARCH RESULTS FOR '{search_query}'\n{search_results}"
    
    return base