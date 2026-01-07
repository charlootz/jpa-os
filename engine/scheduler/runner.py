"""
Routine Runner

Executes a routine: runs the agent with the prompt, posts result to Slack.

Usage:
    python -m engine.scheduler.runner morning_brief
    python -m engine.scheduler.runner evening_recap --dry-run
"""

import os
import sys
import argparse
import asyncio
import logging
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from slack_sdk.web.async_client import AsyncWebClient

from engine.scheduler.routines import get_routine, ROUTINES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_channel_id(client: AsyncWebClient, channel_name: str) -> str | None:
    """Get channel ID from channel name."""
    try:
        result = await client.conversations_list(types="public_channel,private_channel")
        for channel in result.get("channels", []):
            if channel.get("name") == channel_name:
                return channel["id"]
    except Exception as e:
        logger.error(f"Error looking up channel {channel_name}: {e}")
    return None


async def run_routine(routine_name: str, dry_run: bool = False) -> str:
    """
    Execute a routine.

    Args:
        routine_name: Name of the routine to run
        dry_run: If True, print output instead of posting to Slack

    Returns:
        The agent's response
    """
    routine = get_routine(routine_name)
    if not routine:
        available = ", ".join(r.name for r in ROUTINES)
        raise ValueError(f"Unknown routine: {routine_name}. Available: {available}")

    if not routine.enabled:
        logger.info(f"Routine {routine_name} is disabled, skipping")
        return ""

    logger.info(f"Running routine: {routine_name}")
    logger.info(f"Prompt: {routine.prompt[:100]}...")

    # Run the agent
    from engine.agents.base import run_vega

    # Add time context to the prompt
    now = datetime.now()
    time_context = f"Current time: {now.strftime('%A, %B %d, %Y %I:%M %p')}\n\n"
    full_prompt = time_context + routine.prompt

    response = await run_vega(full_prompt)

    if dry_run:
        print("\n" + "=" * 60)
        print(f"ROUTINE: {routine_name}")
        print(f"CHANNEL: {routine.channel}")
        print("=" * 60)
        print(response)
        print("=" * 60 + "\n")
        return response

    # Post to Slack
    if routine.channel:
        token = os.environ.get("SLACK_BOT_TOKEN")
        if not token:
            logger.error("SLACK_BOT_TOKEN not set, cannot post to Slack")
            print(response)
            return response

        client = AsyncWebClient(token=token)
        channel_id = await get_channel_id(client, routine.channel)

        if not channel_id:
            logger.error(f"Could not find channel: {routine.channel}")
            print(response)
            return response

        try:
            await client.chat_postMessage(
                channel=channel_id,
                text=response
            )
            logger.info(f"Posted to #{routine.channel}")
        except Exception as e:
            logger.error(f"Failed to post to Slack: {e}")
            print(response)

    return response


def main():
    parser = argparse.ArgumentParser(description="Run a scheduled routine")
    parser.add_argument("routine", nargs="?", help="Name of routine to run")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Print output instead of posting to Slack")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List available routines")

    args = parser.parse_args()

    if args.list:
        print("Available routines:")
        for r in ROUTINES:
            status = "enabled" if r.enabled else "disabled"
            print(f"  {r.name}: {r.schedule} ({status})")
        return

    if not args.routine:
        parser.print_help()
        return

    asyncio.run(run_routine(args.routine, args.dry_run))


if __name__ == "__main__":
    main()
