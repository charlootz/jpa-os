"""
Work Queue for autonomous agent operation.

Tasks can be added to the queue from anywhere:
- CLI commands
- Slack messages
- Scheduled routines
- Other agents

The autonomous daemon picks up tasks from this queue.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """A task in the work queue."""
    id: str
    description: str
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    source: str = "manual"  # Where the task came from

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class WorkQueue:
    """
    Persistent work queue for autonomous agents.

    Stores tasks in a JSON file in the vault.
    """

    def __init__(self, queue_path: Optional[Path] = None):
        self.queue_path = queue_path or Path("/Users/jpa/jpa-os/vault/hive/work_queue.json")
        self._ensure_queue_exists()

    def _ensure_queue_exists(self):
        """Create queue file if it doesn't exist."""
        if not self.queue_path.exists():
            self.queue_path.parent.mkdir(parents=True, exist_ok=True)
            self._save([])

    def _load(self) -> list[dict]:
        """Load tasks from disk."""
        try:
            return json.loads(self.queue_path.read_text())
        except Exception:
            return []

    def _save(self, tasks: list[dict]):
        """Save tasks to disk."""
        self.queue_path.write_text(json.dumps(tasks, indent=2))

    def _task_to_dict(self, task: Task) -> dict:
        """Convert task to dict for storage."""
        d = asdict(task)
        d['priority'] = task.priority.value
        d['status'] = task.status.value
        return d

    def _dict_to_task(self, d: dict) -> Task:
        """Convert dict to Task."""
        d['priority'] = TaskPriority(d['priority'])
        d['status'] = TaskStatus(d['status'])
        return Task(**d)

    def add(
        self,
        description: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        source: str = "manual"
    ) -> Task:
        """
        Add a new task to the queue.

        Args:
            description: What needs to be done
            priority: Task priority (LOW, NORMAL, HIGH, URGENT)
            source: Where the task came from

        Returns:
            The created Task
        """
        tasks = self._load()

        # Generate ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(tasks)}"

        task = Task(
            id=task_id,
            description=description,
            priority=priority,
            source=source,
        )

        tasks.append(self._task_to_dict(task))
        self._save(tasks)

        # Also update the markdown view
        self._update_markdown_view()

        return task

    def get_next(self) -> Optional[Task]:
        """
        Get the next task to work on.

        Returns highest priority pending task, or None if queue is empty.
        """
        tasks = self._load()

        # Filter to pending tasks
        pending = [t for t in tasks if t['status'] == TaskStatus.PENDING.value]

        if not pending:
            return None

        # Sort by priority (highest first), then by created_at (oldest first)
        pending.sort(key=lambda t: (-t['priority'], t['created_at']))

        return self._dict_to_task(pending[0])

    def start(self, task_id: str) -> bool:
        """Mark a task as in progress."""
        tasks = self._load()

        for task in tasks:
            if task['id'] == task_id:
                task['status'] = TaskStatus.IN_PROGRESS.value
                task['started_at'] = datetime.now().isoformat()
                self._save(tasks)
                self._update_markdown_view()
                return True

        return False

    def complete(self, task_id: str, result: str = "") -> bool:
        """Mark a task as completed."""
        tasks = self._load()

        for task in tasks:
            if task['id'] == task_id:
                task['status'] = TaskStatus.COMPLETED.value
                task['completed_at'] = datetime.now().isoformat()
                task['result'] = result
                self._save(tasks)
                self._update_markdown_view()
                return True

        return False

    def fail(self, task_id: str, error: str = "") -> bool:
        """Mark a task as failed."""
        tasks = self._load()

        for task in tasks:
            if task['id'] == task_id:
                task['status'] = TaskStatus.FAILED.value
                task['completed_at'] = datetime.now().isoformat()
                task['error'] = error
                self._save(tasks)
                self._update_markdown_view()
                return True

        return False

    def list_pending(self) -> list[Task]:
        """Get all pending tasks."""
        tasks = self._load()
        pending = [t for t in tasks if t['status'] == TaskStatus.PENDING.value]
        return [self._dict_to_task(t) for t in pending]

    def list_all(self) -> list[Task]:
        """Get all tasks."""
        tasks = self._load()
        return [self._dict_to_task(t) for t in tasks]

    def clear_completed(self):
        """Remove completed tasks from the queue."""
        tasks = self._load()
        tasks = [t for t in tasks if t['status'] not in [
            TaskStatus.COMPLETED.value,
            TaskStatus.FAILED.value
        ]]
        self._save(tasks)
        self._update_markdown_view()

    def _update_markdown_view(self):
        """Update the markdown view of the queue for humans."""
        md_path = self.queue_path.with_suffix('.md')

        tasks = self._load()
        lines = ["# Work Queue", "", f"Last updated: {datetime.now().isoformat()}", ""]

        # Group by status
        pending = [t for t in tasks if t['status'] == TaskStatus.PENDING.value]
        in_progress = [t for t in tasks if t['status'] == TaskStatus.IN_PROGRESS.value]
        completed = [t for t in tasks if t['status'] == TaskStatus.COMPLETED.value]
        failed = [t for t in tasks if t['status'] == TaskStatus.FAILED.value]

        if in_progress:
            lines.append("## In Progress")
            for t in in_progress:
                lines.append(f"- [ ] **{t['description']}** (started {t.get('started_at', 'unknown')})")
            lines.append("")

        if pending:
            lines.append("## Pending")
            for t in sorted(pending, key=lambda x: -x['priority']):
                priority_label = TaskPriority(t['priority']).name.lower()
                lines.append(f"- [ ] {t['description']} ({priority_label})")
            lines.append("")

        if completed:
            lines.append("## Completed")
            for t in completed[-5:]:  # Last 5 completed
                lines.append(f"- [x] {t['description']}")
            lines.append("")

        if failed:
            lines.append("## Failed")
            for t in failed[-3:]:  # Last 3 failed
                lines.append(f"- [!] {t['description']} - {t.get('error', 'unknown error')}")
            lines.append("")

        md_path.write_text('\n'.join(lines))
