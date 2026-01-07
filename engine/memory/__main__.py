"""
Memory CLI for jpa-os.

Usage:
    python -m engine.memory add "content" [--category cat]
    python -m engine.memory search "query" [--category cat] [--limit n]
    python -m engine.memory list [--category cat]
    python -m engine.memory forget <memory_id>
    python -m engine.memory categories
"""

import argparse
import json
import sys
from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Vega's Memory System")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add memory
    add_parser = subparsers.add_parser("add", help="Store a memory")
    add_parser.add_argument("content", help="What to remember")
    add_parser.add_argument("--category", "-c", default="general", help="Memory category")

    # Search memories
    search_parser = subparsers.add_parser("search", help="Search memories")
    search_parser.add_argument("query", help="What to search for")
    search_parser.add_argument("--category", "-c", help="Filter by category")
    search_parser.add_argument("--limit", "-n", type=int, default=5, help="Max results")

    # List all memories
    list_parser = subparsers.add_parser("list", help="List all memories")
    list_parser.add_argument("--category", "-c", help="Filter by category")

    # Forget a memory
    forget_parser = subparsers.add_parser("forget", help="Delete a memory")
    forget_parser.add_argument("memory_id", help="ID of memory to delete")

    # Show categories
    subparsers.add_parser("categories", help="Show available categories")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Import here to avoid slow startup
    from engine.memory.vega import VegaMemory

    memory = VegaMemory()

    if args.command == "add":
        result = memory.remember(args.content, category=args.category)
        print(f"Stored: {args.content[:50]}...")
        print(f"Category: {args.category}")
        if "results" in result:
            for r in result["results"]:
                print(f"ID: {r.get('id', 'unknown')}")

    elif args.command == "search":
        results = memory.recall(args.query, category=args.category, limit=args.limit)
        if not results:
            print("No memories found.")
        else:
            print(f"Found {len(results)} memories:\n")
            for i, mem in enumerate(results, 1):
                print(f"{i}. {mem.get('memory', '')}")
                print(f"   Score: {mem.get('score', 0):.2f}")
                print(f"   ID: {mem.get('id', 'unknown')}")
                print()

    elif args.command == "list":
        memories = memory.get_all(category=args.category)
        if not memories:
            print("No memories stored yet.")
        else:
            print(f"Total memories: {len(memories)}\n")
            for mem in memories:
                cat = mem.get("metadata", {}).get("category", "general")
                print(f"[{cat}] {mem.get('memory', '')[:80]}")
                print(f"  ID: {mem.get('id', 'unknown')}")
                print()

    elif args.command == "forget":
        success = memory.forget(args.memory_id)
        if success:
            print(f"Forgot memory: {args.memory_id}")
        else:
            print(f"Failed to forget memory: {args.memory_id}")

    elif args.command == "categories":
        print("Available memory categories:\n")
        for cat in memory.CATEGORIES:
            desc = {
                "jpa_preferences": "How jpa likes things done",
                "hive_learnings": "What works in jpa-os",
                "project_context": "Project state and decisions",
                "people": "People jpa works with",
                "operational": "How to run things",
                "general": "Everything else",
            }
            print(f"  {cat}: {desc.get(cat, '')}")


if __name__ == "__main__":
    main()
