from pawpal_system import CareTask, Pet, Owner, Scheduler


# --- Setup ---
owner = Owner(name="Jordan", available_minutes=120)

dog = Pet(name="Mochi", species="dog", age=3)
dog.add_task(CareTask(title="Morning walk", duration_minutes=30, priority="high", frequency="daily"))
dog.add_task(CareTask(title="Brush teeth", duration_minutes=10, priority="medium", frequency="daily"))

cat = Pet(name="Luna", species="cat", age=2)
cat.add_task(CareTask(title="Clean litter box", duration_minutes=10, priority="high", frequency="daily"))
cat.add_task(CareTask(title="Playtime", duration_minutes=20, priority="low", frequency="daily"))
cat.add_task(CareTask(title="Flea treatment", duration_minutes=5, priority="medium", frequency="weekly"))

owner.add_pet(dog)
owner.add_pet(cat)

# --- Schedule ---
scheduler = Scheduler(owner)
scheduler.build_plan()

print("=" * 40)
print("       TODAY'S SCHEDULE")
print("=" * 40)
print(scheduler.explain_plan())
print("=" * 40)
