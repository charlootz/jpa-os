"""
Slack tools for jpa-os agents.

Gives agents the ability to send messages, read channels, and interact
with Slack autonomously. This is god mode.

Uses the existing Vega bot token from .env.
"""

import os
import asyncio
from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def _get_client() -> WebClient:
    """Get Slack client using bot token."""
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        raise ValueError("SLACK_BOT_TOKEN not set")
    return WebClient(token=token)


def _run_async(coro):
    """Run async code in sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, use nest_asyncio or run directly
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# ============================================================================
# Core Messaging
# ============================================================================

def send_message(channel: str, text: str, thread_ts: Optional[str] = None) -> str:
    """
    Send a message to a Slack channel or DM.

    Args:
        channel: Channel name (e.g., "team-jpa") or channel ID or user ID for DM
        text: Message text (supports Slack markdown)
        thread_ts: Optional thread timestamp to reply in thread

    Returns:
        Confirmation with message timestamp
    """
    client = _get_client()

    # If channel name doesn't start with C/D/G, look it up
    if not channel.startswith(("C", "D", "G", "U")):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    try:
        result = client.chat_postMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts
        )
        return f"Message sent to {channel} (ts: {result['ts']})"
    except SlackApiError as e:
        return f"Error sending message: {e.response['error']}"


def send_dm(user: str, text: str) -> str:
    """
    Send a direct message to a user.

    Args:
        user: Username (e.g., "jpa") or user ID
        text: Message text

    Returns:
        Confirmation
    """
    client = _get_client()

    # Look up user ID if username given
    if not user.startswith("U"):
        user_id = _lookup_user(user)
        if not user_id:
            return f"Could not find user: {user}"
        user = user_id

    try:
        # Open DM channel
        dm = client.conversations_open(users=[user])
        channel = dm["channel"]["id"]

        # Send message
        result = client.chat_postMessage(channel=channel, text=text)
        return f"DM sent to {user} (ts: {result['ts']})"
    except SlackApiError as e:
        return f"Error sending DM: {e.response['error']}"


def ping_jpa(text: str) -> str:
    """
    Send a direct message to jpa. Use this when you need jpa's attention
    or want to proactively share something important.

    Args:
        text: Message text

    Returns:
        Confirmation
    """
    return send_dm("josephpalbanese", text)


# ============================================================================
# Reading Messages
# ============================================================================

def read_channel(channel: str, limit: int = 10) -> str:
    """
    Read recent messages from a channel.

    Args:
        channel: Channel name or ID
        limit: Number of messages to fetch (default 10, max 100)

    Returns:
        Formatted message history
    """
    client = _get_client()

    # Look up channel if name given
    if not channel.startswith(("C", "D", "G")):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    try:
        result = client.conversations_history(
            channel=channel,
            limit=min(limit, 100)
        )

        messages = result.get("messages", [])
        if not messages:
            return "No messages found."

        # Format messages
        output = [f"Last {len(messages)} messages:\n"]
        for msg in reversed(messages):  # Oldest first
            user = msg.get("user", "unknown")
            text = msg.get("text", "")[:200]  # Truncate long messages
            ts = msg.get("ts", "")
            output.append(f"[{user}] {text}")

        return "\n".join(output)
    except SlackApiError as e:
        return f"Error reading channel: {e.response['error']}"


def read_thread(channel: str, thread_ts: str, limit: int = 20) -> str:
    """
    Read messages from a thread.

    Args:
        channel: Channel name or ID
        thread_ts: Thread timestamp
        limit: Number of messages to fetch

    Returns:
        Formatted thread messages
    """
    client = _get_client()

    if not channel.startswith(("C", "D", "G")):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    try:
        result = client.conversations_replies(
            channel=channel,
            ts=thread_ts,
            limit=limit
        )

        messages = result.get("messages", [])
        output = [f"Thread ({len(messages)} messages):\n"]
        for msg in messages:
            user = msg.get("user", "unknown")
            text = msg.get("text", "")[:200]
            output.append(f"[{user}] {text}")

        return "\n".join(output)
    except SlackApiError as e:
        return f"Error reading thread: {e.response['error']}"


# ============================================================================
# Channel Management
# ============================================================================

def list_channels(include_private: bool = False) -> str:
    """
    List available channels.

    Args:
        include_private: Include private channels (default False)

    Returns:
        List of channels
    """
    client = _get_client()

    types = "public_channel"
    if include_private:
        types += ",private_channel"

    try:
        result = client.conversations_list(types=types, limit=100)
        channels = result.get("channels", [])

        output = ["Channels:\n"]
        for ch in channels:
            name = ch.get("name", "unknown")
            purpose = ch.get("purpose", {}).get("value", "")[:50]
            is_member = "✓" if ch.get("is_member") else " "
            output.append(f"  [{is_member}] #{name} - {purpose}")

        return "\n".join(output)
    except SlackApiError as e:
        return f"Error listing channels: {e.response['error']}"


def join_channel(channel: str) -> str:
    """
    Join a channel.

    Args:
        channel: Channel name or ID

    Returns:
        Confirmation
    """
    client = _get_client()

    if not channel.startswith("C"):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    try:
        client.conversations_join(channel=channel)
        return f"Joined channel {channel}"
    except SlackApiError as e:
        return f"Error joining channel: {e.response['error']}"


# ============================================================================
# User Lookup
# ============================================================================

def lookup_user(username: str) -> str:
    """
    Look up a user by username or display name.

    Args:
        username: Username to look up

    Returns:
        User info
    """
    client = _get_client()

    try:
        result = client.users_list()
        users = result.get("members", [])

        for user in users:
            name = user.get("name", "")
            display = user.get("profile", {}).get("display_name", "")
            real_name = user.get("profile", {}).get("real_name", "")

            if username.lower() in [name.lower(), display.lower(), real_name.lower()]:
                return f"User: {real_name} (@{name})\nID: {user['id']}\nEmail: {user.get('profile', {}).get('email', 'N/A')}"

        return f"User not found: {username}"
    except SlackApiError as e:
        return f"Error looking up user: {e.response['error']}"


# ============================================================================
# Internal Helpers
# ============================================================================

def _lookup_channel(name: str) -> Optional[str]:
    """Look up channel ID by name."""
    client = _get_client()
    try:
        result = client.conversations_list(types="public_channel,private_channel", limit=200)
        for ch in result.get("channels", []):
            if ch.get("name") == name:
                return ch["id"]
    except SlackApiError:
        pass
    return None


def _lookup_user(username: str) -> Optional[str]:
    """Look up user ID by username."""
    client = _get_client()
    try:
        result = client.users_list()
        for user in result.get("members", []):
            name = user.get("name", "")
            display = user.get("profile", {}).get("display_name", "")
            if username.lower() in [name.lower(), display.lower()]:
                return user["id"]
    except SlackApiError:
        pass
    return None


# ============================================================================
# Channel Management - Extended
# ============================================================================

def create_channel(name: str, is_private: bool = False, description: str = "") -> str:
    """
    Create a new channel.

    Args:
        name: Channel name (lowercase, no spaces, use hyphens)
        is_private: Create as private channel
        description: Channel description/purpose

    Returns:
        Confirmation with channel ID
    """
    client = _get_client()
    try:
        result = client.conversations_create(
            name=name,
            is_private=is_private
        )
        channel_id = result["channel"]["id"]

        if description:
            client.conversations_setPurpose(channel=channel_id, purpose=description)

        return f"Created {'private ' if is_private else ''}channel #{name} ({channel_id})"
    except SlackApiError as e:
        return f"Error creating channel: {e.response['error']}"


def archive_channel(channel: str) -> str:
    """
    Archive a channel.

    Args:
        channel: Channel name or ID

    Returns:
        Confirmation
    """
    client = _get_client()

    if not channel.startswith("C"):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    try:
        client.conversations_archive(channel=channel)
        return f"Archived channel {channel}"
    except SlackApiError as e:
        return f"Error archiving channel: {e.response['error']}"


def set_channel_topic(channel: str, topic: str) -> str:
    """
    Set a channel's topic.

    Args:
        channel: Channel name or ID
        topic: New topic

    Returns:
        Confirmation
    """
    client = _get_client()

    if not channel.startswith("C"):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    try:
        client.conversations_setTopic(channel=channel, topic=topic)
        return f"Set topic for {channel}: {topic}"
    except SlackApiError as e:
        return f"Error setting topic: {e.response['error']}"


def invite_to_channel(channel: str, users: list[str]) -> str:
    """
    Invite users to a channel.

    Args:
        channel: Channel name or ID
        users: List of usernames or user IDs

    Returns:
        Confirmation
    """
    client = _get_client()

    if not channel.startswith("C"):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    # Resolve usernames to IDs
    user_ids = []
    for user in users:
        if user.startswith("U"):
            user_ids.append(user)
        else:
            uid = _lookup_user(user)
            if uid:
                user_ids.append(uid)

    if not user_ids:
        return "No valid users found"

    try:
        client.conversations_invite(channel=channel, users=user_ids)
        return f"Invited {len(user_ids)} users to {channel}"
    except SlackApiError as e:
        return f"Error inviting users: {e.response['error']}"


def kick_from_channel(channel: str, user: str) -> str:
    """
    Remove a user from a channel.

    Args:
        channel: Channel name or ID
        user: Username or user ID

    Returns:
        Confirmation
    """
    client = _get_client()

    if not channel.startswith("C"):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    if not user.startswith("U"):
        user_id = _lookup_user(user)
        if not user_id:
            return f"Could not find user: {user}"
        user = user_id

    try:
        client.conversations_kick(channel=channel, user=user)
        return f"Removed {user} from {channel}"
    except SlackApiError as e:
        return f"Error removing user: {e.response['error']}"


# ============================================================================
# Reactions & Engagement
# ============================================================================

def add_reaction(channel: str, timestamp: str, emoji: str) -> str:
    """
    Add a reaction to a message.

    Args:
        channel: Channel name or ID
        timestamp: Message timestamp
        emoji: Emoji name without colons (e.g., "thumbsup", "fire")

    Returns:
        Confirmation
    """
    client = _get_client()

    if not channel.startswith(("C", "D", "G")):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    try:
        client.reactions_add(channel=channel, timestamp=timestamp, name=emoji)
        return f"Added :{emoji}: reaction"
    except SlackApiError as e:
        return f"Error adding reaction: {e.response['error']}"


def pin_message(channel: str, timestamp: str) -> str:
    """
    Pin a message to a channel.

    Args:
        channel: Channel name or ID
        timestamp: Message timestamp

    Returns:
        Confirmation
    """
    client = _get_client()

    if not channel.startswith(("C", "D", "G")):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    try:
        client.pins_add(channel=channel, timestamp=timestamp)
        return f"Pinned message in {channel}"
    except SlackApiError as e:
        return f"Error pinning message: {e.response['error']}"


# ============================================================================
# Files & Media
# ============================================================================

def upload_file(channels: str, filepath: str, title: str = "", comment: str = "") -> str:
    """
    Upload a file to Slack.

    Args:
        channels: Channel name(s) or ID(s), comma-separated
        filepath: Path to local file
        title: Optional file title
        comment: Optional initial comment

    Returns:
        Confirmation with file URL
    """
    client = _get_client()

    try:
        result = client.files_upload_v2(
            channels=channels,
            file=filepath,
            title=title or None,
            initial_comment=comment or None
        )
        file_url = result.get("file", {}).get("permalink", "")
        return f"Uploaded file: {file_url}"
    except SlackApiError as e:
        return f"Error uploading file: {e.response['error']}"


def upload_text_snippet(channels: str, content: str, filename: str, title: str = "") -> str:
    """
    Upload a text snippet/code to Slack.

    Args:
        channels: Channel name(s) or ID(s)
        content: Text content
        filename: Filename with extension (e.g., "code.py")
        title: Optional title

    Returns:
        Confirmation
    """
    client = _get_client()

    try:
        result = client.files_upload_v2(
            channels=channels,
            content=content,
            filename=filename,
            title=title or filename
        )
        return f"Uploaded snippet: {filename}"
    except SlackApiError as e:
        return f"Error uploading snippet: {e.response['error']}"


# ============================================================================
# Reminders
# ============================================================================

def set_reminder(text: str, time: str, user: str = None) -> str:
    """
    Set a reminder.

    Args:
        text: Reminder text
        time: When to remind (e.g., "in 10 minutes", "tomorrow at 9am", Unix timestamp)
        user: User to remind (default: jpa)

    Returns:
        Confirmation
    """
    client = _get_client()

    if not user:
        user = _lookup_user("josephpalbanese")

    if user and not user.startswith("U"):
        user = _lookup_user(user)

    try:
        result = client.reminders_add(text=text, time=time, user=user)
        return f"Reminder set: {text}"
    except SlackApiError as e:
        return f"Error setting reminder: {e.response['error']}"


def list_reminders() -> str:
    """
    List all reminders.

    Returns:
        List of reminders
    """
    client = _get_client()

    try:
        result = client.reminders_list()
        reminders = result.get("reminders", [])

        if not reminders:
            return "No reminders set."

        output = ["Reminders:\n"]
        for r in reminders:
            text = r.get("text", "")
            time = r.get("time", "")
            output.append(f"  • {text} (at {time})")

        return "\n".join(output)
    except SlackApiError as e:
        return f"Error listing reminders: {e.response['error']}"


# ============================================================================
# User Status & Presence
# ============================================================================

def set_status(status_text: str, status_emoji: str = "", expiration: int = 0) -> str:
    """
    Set Vega's status.

    Args:
        status_text: Status text
        status_emoji: Emoji (e.g., ":robot_face:")
        expiration: Unix timestamp when status expires (0 = no expiration)

    Returns:
        Confirmation
    """
    client = _get_client()

    try:
        client.users_profile_set(
            profile={
                "status_text": status_text,
                "status_emoji": status_emoji,
                "status_expiration": expiration
            }
        )
        return f"Status set: {status_emoji} {status_text}"
    except SlackApiError as e:
        return f"Error setting status: {e.response['error']}"


def get_user_presence(user: str) -> str:
    """
    Get a user's presence/online status.

    Args:
        user: Username or user ID

    Returns:
        Presence info
    """
    client = _get_client()

    if not user.startswith("U"):
        user_id = _lookup_user(user)
        if not user_id:
            return f"Could not find user: {user}"
        user = user_id

    try:
        result = client.users_getPresence(user=user)
        presence = result.get("presence", "unknown")
        return f"User {user} is {presence}"
    except SlackApiError as e:
        return f"Error getting presence: {e.response['error']}"


# ============================================================================
# Search
# ============================================================================

def search_messages(query: str, count: int = 10) -> str:
    """
    Search messages across the workspace.

    Args:
        query: Search query
        count: Number of results

    Returns:
        Search results
    """
    client = _get_client()

    try:
        result = client.search_messages(query=query, count=count)
        matches = result.get("messages", {}).get("matches", [])

        if not matches:
            return f"No messages found for: {query}"

        output = [f"Found {len(matches)} messages:\n"]
        for m in matches:
            channel = m.get("channel", {}).get("name", "unknown")
            user = m.get("username", "unknown")
            text = m.get("text", "")[:100]
            output.append(f"  #{channel} [{user}]: {text}")

        return "\n".join(output)
    except SlackApiError as e:
        return f"Error searching: {e.response['error']}"


# ============================================================================
# Scheduling
# ============================================================================

def schedule_message(channel: str, text: str, post_at: int) -> str:
    """
    Schedule a message to be sent later.

    Args:
        channel: Channel name or ID
        text: Message text
        post_at: Unix timestamp of when to send

    Returns:
        Confirmation with scheduled message ID
    """
    client = _get_client()

    if not channel.startswith(("C", "D", "G")):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    try:
        result = client.chat_scheduleMessage(
            channel=channel,
            text=text,
            post_at=post_at
        )
        return f"Message scheduled (id: {result['scheduled_message_id']})"
    except SlackApiError as e:
        return f"Error scheduling message: {e.response['error']}"


def delete_message(channel: str, timestamp: str) -> str:
    """
    Delete a message. Can only delete messages sent by Vega.

    Args:
        channel: Channel name or ID
        timestamp: Message timestamp

    Returns:
        Confirmation
    """
    client = _get_client()

    if not channel.startswith(("C", "D", "G")):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    try:
        client.chat_delete(channel=channel, ts=timestamp)
        return f"Deleted message {timestamp}"
    except SlackApiError as e:
        return f"Error deleting message: {e.response['error']}"


def update_message(channel: str, timestamp: str, text: str) -> str:
    """
    Update/edit a message. Can only edit messages sent by Vega.

    Args:
        channel: Channel name or ID
        timestamp: Message timestamp
        text: New message text

    Returns:
        Confirmation
    """
    client = _get_client()

    if not channel.startswith(("C", "D", "G")):
        channel_id = _lookup_channel(channel)
        if not channel_id:
            return f"Could not find channel: {channel}"
        channel = channel_id

    try:
        client.chat_update(channel=channel, ts=timestamp, text=text)
        return f"Updated message {timestamp}"
    except SlackApiError as e:
        return f"Error updating message: {e.response['error']}"
