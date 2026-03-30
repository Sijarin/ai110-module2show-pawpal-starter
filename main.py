from datetime import date
from tabulate import tabulate
from pawpal_system import CareTask, Pet, Owner, Scheduler

SPECIES_EMOJI = {"dog": "🐶", "cat": "🐱", "other": "🐾"}

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

# --- Full schedule (tabulate) ---
print("=" * 50)
print("           TODAY'S SCHEDULE")
print("=" * 50)

sorted_schedule = scheduler.sort_by_time()
table_rows = []
for pet, task in sorted_schedule:
    hours, mins = divmod(task.start_time, 60)
    period = "am" if hours < 12 else "pm"
    display_hour = hours if 1 <= hours <= 12 else (12 if hours == 0 else hours - 12)
    time_str = f"{display_hour}:{mins:02d}{period}"
    species_emoji = SPECIES_EMOJI.get(pet.species, "🐾")
    table_rows.append([
        time_str,
        f"{species_emoji} {pet.name}",
        task.title,
        task.duration_minutes,
        task.priority.upper(),
    ])

print(tabulate(table_rows, headers=["Time", "Pet", "Task", "Duration", "Priority"], tablefmt="grid"))

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

# --- find_next_slot demo ---
print("\n--- find_next_slot demo ---")
# Reset start_times to the built plan values before testing find_next_slot
scheduler.build_plan()
slot_30 = scheduler.find_next_slot(30)
slot_5 = scheduler.find_next_slot(5)
slot_huge = scheduler.find_next_slot(999)
print(f"  First slot for 30-min task: {slot_30} min from midnight")
print(f"  First slot for 5-min task:  {slot_5} min from midnight")
print(f"  First slot for 999-min task: {slot_huge} (None = no room)")

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

print("=" * 50)
