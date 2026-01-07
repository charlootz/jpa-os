"""
Routine Runner

Executes a routine: runs the agent with the prompt, posts result to Discord.

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

import discord
import aiohttp

from engine.scheduler.routines import get_routine, ROUTINES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def post_to_discord(channel_name: str, content: str):
    """Post a message to Discord channel."""
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not set")
        return False

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    posted = False

    @client.event
    async def on_ready():
        nonlocal posted
        for guild in client.guilds:
            for channel in guild.text_channels:
                if channel.name == channel_name:
                    # Split long messages (Discord 2000 char limit)
                    if len(content) <= 2000:
                        await channel.send(content)
                    else:
                        chunks = [content[i:i+2000] for i in range(0, len(content), 2000)]
                        for chunk in chunks:
                            await channel.send(chunk)
                    posted = True
                    logger.info(f"Posted to #{channel_name}")
                    await client.close()
                    return
        logger.error(f"Channel not found: {channel_name}")
        await client.close()

    try:
        await client.start(token)
    except:
        pass

    return posted


async def run_routine(routine_name: str, dry_run: bool = False) -> str:
    """
    Execute a routine.

    Args:
        routine_name: Name of the routine to run
        dry_run: If True, print output instead of posting to Discord

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

    # Post to Discord
    if routine.channel:
        # Map old Slack channel names to Discord
        channel_map = {
            "team-jpa": "general",  # or whatever your Discord channel is
        }
        discord_channel = channel_map.get(routine.channel, routine.channel)
        await post_to_discord(discord_channel, response)

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
