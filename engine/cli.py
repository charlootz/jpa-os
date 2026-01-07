"""
CLI for jpa-os — Talk to Vega.

Usage:
    python -m engine.cli "what's going on"           # One-shot
    python -m engine.cli                             # Interactive TUI
    python -m engine.cli --simple                    # Simple interactive mode
    python -m engine.cli --autonomous "task"         # Autonomous mode with hooks
"""

import argparse
import sys
from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="jpa-os — Talk to Vega")
    parser.add_argument("task", nargs="?", help="What you want Vega to do (omit for interactive)")
    parser.add_argument("--simple", "-s", action="store_true", help="Simple interactive mode (no TUI)")
    parser.add_argument("--autonomous", "-a", action="store_true", help="Autonomous mode with hooks and work queue")

    args = parser.parse_args()

    if args.autonomous and args.task:
        # Autonomous mode with task
        from engine.agents.base import run_autonomous
        print("Vega (autonomous): ", end="", flush=True)
        result = run_autonomous(args.task)
        print(result)

    elif args.task:
        # One-shot mode
        from engine.agents.base import run
        print("Vega: ", end="", flush=True)
        result = run(args.task)
        print(result)

    elif args.simple:
        # Simple interactive mode
        from engine.agents.base import run
        print("jpa-os — Talk to Vega")
        print("Type 'quit' or 'exit' to leave\n")

        while True:
            try:
                message = input("jpa: ").strip()
                if message.lower() in ["quit", "exit", "q"]:
                    print("Pro uno vincimus.")
                    break
                if not message:
                    continue

                print("Vega: ", end="", flush=True)
                result = run(message)
                print(result)
                print()

            except KeyboardInterrupt:
                print("\nPro uno vincimus.")
                break
            except EOFError:
                break

    else:
        # TUI mode
        try:
            from engine.tui import main as tui_main
            tui_main()
        except ImportError:
            print("Textual not installed. Use --simple for basic mode.")
            print("Install with: pip install textual")
            sys.exit(1)


if __name__ == "__main__":
    main()
