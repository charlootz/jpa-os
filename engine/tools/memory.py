"""
Memory tools for jpa-os agents.

These tools allow agents to store and recall memories.
"""

import json
from typing import Optional


def remember(content: str, category: str = "general") -> str:
    """
    Store a memory. Use this to remember important observations, learnings,
    preferences, or context that should persist across sessions.

    Args:
        content: What to remember (be specific and clear)
        category: One of: jpa_preferences, hive_learnings, project_context,
                  people, operational, general

    Returns:
        Confirmation of stored memory
    """
    from engine.memory.vega import get_memory

    valid_categories = [
        "jpa_preferences",
        "hive_learnings",
        "project_context",
        "people",
        "operational",
        "general"
    ]

    if category not in valid_categories:
        category = "general"

    mem = get_memory()
    result = mem.remember(content, category=category)

    return f"Stored memory in '{category}': {content[:100]}..."


def recall(query: str, category: Optional[str] = None, limit: int = 5) -> str:
    """
    Search memories for relevant information.

    Args:
        query: What to search for
        category: Optional category to filter by
        limit: Max number of results (default 5)

    Returns:
        Relevant memories as formatted text
    """
    from engine.memory.vega import get_memory

    mem = get_memory()
    results = mem.recall(query, category=category, limit=limit)

    if not results:
        return "No memories found for that query."

    output = [f"Found {len(results)} memories:\n"]
    for i, m in enumerate(results, 1):
        memory_text = m.get("memory", "")
        cat = m.get("metadata", {}).get("category", "general")
        score = m.get("score", 0)
        output.append(f"{i}. [{cat}] {memory_text} (relevance: {score:.2f})")

    return "\n".join(output)


def list_memories(category: Optional[str] = None) -> str:
    """
    List all stored memories, optionally filtered by category.

    Args:
        category: Optional category to filter by

    Returns:
        All memories as formatted text
    """
    from engine.memory.vega import get_memory

    mem = get_memory()
    memories = mem.get_all(category=category)

    if not memories:
        return "No memories stored yet."

    output = [f"Total memories: {len(memories)}\n"]
    for m in memories:
        memory_text = m.get("memory", "")
        cat = m.get("metadata", {}).get("category", "general")
        output.append(f"[{cat}] {memory_text}")

    return "\n".join(output)
