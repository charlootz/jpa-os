"""
Discord tools for jpa-os agents.

God mode over Discord. Vega can:
- Send messages as herself or any agent
- Create/manage channels
- Create agent identities (webhooks)
- Manage roles and permissions
- Upload files
- And more

Uses the bot token from .env.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional
import discord
from discord import Webhook
import aiohttp

# Paths
ROOT = Path(__file__).parent.parent.parent
WEBHOOKS_PATH = ROOT / "vault" / "hive" / "discord_webhooks.json"


def _get_token() -> str:
    """Get Discord bot token."""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN not set")
    return token


def _load_webhooks() -> dict:
    """Load webhook mappings."""
    if WEBHOOKS_PATH.exists():
        return json.loads(WEBHOOKS_PATH.read_text())
    return {}


def _save_webhooks(webhooks: dict):
    """Save webhook mappings."""
    WEBHOOKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    WEBHOOKS_PATH.write_text(json.dumps(webhooks, indent=2))


def _run_async(coro):
    """Run async code."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# ============================================================================
# Messaging
# ============================================================================

def send_message(channel_name: str, content: str, guild_name: str = None) -> str:
    """
    Send a message to a Discord channel as Vega.

    Args:
        channel_name: Name of the channel (e.g., "general")
        content: Message content
        guild_name: Server name (optional if only in one server)

    Returns:
        Confirmation
    """
    async def _send():
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            # Find the channel
            for guild in client.guilds:
                if guild_name and guild.name.lower() != guild_name.lower():
                    continue
                for channel in guild.text_channels:
                    if channel.name == channel_name:
                        await channel.send(content)
                        await client.close()
                        return
            await client.close()

        await client.start(_get_token())

    _run_async(_send())
    return f"Sent message to #{channel_name}"


def send_dm(username: str, content: str) -> str:
    """
    Send a DM to a user.

    Args:
        username: Discord username
        content: Message content

    Returns:
        Confirmation
    """
    async def _send():
        intents = discord.Intents.default()
        intents.members = True
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            for guild in client.guilds:
                for member in guild.members:
                    if member.name.lower() == username.lower() or str(member) == username:
                        await member.send(content)
                        await client.close()
                        return
            await client.close()

        await client.start(_get_token())

    _run_async(_send())
    return f"Sent DM to {username}"


def ping_jpa(content: str) -> str:
    """
    Send a DM to jpa. Use when you need jpa's attention.

    Args:
        content: Message content

    Returns:
        Confirmation
    """
    # Try common username patterns
    for username in ["jpa", "josephpalbanese", "joseph"]:
        try:
            return send_dm(username, content)
        except:
            continue
    return "Could not find jpa on Discord"


def send_as_agent(channel_name: str, agent_name: str, content: str, avatar_url: str = None) -> str:
    """
    Send a message as a specific agent using webhooks.
    Creates the webhook if it doesn't exist.

    Args:
        channel_name: Channel to send to
        agent_name: Name the message appears from
        content: Message content
        avatar_url: Optional avatar URL for the agent

    Returns:
        Confirmation
    """
    webhooks = _load_webhooks()

    async def _send():
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            for guild in client.guilds:
                for channel in guild.text_channels:
                    if channel.name == channel_name:
                        # Check for existing webhook
                        channel_key = str(channel.id)
                        webhook_url = None

                        if agent_name in webhooks and channel_key in webhooks[agent_name]:
                            webhook_url = webhooks[agent_name][channel_key]
                        else:
                            # Create new webhook
                            webhook = await channel.create_webhook(name=agent_name)
                            webhook_url = webhook.url

                            if agent_name not in webhooks:
                                webhooks[agent_name] = {}
                            webhooks[agent_name][channel_key] = webhook_url
                            _save_webhooks(webhooks)

                        # Send via webhook
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(webhook_url, session=session)
                            await webhook.send(
                                content=content,
                                username=agent_name,
                                avatar_url=avatar_url
                            )

                        await client.close()
                        return
            await client.close()

        await client.start(_get_token())

    _run_async(_send())
    return f"Sent message as {agent_name} to #{channel_name}"


# ============================================================================
# Agent Identity Management
# ============================================================================

def create_agent_identity(agent_name: str, channel_name: str = "general", avatar_url: str = None) -> str:
    """
    Create a Discord identity (webhook) for a new agent.
    Call this when spawning a new agent so they can post as themselves.

    Args:
        agent_name: The agent's name
        channel_name: Initial channel to create webhook in
        avatar_url: Optional avatar URL

    Returns:
        Confirmation with webhook info
    """
    webhooks = _load_webhooks()

    async def _create():
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            for guild in client.guilds:
                for channel in guild.text_channels:
                    if channel.name == channel_name:
                        webhook = await channel.create_webhook(
                            name=agent_name,
                            reason=f"jpa-os agent: {agent_name}"
                        )

                        if agent_name not in webhooks:
                            webhooks[agent_name] = {}
                        webhooks[agent_name][str(channel.id)] = webhook.url
                        _save_webhooks(webhooks)

                        await client.close()
                        return
            await client.close()

        await client.start(_get_token())

    _run_async(_create())
    return f"Created Discord identity for {agent_name} in #{channel_name}"


def list_agent_identities() -> str:
    """
    List all agent identities (webhooks) we've created.

    Returns:
        List of agents and their channels
    """
    webhooks = _load_webhooks()

    if not webhooks:
        return "No agent identities created yet."

    output = ["Agent Discord Identities:\n"]
    for agent, channels in webhooks.items():
        output.append(f"  {agent}: {len(channels)} channel(s)")

    return "\n".join(output)


# ============================================================================
# Channel Management
# ============================================================================

def create_channel(name: str, category: str = None, topic: str = "", private: bool = False) -> str:
    """
    Create a new Discord channel.

    Args:
        name: Channel name
        category: Category to put it in (optional)
        topic: Channel topic
        private: Make it private

    Returns:
        Confirmation
    """
    async def _create():
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            for guild in client.guilds:
                # Find category if specified
                cat = None
                if category:
                    for c in guild.categories:
                        if c.name.lower() == category.lower():
                            cat = c
                            break

                # Create channel
                overwrites = {}
                if private:
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        guild.me: discord.PermissionOverwrite(read_messages=True)
                    }

                channel = await guild.create_text_channel(
                    name=name,
                    category=cat,
                    topic=topic,
                    overwrites=overwrites if private else None
                )

                await client.close()
                return
            await client.close()

        await client.start(_get_token())

    _run_async(_create())
    return f"Created channel #{name}"


def delete_channel(name: str) -> str:
    """
    Delete a Discord channel.

    Args:
        name: Channel name

    Returns:
        Confirmation
    """
    async def _delete():
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            for guild in client.guilds:
                for channel in guild.text_channels:
                    if channel.name == name:
                        await channel.delete(reason="Deleted by jpa-os")
                        await client.close()
                        return
            await client.close()

        await client.start(_get_token())

    _run_async(_delete())
    return f"Deleted channel #{name}"


def list_channels() -> str:
    """
    List all channels in the server.

    Returns:
        Channel list
    """
    result = []

    async def _list():
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            for guild in client.guilds:
                result.append(f"**{guild.name}**\n")
                for category in guild.categories:
                    result.append(f"  {category.name}/")
                    for channel in category.text_channels:
                        result.append(f"    #{channel.name}")
                # Uncategorized channels
                for channel in guild.text_channels:
                    if channel.category is None:
                        result.append(f"  #{channel.name}")
            await client.close()

        await client.start(_get_token())

    _run_async(_list())
    return "\n".join(result) if result else "No channels found"


def set_channel_topic(channel_name: str, topic: str) -> str:
    """
    Set a channel's topic.

    Args:
        channel_name: Channel name
        topic: New topic

    Returns:
        Confirmation
    """
    async def _set():
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            for guild in client.guilds:
                for channel in guild.text_channels:
                    if channel.name == channel_name:
                        await channel.edit(topic=topic)
                        await client.close()
                        return
            await client.close()

        await client.start(_get_token())

    _run_async(_set())
    return f"Set topic for #{channel_name}"


# ============================================================================
# Role Management
# ============================================================================

def create_role(name: str, color: str = None, permissions: list = None) -> str:
    """
    Create a new role.

    Args:
        name: Role name
        color: Hex color (e.g., "#FF0000")
        permissions: List of permission names

    Returns:
        Confirmation
    """
    async def _create():
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            for guild in client.guilds:
                role_color = discord.Color.default()
                if color:
                    role_color = discord.Color(int(color.lstrip("#"), 16))

                await guild.create_role(name=name, color=role_color)
                await client.close()
                return
            await client.close()

        await client.start(_get_token())

    _run_async(_create())
    return f"Created role: {name}"


def assign_role(username: str, role_name: str) -> str:
    """
    Assign a role to a user.

    Args:
        username: Discord username
        role_name: Role to assign

    Returns:
        Confirmation
    """
    async def _assign():
        intents = discord.Intents.default()
        intents.members = True
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            for guild in client.guilds:
                role = discord.utils.get(guild.roles, name=role_name)
                if not role:
                    await client.close()
                    return

                for member in guild.members:
                    if member.name.lower() == username.lower():
                        await member.add_roles(role)
                        await client.close()
                        return
            await client.close()

        await client.start(_get_token())

    _run_async(_assign())
    return f"Assigned {role_name} to {username}"


# ============================================================================
# Reading
# ============================================================================

def read_channel(channel_name: str, limit: int = 10) -> str:
    """
    Read recent messages from a channel.

    Args:
        channel_name: Channel name
        limit: Number of messages

    Returns:
        Messages
    """
    messages = []

    async def _read():
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            for guild in client.guilds:
                for channel in guild.text_channels:
                    if channel.name == channel_name:
                        async for msg in channel.history(limit=limit):
                            messages.append(f"[{msg.author.name}] {msg.content[:200]}")
                        await client.close()
                        return
            await client.close()

        await client.start(_get_token())

    _run_async(_read())

    if not messages:
        return f"No messages found in #{channel_name}"

    return f"Last {len(messages)} messages in #{channel_name}:\n" + "\n".join(reversed(messages))


# ============================================================================
# Server Info
# ============================================================================

def server_info() -> str:
    """
    Get info about the Discord server.

    Returns:
        Server information
    """
    info = []

    async def _info():
        intents = discord.Intents.default()
        intents.members = True
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            for guild in client.guilds:
                info.append(f"**{guild.name}**")
                info.append(f"Members: {guild.member_count}")
                info.append(f"Channels: {len(guild.text_channels)} text, {len(guild.voice_channels)} voice")
                info.append(f"Roles: {len(guild.roles)}")
                info.append(f"Owner: {guild.owner}")
            await client.close()

        await client.start(_get_token())

    _run_async(_info())
    return "\n".join(info) if info else "No server info found"
