"""
Entry point for autonomous daemon.

Usage:
    python -m engine.autonomous              # Start daemon
    python -m engine.autonomous add "task"   # Add task to queue
    python -m engine.autonomous list         # List pending tasks
    python -m engine.autonomous clear        # Clear completed tasks
"""

import argparse
import asyncio
import sys

from dotenv import load_dotenv
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="jpa-os Autonomous Daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  (none)     Start the autonomous daemon
  add        Add a task to the work queue
  list       List all tasks in the queue
  pending    List pending tasks
  clear      Clear completed/failed tasks

Examples:
  python -m engine.autonomous
  python -m engine.autonomous add "Review today's meetings and summarize"
  python -m engine.autonomous add --priority high "Urgent: check on CI failures"
  python -m engine.autonomous list
"""
    )

    subparsers = parser.add_subparsers(dest='command')

    # Add task command
    add_parser = subparsers.add_parser('add', help='Add a task to the queue')
    add_parser.add_argument('description', help='Task description')
    add_parser.add_argument(
        '--priority', '-p',
        choices=['low', 'normal', 'high', 'urgent'],
        default='normal',
        help='Task priority'
    )
    add_parser.add_argument(
        '--source', '-s',
        default='cli',
        help='Source of the task'
    )

    # List command
    subparsers.add_parser('list', help='List all tasks')
    subparsers.add_parser('pending', help='List pending tasks')
    subparsers.add_parser('clear', help='Clear completed tasks')

    args = parser.parse_args()

    if args.command == 'add':
        from engine.autonomous.queue import WorkQueue, TaskPriority

        priority_map = {
            'low': TaskPriority.LOW,
            'normal': TaskPriority.NORMAL,
            'high': TaskPriority.HIGH,
            'urgent': TaskPriority.URGENT,
        }

        queue = WorkQueue()
        task = queue.add(
            description=args.description,
            priority=priority_map[args.priority],
            source=args.source,
        )
        print(f"Added task: {task.id}")
        print(f"Description: {task.description}")
        print(f"Priority: {task.priority.name}")

    elif args.command == 'list':
        from engine.autonomous.queue import WorkQueue

        queue = WorkQueue()
        tasks = queue.list_all()

        if not tasks:
            print("No tasks in queue")
            return

        print(f"{'ID':<30} {'Status':<12} {'Priority':<8} Description")
        print("-" * 80)
        for task in tasks:
            print(f"{task.id:<30} {task.status.value:<12} {task.priority.name:<8} {task.description[:30]}")

    elif args.command == 'pending':
        from engine.autonomous.queue import WorkQueue

        queue = WorkQueue()
        tasks = queue.list_pending()

        if not tasks:
            print("No pending tasks")
            return

        print(f"{'Priority':<8} Description")
        print("-" * 60)
        for task in sorted(tasks, key=lambda t: -t.priority.value):
            print(f"{task.priority.name:<8} {task.description}")

    elif args.command == 'clear':
        from engine.autonomous.queue import WorkQueue

        queue = WorkQueue()
        queue.clear_completed()
        print("Cleared completed and failed tasks")

    else:
        # No command = start daemon
        from engine.autonomous.daemon import main as daemon_main
        asyncio.run(daemon_main())


if __name__ == "__main__":
    main()
