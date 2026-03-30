import json
import os
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


@dataclass
class CareTask:
    """A single pet care activity."""
    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]
    frequency: Literal["daily", "weekly", "as_needed"] = "daily"
    completed: bool = False
    start_time: int | None = None  # minutes from midnight, assigned by Scheduler
    due_date: date | None = None   # date this task is due; None means no specific due date

    def to_dict(self) -> dict:
        """Convert this CareTask to a plain dict for JSON serialization."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "completed": self.completed,
            "start_time": self.start_time,
            "due_date": self.due_date.isoformat() if self.due_date is not None else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CareTask":
        """Reconstruct a CareTask from a plain dict."""
        due_date = date.fromisoformat(data["due_date"]) if data.get("due_date") is not None else None
        return cls(
            title=data["title"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            frequency=data.get("frequency", "daily"),
            completed=data.get("completed", False),
            start_time=data.get("start_time"),
            due_date=due_date,
        )


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

    def to_dict(self) -> dict:
        """Convert this Pet to a plain dict for JSON serialization."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Reconstruct a Pet from a plain dict."""
        pet = cls(
            name=data["name"],
            species=data["species"],
            age=data["age"],
        )
        pet.tasks = [CareTask.from_dict(t) for t in data.get("tasks", [])]
        return pet


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

    def to_dict(self) -> dict:
        """Convert this Owner to a plain dict for JSON serialization."""
        return {
            "name": self.name,
            "available_minutes": self.available_minutes,
            "pets": [p.to_dict() for p in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Reconstruct an Owner from a plain dict."""
        owner = cls(
            name=data["name"],
            available_minutes=data.get("available_minutes", 480),
        )
        owner.pets = [Pet.from_dict(p) for p in data.get("pets", [])]
        return owner

    def save_to_json(self, filepath: str) -> None:
        """Write this Owner's data to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str) -> "Owner":
        """Read a JSON file and return a fully reconstructed Owner object."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


class Scheduler:
    """Retrieves, organizes, and schedules care tasks across an owner's pets."""

    def __init__(self, owner: Owner):
        """Initialize the scheduler with an owner and an empty schedule."""
        self.owner = owner
        self.schedule: list[tuple[Pet, CareTask]] = []

    def build_plan(self) -> list[tuple[Pet, CareTask]]:
        """Sort tasks by priority and schedule them within the owner's available time budget."""
        all_tasks = self.owner.get_all_tasks()

        # Primary sort: priority (high → medium → low)
        # Secondary sort: shorter tasks first so more tasks fit in the time budget
        sorted_tasks = sorted(
            all_tasks,
            key=lambda pt: (PRIORITY_ORDER[pt[1].priority], pt[1].duration_minutes)
        )

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
        lines.append(f"\n{total} of {self.owner.available_minutes} minutes scheduled.")
        return "\n".join(lines)

    def mark_completed(self, task_title: str) -> bool:
        """Mark a scheduled task as completed and schedule its next recurrence if applicable."""
        for pet, task in self.schedule:
            if task.title.lower() == task_title.lower():
                task.completed = True
                # Auto-create the next occurrence for recurring tasks
                if task.frequency in RECURRENCE_DAYS:
                    days_ahead = RECURRENCE_DAYS[task.frequency]
                    next_due = (task.due_date or date.today()) + timedelta(days=days_ahead)
                    next_task = CareTask(
                        title=task.title,
                        duration_minutes=task.duration_minutes,
                        priority=task.priority,
                        frequency=task.frequency,
                        due_date=next_due,
                    )
                    pet.add_task(next_task)
                return True
        return False

    def detect_conflicts(self) -> list[str]:
        """Return warning messages for any tasks whose time windows overlap. Never raises."""
        warnings = []
        items = [(pet, task) for pet, task in self.schedule if task.start_time is not None]

        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                pet_a, task_a = items[i]
                pet_b, task_b = items[j]
                end_a = task_a.start_time + task_a.duration_minutes
                end_b = task_b.start_time + task_b.duration_minutes
                # Two intervals [s_a, end_a) and [s_b, end_b) overlap when neither ends before the other starts
                if task_a.start_time < end_b and task_b.start_time < end_a:
                    warnings.append(
                        f"CONFLICT: '{task_a.title}' ({pet_a.name}, {task_a.start_time}-{end_a} min) "
                        f"overlaps with '{task_b.title}' ({pet_b.name}, {task_b.start_time}-{end_b} min)"
                    )
        return warnings

    def sort_by_time(self) -> list[tuple[Pet, CareTask]]:
        """Return the schedule sorted by start_time (earliest first)."""
        return sorted(self.schedule, key=lambda pt: pt[1].start_time or 0)

    def filter_by_pet(self, pet_name: str) -> list[CareTask]:
        """Return scheduled tasks belonging to a specific pet by name."""
        return [task for pet, task in self.schedule if pet.name.lower() == pet_name.lower()]

    def filter_by_status(self, completed: bool) -> list[tuple[Pet, CareTask]]:
        """Return scheduled tasks matching the given completion status."""
        return [(pet, task) for pet, task in self.schedule if task.completed == completed]

    def find_next_slot(self, duration_minutes: int) -> int | None:
        """Return the first start time (minutes from midnight) with a gap large enough for duration_minutes.

        Scans the current schedule sorted by start_time and looks for a free gap before the
        owner's available_minutes runs out. Returns the gap's start minute, or None if no
        gap large enough exists within the available time budget.
        """
        # Build a list of (start, end) intervals from scheduled tasks that have a start_time
        intervals = sorted(
            [(task.start_time, task.start_time + task.duration_minutes)
             for _, task in self.schedule
             if task.start_time is not None],
            key=lambda iv: iv[0],
        )

        cursor = 0  # current position in the day (minutes from midnight)

        for start, end in intervals:
            # Gap between cursor and the next task's start
            if start - cursor >= duration_minutes:
                return cursor
            # Advance cursor past this task if it pushes further
            if end > cursor:
                cursor = end

        # Check remaining time after all scheduled tasks
        if cursor + duration_minutes <= self.owner.available_minutes:
            return cursor

        return None
