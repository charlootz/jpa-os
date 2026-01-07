"""
Entry point for python -m engine.slack
"""

from engine.slack.dispatcher import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
