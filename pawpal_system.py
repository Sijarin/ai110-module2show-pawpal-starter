from dataclasses import dataclass, field
from typing import Literal


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class CareTask:
    """A single pet care activity."""
    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]
    frequency: Literal["daily", "weekly", "as_needed"] = "daily"
    completed: bool = False
    start_time: int | None = None  # minutes from midnight, assigned by Scheduler


@dataclass
class Pet:
    """A pet with its own list of care tasks."""
    name: str
    species: Literal["dog", "cat", "other"]
    age: int
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> list[CareTask]:
        """Return tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """An owner who may have multiple pets."""
    name: str
    pets: list[Pet] = field(default_factory=list)
    available_minutes: int = 480  # default: 8 hours

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[Pet, CareTask]]:
        """Return all pending tasks across all pets as (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.get_pending_tasks()]


class Scheduler:
    """Retrieves, organizes, and schedules care tasks across an owner's pets."""

    def __init__(self, owner: Owner):
        """Initialize the scheduler with an owner and an empty schedule."""
        self.owner = owner
        self.schedule: list[tuple[Pet, CareTask]] = []

    def build_plan(self) -> list[tuple[Pet, CareTask]]:
        """Sort tasks by priority and schedule them within the owner's available time budget."""
        all_tasks = self.owner.get_all_tasks()

        # Sort by priority (high → medium → low)
        sorted_tasks = sorted(all_tasks, key=lambda pt: PRIORITY_ORDER[pt[1].priority])

        time_used = 0
        self.schedule = []

        for pet, task in sorted_tasks:
            if time_used + task.duration_minutes <= self.owner.available_minutes:
                task.start_time = time_used
                time_used += task.duration_minutes
                self.schedule.append((pet, task))

        return self.schedule

    def explain_plan(self) -> str:
        """Return a plain-language summary of the scheduled tasks."""
        if not self.schedule:
            raise RuntimeError("Call build_plan() before explain_plan().")

        lines = [f"Care plan for {self.owner.name}:\n"]
        for pet, task in self.schedule:
            hours, mins = divmod(task.start_time, 60)
            period = "am" if hours < 12 else "pm"
            display_hour = hours if 1 <= hours <= 12 else (12 if hours == 0 else hours - 12)
            time_str = f"{display_hour}:{mins:02d}{period}"
            lines.append(
                f"  [{task.priority.upper()}] {time_str} — {task.title} "
                f"for {pet.name} ({task.duration_minutes} min)"
            )

        total = sum(t.duration_minutes for _, t in self.schedule)
        lines.append(f"\nTotal time: {total} min of {self.owner.available_minutes} min available.")
        return "\n".join(lines)

    def mark_completed(self, task_title: str) -> bool:
        """Mark a scheduled task as completed by title. Returns True if found."""
        for _, task in self.schedule:
            if task.title.lower() == task_title.lower():
                task.completed = True
                return True
        return False
