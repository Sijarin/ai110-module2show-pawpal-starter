from datetime import date
from pawpal_system import CareTask, Pet, Owner, Scheduler


# --- Setup ---
owner = Owner(name="Jordan", available_minutes=120)

dog = Pet(name="Mochi", species="dog", age=3)
# Added out of order: low priority first, then high
dog.add_task(CareTask(title="Playtime",     duration_minutes=25, priority="low",    frequency="daily",  due_date=date.today()))
dog.add_task(CareTask(title="Morning walk", duration_minutes=30, priority="high",   frequency="daily",  due_date=date.today()))
dog.add_task(CareTask(title="Brush teeth",  duration_minutes=10, priority="medium", frequency="daily",  due_date=date.today()))

cat = Pet(name="Luna", species="cat", age=2)
# Added out of order: as_needed first, then high priority
cat.add_task(CareTask(title="Flea treatment",   duration_minutes=5,  priority="medium", frequency="weekly", due_date=date.today()))
cat.add_task(CareTask(title="Clean litter box", duration_minutes=10, priority="high",   frequency="daily",  due_date=date.today()))
cat.add_task(CareTask(title="Playtime",         duration_minutes=20, priority="low",    frequency="daily",  due_date=date.today()))

owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler(owner)
scheduler.build_plan()

# --- Full schedule ---
print("=" * 40)
print("       TODAY'S SCHEDULE")
print("=" * 40)
print(scheduler.explain_plan())

# --- Sorted by start time ---
print("\n--- Sorted by start time ---")
for pet, task in scheduler.sort_by_time():
    print(f"  {task.start_time:3d} min — {task.title} ({pet.name})")

# --- Filter: Mochi's tasks only ---
print("\n--- Mochi's tasks ---")
for task in scheduler.filter_by_pet("Mochi"):
    print(f"  {task.title} [{task.priority}]")

# --- Filter: incomplete tasks ---
print("\n--- Incomplete tasks ---")
for pet, task in scheduler.filter_by_status(completed=False):
    print(f"  {task.title} for {pet.name}")

# --- Conflict detection demo ---
# Force two already-scheduled tasks to overlap by shifting start_times
for pet, task in scheduler.schedule:
    if task.title == "Morning walk":
        task.start_time = 0   # runs 0-30 min
    if task.title == "Clean litter box":
        task.start_time = 15  # runs 15-25 min — overlaps with Morning walk

print("\n--- Conflict detection ---")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts found.")

# --- Recurring task demo ---
print("\n--- Completing 'Morning walk' (daily recurring) ---")
scheduler.mark_completed("Morning walk")
print("  Mochi's full task list after completion:")
for task in dog.tasks:
    status = "done" if task.completed else f"due {task.due_date}"
    print(f"    {task.title} [{task.frequency}] — {status}")

print("\n--- Completing 'Flea treatment' (weekly recurring) ---")
scheduler.mark_completed("Flea treatment")
print("  Luna's full task list after completion:")
for task in cat.tasks:
    status = "done" if task.completed else f"due {task.due_date}"
    print(f"    {task.title} [{task.frequency}] — {status}")

print("=" * 40)
