"""
jpa-os Main Entry Point

Runs both the Discord dispatcher (for receiving messages) and the scheduler
(for autonomous routines) in parallel.

Usage:
    python -m engine.main

This is what Railway should run.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

from engine.scheduler.routines import ROUTINES
from engine.scheduler.runner import run_routine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Timezone
TIMEZONE = ZoneInfo("America/New_York")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Track last run times for routines
last_run = {}


async def run_agent_and_respond(message: str, channel: discord.TextChannel, reference=None):
    """Run Vega and respond in Discord."""
    try:
        from engine.agents.base import run_vega_streaming

        thinking_msg = await channel.send("_thinking..._", reference=reference, mention_author=False)

        full_response = ""
        async for chunk in run_vega_streaming(message):
            full_response += chunk

        if len(full_response) <= 2000:
            await thinking_msg.edit(content=full_response)
        else:
            await thinking_msg.edit(content=full_response[:2000])
            remaining = full_response[2000:]
            while remaining:
                chunk = remaining[:2000]
                remaining = remaining[2000:]
                await channel.send(chunk)

    except Exception as e:
        logger.error(f"Error running agent: {e}")
        await channel.send(f"Sorry, I encountered an error: {str(e)}")


@bot.event
async def on_ready():
    """Called when bot is ready."""
    logger.info(f"Bot is ready! Logged in as {bot.user}")
    logger.info(f"Connected to {len(bot.guilds)} guild(s)")

    # Start the scheduler
    if not scheduler_check.is_running():
        scheduler_check.start()
        logger.info("Scheduler started")

    # Set status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="the hive"
        )
    )


@bot.event
async def on_message(message: discord.Message):
    """Handle incoming messages."""
    if message.author == bot.user or message.author.bot:
        return

    is_mentioned = bot.user in message.mentions
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_general = hasattr(message.channel, 'name') and message.channel.name in ["general", "team-jpa"]

    if is_mentioned or is_dm or is_general:
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()

        if not content:
            await message.channel.send("How can I help?", reference=message)
            return

        logger.info(f"Processing: {content[:50]}...")
        await run_agent_and_respond(content, message.channel, reference=message)

    await bot.process_commands(message)


@tasks.loop(minutes=1)
async def scheduler_check():
    """Check if any routines should run."""
    from croniter import croniter

    now = datetime.now(TIMEZONE)
    current_minute = now.strftime("%Y-%m-%d %H:%M")

    for routine in ROUTINES:
        if not routine.enabled:
            continue

        cron = croniter(routine.schedule, now.replace(second=0, microsecond=0) - timedelta(minutes=1))
        next_run = cron.get_next(datetime)

        if next_run.strftime("%Y-%m-%d %H:%M") == current_minute:
            if last_run.get(routine.name) != current_minute:
                logger.info(f"Triggering routine: {routine.name}")
                last_run[routine.name] = current_minute

                try:
                    # Run the routine
                    await run_routine(routine.name)
                    logger.info(f"Routine {routine.name} completed")
                except Exception as e:
                    logger.error(f"Routine {routine.name} failed: {e}")


@scheduler_check.before_loop
async def before_scheduler():
    """Wait for bot to be ready before starting scheduler."""
    await bot.wait_until_ready()


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


@bot.command(name="status")
async def status(ctx):
    now = datetime.now(TIMEZONE)
    await ctx.send(f"**Vega Status**\nOnline since boot\nTime: {now.strftime('%I:%M %p %Z')}\nRoutines: {len([r for r in ROUTINES if r.enabled])} active")


@bot.command(name="routines")
async def list_routines(ctx):
    output = ["**Scheduled Routines:**"]
    for r in ROUTINES:
        status = "✓" if r.enabled else "✗"
        output.append(f"{status} `{r.name}`: {r.schedule}")
    await ctx.send("\n".join(output))


@bot.command(name="run")
async def run_now(ctx, routine_name: str):
    """Manually trigger a routine."""
    try:
        await ctx.send(f"Running `{routine_name}`...")
        await run_routine(routine_name)
        await ctx.send(f"✓ `{routine_name}` completed")
    except Exception as e:
        await ctx.send(f"✗ Error: {e}")


async def main():
    """Start everything."""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not set")
        return

    logger.info("Starting jpa-os...")
    logger.info(f"Loaded {len(ROUTINES)} routines")

    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
