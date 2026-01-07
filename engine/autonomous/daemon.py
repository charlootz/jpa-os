"""
Autonomous Daemon for jpa-os.

Runs continuously, processing tasks from the work queue.
This is how Vega achieves true autonomy — a persistent process
that works through tasks without requiring prompts.

Usage:
    python -m engine.autonomous.daemon

Features:
- Continuous operation with configurable sleep between tasks
- Graceful shutdown on SIGINT/SIGTERM
- Logging of all activity
- Integration with the work queue
- Uses hooks for auto-approval of safe operations
"""

import asyncio
import logging
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from engine.autonomous.queue import WorkQueue, Task, TaskStatus
from engine.agents.base import run_vega_autonomous

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/Users/jpa/jpa-os/vault/hive/logs/daemon.log'),
    ]
)
logger = logging.getLogger(__name__)


class AutonomousDaemon:
    """
    Daemon for autonomous agent operation.

    Continuously processes tasks from the work queue,
    enabling agents to work without human prompting.
    """

    def __init__(
        self,
        queue: Optional[WorkQueue] = None,
        sleep_between_tasks: int = 10,
        sleep_when_idle: int = 60,
        max_consecutive_failures: int = 3,
    ):
        """
        Initialize the daemon.

        Args:
            queue: Work queue to process (defaults to standard location)
            sleep_between_tasks: Seconds to sleep between tasks
            sleep_when_idle: Seconds to sleep when queue is empty
            max_consecutive_failures: Stop after this many failures in a row
        """
        self.queue = queue or WorkQueue()
        self.sleep_between_tasks = sleep_between_tasks
        self.sleep_when_idle = sleep_when_idle
        self.max_consecutive_failures = max_consecutive_failures

        self.running = False
        self.consecutive_failures = 0
        self.tasks_processed = 0
        self.start_time: Optional[datetime] = None

    async def start(self):
        """Start the daemon."""
        self.running = True
        self.start_time = datetime.now()

        logger.info("=" * 60)
        logger.info("AUTONOMOUS DAEMON STARTING")
        logger.info(f"Sleep between tasks: {self.sleep_between_tasks}s")
        logger.info(f"Sleep when idle: {self.sleep_when_idle}s")
        logger.info("=" * 60)

        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._handle_shutdown)

        await self._main_loop()

    def _handle_shutdown(self):
        """Handle shutdown signals."""
        logger.info("Shutdown signal received, stopping gracefully...")
        self.running = False

    async def _main_loop(self):
        """Main processing loop."""
        while self.running:
            try:
                # Get next task
                task = self.queue.get_next()

                if task is None:
                    logger.debug("No pending tasks, sleeping...")
                    await asyncio.sleep(self.sleep_when_idle)
                    continue

                # Process the task
                await self._process_task(task)

                # Sleep between tasks
                if self.running:
                    await asyncio.sleep(self.sleep_between_tasks)

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.consecutive_failures += 1

                if self.consecutive_failures >= self.max_consecutive_failures:
                    logger.error(f"Too many consecutive failures ({self.consecutive_failures}), stopping")
                    self.running = False
                else:
                    await asyncio.sleep(self.sleep_when_idle)

        # Log final stats
        self._log_shutdown_stats()

    async def _process_task(self, task: Task):
        """Process a single task."""
        logger.info(f"Processing task: {task.id}")
        logger.info(f"Description: {task.description}")

        # Mark as in progress
        self.queue.start(task.id)

        try:
            # Run Vega in autonomous mode
            result = await run_vega_autonomous(
                initial_task=task.description,
                stream_callback=lambda x: print(x, end='', flush=True),
            )

            # Mark as complete
            self.queue.complete(task.id, result)
            self.tasks_processed += 1
            self.consecutive_failures = 0

            logger.info(f"Task {task.id} completed successfully")

        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            self.queue.fail(task.id, str(e))
            self.consecutive_failures += 1

    def _log_shutdown_stats(self):
        """Log statistics on shutdown."""
        if self.start_time:
            runtime = datetime.now() - self.start_time
        else:
            runtime = "unknown"

        logger.info("=" * 60)
        logger.info("AUTONOMOUS DAEMON STOPPED")
        logger.info(f"Runtime: {runtime}")
        logger.info(f"Tasks processed: {self.tasks_processed}")
        logger.info("=" * 60)


async def main():
    """Entry point for the daemon."""
    # Ensure log directory exists
    log_dir = Path('/Users/jpa/jpa-os/vault/hive/logs')
    log_dir.mkdir(parents=True, exist_ok=True)

    daemon = AutonomousDaemon()
    await daemon.start()


if __name__ == "__main__":
    asyncio.run(main())
