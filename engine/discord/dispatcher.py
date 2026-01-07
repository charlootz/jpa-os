"""
jpa-os Discord Dispatcher

The master bot that runs the Discord server.
Listens for messages, routes to agents, manages agent identities via webhooks.

Usage:
    python -m engine.discord.dispatcher

Requires:
    DISCORD_TOKEN - Bot token from discord.com/developers
"""

import os
import asyncio
import logging
import json
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
ROOT = Path(__file__).parent.parent.parent
WEBHOOKS_PATH = ROOT / "vault" / "hive" / "discord_webhooks.json"

# Bot intents - we need message content
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# The master bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Webhook cache: {agent_name: {channel_id: webhook_url}}
_webhook_cache = {}


def load_webhooks() -> dict:
    """Load webhook mappings from disk."""
    if WEBHOOKS_PATH.exists():
        return json.loads(WEBHOOKS_PATH.read_text())
    return {}


def save_webhooks(webhooks: dict):
    """Save webhook mappings to disk."""
    WEBHOOKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    WEBHOOKS_PATH.write_text(json.dumps(webhooks, indent=2))


# Channels where Vega listens to all messages (no @mention needed)
ALWAYS_LISTEN_CHANNELS = [
    "team-jpa",
    "general",
]

# jpa's Discord user ID (will be set on first message)
JPA_USER_ID = None


async def run_agent_and_respond(
    agent_name: str,
    message: str,
    channel: discord.TextChannel,
    reference: discord.Message = None
):
    """
    Spawn an agent, get response, post to Discord.
    """
    try:
        from engine.agents.base import run_vega_streaming

        # Send thinking indicator
        thinking_msg = await channel.send(
            "_thinking..._",
            reference=reference,
            mention_author=False
        )

        # Collect the full response
        full_response = ""
        async for chunk in run_vega_streaming(message):
            full_response += chunk

        # Edit the message with the response
        # Discord has 2000 char limit, split if needed
        if len(full_response) <= 2000:
            await thinking_msg.edit(content=full_response)
        else:
            # Split into chunks
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

    # Load webhook cache
    global _webhook_cache
    _webhook_cache = load_webhooks()

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
    global JPA_USER_ID

    # Ignore own messages
    if message.author == bot.user:
        return

    # Ignore other bots
    if message.author.bot:
        return

    # Track jpa's user ID from first message
    if JPA_USER_ID is None and message.author.name.lower() in ["jpa", "josephpalbanese", "joseph"]:
        JPA_USER_ID = message.author.id
        logger.info(f"Learned jpa's Discord ID: {JPA_USER_ID}")

    # Check if bot is mentioned
    is_mentioned = bot.user in message.mentions

    # Check if in always-listen channel
    is_always_listen = message.channel.name in ALWAYS_LISTEN_CHANNELS

    # Check if DM
    is_dm = isinstance(message.channel, discord.DMChannel)

    # Respond if mentioned, DM, or in always-listen channel
    if is_mentioned or is_dm or is_always_listen:
        # Clean up the message (remove bot mention)
        content = message.content
        if is_mentioned:
            content = content.replace(f"<@{bot.user.id}>", "").strip()

        if not content:
            await message.channel.send("How can I help?", reference=message)
            return

        logger.info(f"Processing message from {message.author}: {content[:50]}...")

        await run_agent_and_respond(
            agent_name="Vega",
            message=content,
            channel=message.channel,
            reference=message
        )

    # Process commands
    await bot.process_commands(message)


# ============================================================================
# Agent Identity Management (Webhooks)
# ============================================================================

async def create_agent_webhook(
    channel: discord.TextChannel,
    agent_name: str,
    avatar_url: Optional[str] = None
) -> str:
    """
    Create a webhook for an agent in a channel.
    Returns the webhook URL.
    """
    # Check if we already have one
    if agent_name in _webhook_cache:
        if str(channel.id) in _webhook_cache[agent_name]:
            return _webhook_cache[agent_name][str(channel.id)]

    # Create new webhook
    webhook = await channel.create_webhook(
        name=agent_name,
        reason=f"jpa-os agent identity for {agent_name}"
    )

    # Cache it
    if agent_name not in _webhook_cache:
        _webhook_cache[agent_name] = {}
    _webhook_cache[agent_name][str(channel.id)] = webhook.url

    # Save to disk
    save_webhooks(_webhook_cache)

    logger.info(f"Created webhook for {agent_name} in #{channel.name}")
    return webhook.url


async def send_as_agent(
    channel: discord.TextChannel,
    agent_name: str,
    content: str,
    avatar_url: Optional[str] = None
):
    """
    Send a message as a specific agent using webhooks.
    """
    webhook_url = await create_agent_webhook(channel, agent_name, avatar_url)

    async with discord.Webhook.from_url(webhook_url, client=bot) as webhook:
        await webhook.send(
            content=content,
            username=agent_name,
            avatar_url=avatar_url
        )


# ============================================================================
# Commands
# ============================================================================

@bot.command(name="ping")
async def ping(ctx):
    """Check if bot is alive."""
    await ctx.send(f"Pong! Latency: {round(bot.latency * 1000)}ms")


@bot.command(name="agents")
async def list_agents(ctx):
    """List all agents in the hive."""
    census_path = ROOT / "vault" / "hive" / "census.md"
    if census_path.exists():
        content = census_path.read_text()
        await ctx.send(f"```\n{content}\n```")
    else:
        await ctx.send("No census found.")


@bot.command(name="status")
async def status(ctx):
    """Show jpa-os status."""
    from engine.memory.vega import get_memory
    try:
        mem = get_memory()
        memories = mem.get_all()
        memory_count = len(memories)
    except:
        memory_count = "?"

    status_msg = f"""**jpa-os Status**
Bot: {bot.user.name} (online)
Guilds: {len(bot.guilds)}
Memories: {memory_count}
Webhooks: {sum(len(v) for v in _webhook_cache.values())}
"""
    await ctx.send(status_msg)


# ============================================================================
# Main
# ============================================================================

async def main():
    """Start the Discord dispatcher."""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not set")
        return

    logger.info("Starting jpa-os Discord dispatcher...")
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
