"""
CLI for jpa-os agents.

Usage:
    python -m engine.cli "what do you know about me"
    python -m engine.cli --project custom-records "what should I focus on"
"""

import argparse
from dotenv import load_dotenv

load_dotenv()

from engine.agents.base import run


def main():
    parser = argparse.ArgumentParser(description="jpa-os agent CLI")
    parser.add_argument("task", help="What you want the agent to do")
    parser.add_argument("--project", "-p", help="Project context (e.g., custom-records)")
    
    args = parser.parse_args()
    
    result = run(args.task, project=args.project)
    print(result)


if __name__ == "__main__":
    main()