from datetime import date, timedelta
from pawpal_system import CareTask, Pet, Owner, Scheduler


# --- Helpers ---

def make_scheduler(*pets, available_minutes=120):
    owner = Owner(name="Jordan", available_minutes=available_minutes)
    for pet in pets:
        owner.add_pet(pet)
    s = Scheduler(owner)
    s.build_plan()
    return s


def dog_with(*tasks):
    pet = Pet(name="Mochi", species="dog", age=3)
    for t in tasks:
        pet.add_task(t)
    return pet


def cat_with(*tasks):
    pet = Pet(name="Luna", species="cat", age=2)
    for t in tasks:
        pet.add_task(t)
    return pet


# --- Original tests ---

def test_mark_completed_changes_task_status():
    """mark_completed() should set the task's completed flag to True."""
    task = CareTask(title="Morning walk", duration_minutes=30, priority="high")
    s = make_scheduler(dog_with(task))
    assert s.mark_completed("Morning walk") is True
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """add_task() should increase the pet's task list by one."""
    pet = Pet(name="Luna", species="cat", age=2)
    assert len(pet.tasks) == 0
    pet.add_task(CareTask(title="Playtime", duration_minutes=20, priority="low"))
    assert len(pet.tasks) == 1
    pet.add_task(CareTask(title="Clean litter box", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 2


# --- Happy paths ---

def test_build_plan_sorts_by_priority():
    """High-priority tasks should appear before low-priority tasks in the schedule."""
    pet = dog_with(
        CareTask(title="Low task",  duration_minutes=10, priority="low"),
        CareTask(title="High task", duration_minutes=10, priority="high"),
    )
    s = make_scheduler(pet)
    titles = [task.title for _, task in s.schedule]
    assert titles.index("High task") < titles.index("Low task")


def test_build_plan_excludes_tasks_over_budget():
    """Tasks that would exceed available_minutes should not be scheduled."""
    pet = dog_with(
        CareTask(title="Short task", duration_minutes=10, priority="high"),
        CareTask(title="Long task",  duration_minutes=200, priority="high"),
    )
    s = make_scheduler(pet, available_minutes=30)
    titles = [task.title for _, task in s.schedule]
    assert "Short task" in titles
    assert "Long task" not in titles


def test_daily_task_recurrence():
    """Completing a daily task should create a new task due tomorrow."""
    today = date.today()
    task = CareTask(title="Walk", duration_minutes=20, priority="high",
                    frequency="daily", due_date=today)
    pet = dog_with(task)
    s = make_scheduler(pet)
    s.mark_completed("Walk")

    future_tasks = [t for t in pet.tasks if not t.completed]
    assert len(future_tasks) == 1
    assert future_tasks[0].due_date == today + timedelta(days=1)


def test_weekly_task_recurrence():
    """Completing a weekly task should create a new task due in 7 days."""
    today = date.today()
    task = CareTask(title="Flea treatment", duration_minutes=5, priority="medium",
                    frequency="weekly", due_date=today)
    pet = cat_with(task)
    s = make_scheduler(pet)
    s.mark_completed("Flea treatment")

    future_tasks = [t for t in pet.tasks if not t.completed]
    assert len(future_tasks) == 1
    assert future_tasks[0].due_date == today + timedelta(days=7)


# --- Edge cases ---

def test_as_needed_task_no_recurrence():
    """Completing an as_needed task should NOT create a follow-up task."""
    task = CareTask(title="Vet visit", duration_minutes=60, priority="high",
                    frequency="as_needed")
    pet = dog_with(task)
    s = make_scheduler(pet, available_minutes=120)
    s.mark_completed("Vet visit")

    future_tasks = [t for t in pet.tasks if not t.completed]
    assert len(future_tasks) == 0


def test_pet_with_no_tasks_does_not_crash():
    """A pet with no tasks should not cause build_plan() to crash."""
    s = make_scheduler(dog_with())
    assert s.schedule == []


def test_detect_conflicts_identical_start_times():
    """Two tasks starting at the same time should be flagged as a conflict."""
    pet = dog_with(
        CareTask(title="Task A", duration_minutes=20, priority="high"),
        CareTask(title="Task B", duration_minutes=20, priority="high"),
    )
    s = make_scheduler(pet)
    # Force both to start at the same time
    for _, task in s.schedule:
        task.start_time = 0
    conflicts = s.detect_conflicts()
    assert len(conflicts) == 1
    assert "Task A" in conflicts[0]
    assert "Task B" in conflicts[0]


def test_detect_conflicts_no_overlap():
    """Non-overlapping tasks should produce no conflict warnings."""
    pet = dog_with(
        CareTask(title="Task A", duration_minutes=10, priority="high"),
        CareTask(title="Task B", duration_minutes=10, priority="medium"),
    )
    s = make_scheduler(pet)
    # Assign back-to-back start times
    for i, (_, task) in enumerate(s.schedule):
        task.start_time = i * 15
    assert s.detect_conflicts() == []


def test_filter_by_pet_unknown_name():
    """filter_by_pet() with a name not in the schedule should return an empty list."""
    s = make_scheduler(dog_with(CareTask(title="Walk", duration_minutes=20, priority="high")))
    assert s.filter_by_pet("Ghost") == []


def test_build_plan_zero_available_minutes():
    """With zero available minutes, nothing should be scheduled."""
    pet = dog_with(CareTask(title="Walk", duration_minutes=10, priority="high"))
    s = make_scheduler(pet, available_minutes=0)
    assert s.schedule == []
