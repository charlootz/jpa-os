"""
jpa-os Slack Dispatcher

Listens for Slack events and routes them to the appropriate agent.
Uses Socket Mode (no public URL needed).

Usage:
    python -m engine.slack.dispatcher

Requires environment variables:
    SLACK_BOT_TOKEN - Bot User OAuth Token (xoxb-...)
    SLACK_APP_TOKEN - App-Level Token (xapp-...) for Socket Mode
"""

import os
import asyncio
import logging
from pathlib import Path

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    name="jpa-os"
)


def get_agent_name_from_bot_id(bot_id: str) -> str:
    """
    Map Slack bot ID to agent name.
    For now, we only have Vega. Later this will read from config.
    """
    # TODO: Read from census or config
    # For now, default to Vega
    return "Vega"


async def run_agent_and_respond(agent_name: str, message: str, say, thread_ts: str = None):
    """
    Spawn an agent, get response, post to Slack.
    """
    try:
        # Import here to avoid circular imports
        from engine.agents.base import run_vega_streaming

        # Acknowledge we're working on it
        thinking_msg = await say(
            text=f"_thinking..._",
            thread_ts=thread_ts
        )

        # Collect the full response
        full_response = ""
        async for chunk in run_vega_streaming(message):
            full_response += chunk

        # Update the message with the response
        await app.client.chat_update(
            channel=thinking_msg["channel"],
            ts=thinking_msg["ts"],
            text=full_response
        )

    except Exception as e:
        logger.error(f"Error running agent: {e}")
        await say(
            text=f"Sorry, I encountered an error: {str(e)}",
            thread_ts=thread_ts
        )


@app.event("app_mention")
async def handle_mention(event, say):
    """
    Handle @mentions of the bot.
    """
    logger.info(f"Received mention: {event}")

    # Extract the message text (remove the bot mention)
    text = event.get("text", "")
    # Remove the <@BOT_ID> mention from the text
    import re
    text = re.sub(r"<@[A-Z0-9]+>\s*", "", text).strip()

    if not text:
        await say(
            text="How can I help?",
            thread_ts=event.get("thread_ts") or event.get("ts")
        )
        return

    # Get thread_ts for threading
    thread_ts = event.get("thread_ts") or event.get("ts")

    # Run the agent
    await run_agent_and_respond(
        agent_name="Vega",
        message=text,
        say=say,
        thread_ts=thread_ts
    )


# Channels where Vega listens without @mention
ALWAYS_LISTEN_CHANNELS = [
    "team-jpa",  # Channel names (will be resolved to IDs)
]

# Cache for channel name -> ID mapping
_channel_id_cache = {}


async def get_channel_id(channel_name: str) -> str | None:
    """Get channel ID from channel name."""
    if channel_name in _channel_id_cache:
        return _channel_id_cache[channel_name]

    try:
        result = await app.client.conversations_list(types="public_channel,private_channel")
        for channel in result.get("channels", []):
            if channel.get("name") == channel_name:
                _channel_id_cache[channel_name] = channel["id"]
                return channel["id"]
    except Exception as e:
        logger.error(f"Error looking up channel {channel_name}: {e}")

    return None


async def is_always_listen_channel(channel_id: str) -> bool:
    """Check if this channel is one we always listen to."""
    for channel_name in ALWAYS_LISTEN_CHANNELS:
        cid = await get_channel_id(channel_name)
        if cid == channel_id:
            return True
    return False


@app.event("message")
async def handle_message(event, say):
    """
    Handle messages - DMs and monitored channels.
    """
    # Ignore bot messages to prevent loops
    if event.get("bot_id"):
        return

    # Ignore message edits, deletes, etc.
    if event.get("subtype"):
        return

    text = event.get("text", "").strip()
    if not text:
        return

    channel_id = event.get("channel")
    channel_type = event.get("channel_type")

    # Handle DMs
    if channel_type == "im":
        logger.info(f"Received DM: {event}")
        await run_agent_and_respond(
            agent_name="Vega",
            message=text,
            say=say,
            thread_ts=event.get("thread_ts")
        )
        return

    # Handle monitored channels (no @mention needed)
    if await is_always_listen_channel(channel_id):
        logger.info(f"Received message in monitored channel: {event}")
        await run_agent_and_respond(
            agent_name="Vega",
            message=text,
            say=say,
            thread_ts=event.get("thread_ts") or event.get("ts")
        )


async def main():
    """
    Start the Slack dispatcher.
    """
    # Check for required tokens
    if not os.environ.get("SLACK_BOT_TOKEN"):
        logger.error("SLACK_BOT_TOKEN not set")
        logger.error("Get it from: api.slack.com/apps > OAuth & Permissions > Bot User OAuth Token")
        return

    if not os.environ.get("SLACK_APP_TOKEN"):
        logger.error("SLACK_APP_TOKEN not set")
        logger.error("Get it from: api.slack.com/apps > Basic Information > App-Level Tokens")
        logger.error("Create one with 'connections:write' scope")
        return

    handler = AsyncSocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))

    logger.info("Starting jpa-os Slack dispatcher...")
    logger.info("Vega is online and listening.")

    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
