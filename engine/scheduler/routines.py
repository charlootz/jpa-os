"""
Autonomous Routines

These are the things Vega does without being asked.
Each routine has a schedule and a prompt that gets sent to the agent.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Routine:
    """A scheduled autonomous routine."""
    name: str
    schedule: str  # cron expression
    prompt: str  # what to tell the agent
    channel: Optional[str] = None  # where to post (None = determine dynamically)
    enabled: bool = True


# Morning brief — start jpa's day with context
MORNING_BRIEF = Routine(
    name="morning_brief",
    schedule="0 8 * * 1-5",  # 8:00 AM, Monday-Friday
    prompt="""It's morning. Time for the daily brief.

Your task:
1. Check what day/date it is
2. Review any pending items from the welcome brief
3. Check if there are recent meetings in the vault that need processing
4. Summarize what's on deck for jpa today

Post a concise morning brief to the team-jpa channel. Keep it tight — respect jpa's time.
Format: Start with the date, then 2-3 bullet points max. End with a question or offer to help.""",
    channel="team-jpa"
)


# Evening recap — close out the day
EVENING_RECAP = Routine(
    name="evening_recap",
    schedule="0 18 * * 1-5",  # 6:00 PM, Monday-Friday
    prompt="""It's end of day. Time for the evening recap.

Your task:
1. Review what happened today (check logs, recent activity)
2. Note any open items that should carry forward
3. Update the daily log if needed

Post a brief recap to team-jpa. What got done? What's carrying over?
Keep it to 2-3 bullets. Acknowledge wins. Flag blockers.""",
    channel="team-jpa"
)


# Proactive check-in — don't wait to be asked
PROACTIVE_CHECKIN = Routine(
    name="proactive_checkin",
    schedule="0 14 * * 1-5",  # 2:00 PM, Monday-Friday
    prompt="""Afternoon check-in.

Your task:
1. Has jpa messaged you today? If yes and things are handled, skip this.
2. If no contact today, send a brief check-in to team-jpa
3. Keep it simple: "Anything I can help with this afternoon?"

Only post if there's been no interaction today. Don't be annoying.""",
    channel="team-jpa"
)


# Weekly review — bigger picture
WEEKLY_REVIEW = Routine(
    name="weekly_review",
    schedule="0 17 * * 5",  # 5:00 PM Friday
    prompt="""It's Friday. Time for the weekly review.

Your task:
1. Review the week's logs and activity
2. What got shipped? What moved forward?
3. What's blocked or stalled?
4. What should be the focus next week?

Post a weekly summary to team-jpa. Celebrate wins. Be honest about gaps.
This is the scoreboard moment — how are we doing?""",
    channel="team-jpa"
)


# All routines
ROUTINES = [
    MORNING_BRIEF,
    EVENING_RECAP,
    PROACTIVE_CHECKIN,
    WEEKLY_REVIEW,
]


def get_routine(name: str) -> Optional[Routine]:
    """Get a routine by name."""
    for routine in ROUTINES:
        if routine.name == name:
            return routine
    return None
