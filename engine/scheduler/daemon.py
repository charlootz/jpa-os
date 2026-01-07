"""
Scheduler Daemon

Runs continuously, triggering routines at their scheduled times.

Usage:
    python -m engine.scheduler.daemon

This should be run as a background service (launchd, systemd, etc.)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from croniter import croniter
from dotenv import load_dotenv
load_dotenv()

from engine.scheduler.routines import ROUTINES
from engine.scheduler.runner import run_routine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# jpa's timezone
TIMEZONE = ZoneInfo("America/New_York")


def get_next_run(cron_expr: str, base_time: datetime) -> datetime:
    """Get the next run time for a cron expression."""
    cron = croniter(cron_expr, base_time)
    return cron.get_next(datetime)


async def scheduler_loop():
    """
    Main scheduler loop.

    Checks every minute if any routine should run.
    """
    logger.info("Scheduler daemon starting...")
    logger.info(f"Timezone: {TIMEZONE}")
    logger.info(f"Loaded {len(ROUTINES)} routines:")
    for r in ROUTINES:
        if r.enabled:
            logger.info(f"  - {r.name}: {r.schedule}")

    # Track last run times to avoid double-firing
    last_run = {}

    while True:
        now = datetime.now(TIMEZONE)
        current_minute = now.strftime("%Y-%m-%d %H:%M")

        for routine in ROUTINES:
            if not routine.enabled:
                continue

            # Check if this routine should run now
            cron = croniter(routine.schedule, now.replace(second=0, microsecond=0) - timedelta(minutes=1))
            next_run = cron.get_next(datetime)

            # If next run is within this minute and we haven't run it yet
            if next_run.strftime("%Y-%m-%d %H:%M") == current_minute:
                if last_run.get(routine.name) != current_minute:
                    logger.info(f"Triggering routine: {routine.name}")
                    last_run[routine.name] = current_minute

                    try:
                        await run_routine(routine.name)
                        logger.info(f"Routine {routine.name} completed")
                    except Exception as e:
                        logger.error(f"Routine {routine.name} failed: {e}")

        # Sleep until next minute
        now = datetime.now(TIMEZONE)
        seconds_until_next_minute = 60 - now.second
        await asyncio.sleep(seconds_until_next_minute)


def main():
    """Entry point."""
    try:
        asyncio.run(scheduler_loop())
    except KeyboardInterrupt:
        logger.info("Scheduler daemon stopped")


if __name__ == "__main__":
    main()
