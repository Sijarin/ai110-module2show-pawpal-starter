from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Pet:
    name: str
    species: Literal["dog", "cat", "other"]
    age: int


@dataclass
class CareTask:
    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]


@dataclass
class Owner:
    name: str
    pet: Pet
    available_minutes: int = 480  # default: 8 hours


class Scheduler:
    def __init__(self, owner: Owner, tasks: list[CareTask]):
        self.owner = owner
        self.tasks = tasks
        self.schedule: list[CareTask] = []

    def build_plan(self) -> list[CareTask]:
        """Select and order tasks based on priority and available time."""
        pass

    def explain_plan(self) -> str:
        """Return a plain-language explanation of the scheduled tasks."""
        pass
