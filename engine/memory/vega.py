"""
Vega's Memory System

Long-term memory for the COO. Stores observations, learnings, and context
that persist across sessions.

Uses mem0 hosted platform for simplicity and reliability.

Memory categories:
- jpa_preferences: How jpa likes things done, communication style, priorities
- hive_learnings: What works and doesn't in the hive
- project_context: Ongoing project state and decisions
- people: Info about people jpa works with
- operational: How to run jpa-os effectively
"""

import os
from datetime import datetime
import pytz
from typing import Optional
from mem0 import MemoryClient


class VegaMemory:
    """
    Vega's memory interface.

    This is how I remember things across sessions.
    Uses mem0 hosted platform.
    """

    # Memory categories for organization
    CATEGORIES = [
        "jpa_preferences",    # How jpa likes things
        "hive_learnings",     # What works in jpa-os
        "project_context",    # Project state and decisions
        "people",             # People jpa works with
        "operational",        # How to run things
        "general",            # Everything else
    ]

    def __init__(self):
        """Initialize memory system with hosted mem0."""
        api_key = os.getenv("MEM0_API_KEY")
        if not api_key:
            raise ValueError("MEM0_API_KEY not set in environment")

        self.client = MemoryClient(api_key=api_key)
        self.agent_id = "vega"
        self.user_id = "jpa"  # The one we serve

    def remember(
        self,
        content: str,
        category: str = "general",
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Store a memory.

        Args:
            content: What to remember
            category: One of CATEGORIES
            metadata: Additional context

        Returns:
            Memory storage result
        """
        meta = metadata or {}
        meta["category"] = category
        meta["timestamp"] = datetime.now(pytz.timezone("America/New_York")).isoformat()

        result = self.client.add(
            content,
            agent_id=self.agent_id,
            user_id=self.user_id,
            metadata=meta
        )

        return result

    def recall(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> list:
        """
        Search memories.

        Args:
            query: What to search for
            category: Filter by category (optional)
            limit: Max results

        Returns:
            List of relevant memories
        """
        # Platform API requires filters dict
        filters = {"user_id": self.user_id}

        results = self.client.search(
            query,
            filters=filters,
            limit=limit,
        )

        # Handle both list and dict response formats
        if isinstance(results, list):
            memories = results
        else:
            memories = results.get("results", results.get("memories", []))

        # Filter by category in post-processing if specified
        if category:
            memories = [m for m in memories if m.get("metadata", {}).get("category") == category]

        return memories

    def get_all(self, category: Optional[str] = None) -> list:
        """
        Get all memories, optionally filtered by category.
        """
        # Platform API requires filters dict
        filters = {"user_id": self.user_id}

        results = self.client.get_all(filters=filters)

        # Handle both list and dict response formats
        if isinstance(results, list):
            memories = results
        else:
            memories = results.get("results", results.get("memories", []))

        # Filter by category in post-processing if specified
        if category:
            memories = [m for m in memories if m.get("metadata", {}).get("category") == category]

        return memories

    def forget(self, memory_id: str) -> bool:
        """
        Delete a specific memory.
        """
        try:
            self.client.delete(memory_id)
            return True
        except Exception:
            return False

    def get_context_for_conversation(self, topic: str = None) -> str:
        """
        Build a context string for injection into conversations.

        This pulls relevant memories to include in the system prompt
        or conversation context.
        """
        sections = []

        # Always include jpa preferences
        prefs = self.recall("jpa preferences style", category="jpa_preferences", limit=3)
        if prefs:
            sections.append("## What I Know About jpa")
            for mem in prefs:
                sections.append(f"- {mem.get('memory', '')}")

        # If there's a topic, pull relevant memories
        if topic:
            relevant = self.recall(topic, limit=5)
            if relevant:
                sections.append(f"\n## Relevant Context")
                for mem in relevant:
                    sections.append(f"- {mem.get('memory', '')}")

        # Include recent operational learnings
        ops = self.recall("how to operate effectively", category="operational", limit=2)
        if ops:
            sections.append("\n## Operational Notes")
            for mem in ops:
                sections.append(f"- {mem.get('memory', '')}")

        return "\n".join(sections) if sections else ""


# Singleton instance
_memory_instance = None

def get_memory() -> VegaMemory:
    """Get the singleton memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = VegaMemory()
    return _memory_instance


# Convenience functions
def remember(content: str, category: str = "general", metadata: dict = None) -> dict:
    """Store a memory."""
    return get_memory().remember(content, category, metadata)


def recall(query: str, category: str = None, limit: int = 5) -> list:
    """Search memories."""
    return get_memory().recall(query, category, limit)


def get_context(topic: str = None) -> str:
    """Get context for conversation."""
    return get_memory().get_context_for_conversation(topic)
