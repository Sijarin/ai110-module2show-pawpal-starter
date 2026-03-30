from pawpal_system import CareTask, Pet, Owner, Scheduler


def test_mark_completed_changes_task_status():
    """mark_completed() should set the task's completed flag to True."""
    pet = Pet(name="Mochi", species="dog", age=3)
    task = CareTask(title="Morning walk", duration_minutes=30, priority="high")
    pet.add_task(task)

    owner = Owner(name="Jordan")
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.build_plan()
    result = scheduler.mark_completed("Morning walk")

    assert result is True
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """add_task() should increase the pet's task list by one."""
    pet = Pet(name="Luna", species="cat", age=2)
    assert len(pet.tasks) == 0

    pet.add_task(CareTask(title="Playtime", duration_minutes=20, priority="low"))
    assert len(pet.tasks) == 1

    pet.add_task(CareTask(title="Clean litter box", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 2
