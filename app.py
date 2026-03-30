import os
import streamlit as st
from pawpal_system import CareTask, Pet, Owner, Scheduler

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

SPECIES_EMOJI = {"dog": "🐶", "cat": "🐱", "other": "🐾"}
PRIORITY_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


st.title("🐾 PawPal+")

# --- Sidebar: Clear saved data ---
with st.sidebar:
    st.header("Data Management")
    if st.button("Clear saved data"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.session_state.owner = None
        st.success("Saved data cleared and session reset.")

# --- Session state setup ---
if "owner" not in st.session_state:
    # On startup, load from data.json if it exists
    if os.path.exists(DATA_FILE):
        try:
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
        except Exception:
            st.session_state.owner = None
    else:
        st.session_state.owner = None

# --- Step 1: Create Owner ---
st.subheader("Step 1: Owner")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_minutes = st.number_input("Available time (minutes)", min_value=0, max_value=480, value=120)

if st.button("Save owner"):
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
    st.session_state.owner.save_to_json(DATA_FILE)
    st.success(f"Owner '{owner_name}' saved!")

st.divider()

# --- Step 2: Add Pets ---
st.subheader("Step 2: Add Pets")

if st.session_state.owner is None:
    st.info("Save an owner above first.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Pet age", min_value=0, max_value=30, value=3)

    if st.button("Add pet"):
        new_pet = Pet(name=pet_name, species=species, age=age)
        st.session_state.owner.add_pet(new_pet)
        st.session_state.owner.save_to_json(DATA_FILE)
        st.success(f"Added pet '{pet_name}' to {st.session_state.owner.name}!")

    if st.session_state.owner.pets:
        st.write("Pets registered:")
        st.table([{"name": p.name, "species": p.species, "age": p.age,
                   "tasks": len(p.tasks)} for p in st.session_state.owner.pets])

st.divider()

# --- Step 3: Add Tasks to a Pet ---
st.subheader("Step 3: Add Tasks")

owner = st.session_state.owner
if owner is None or not owner.pets:
    st.info("Add at least one pet above before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Assign task to pet", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as_needed"])

    if st.button("Add task"):
        task = CareTask(title=task_title, duration_minutes=int(duration),
                        priority=priority, frequency=frequency)
        selected_pet.add_task(task)
        owner.save_to_json(DATA_FILE)
        st.success(f"Added '{task_title}' to {selected_pet_name}!")

    pending = selected_pet.get_pending_tasks()
    if pending:
        st.write(f"Tasks for {selected_pet_name}:")
        st.table([{"title": t.title, "duration (min)": t.duration_minutes,
                   "priority": t.priority, "frequency": t.frequency} for t in pending])
    else:
        st.info("No tasks yet for this pet.")

st.divider()

# --- Step 4: Generate Schedule ---
st.subheader("Step 4: Build Schedule")

if st.button("Generate schedule"):
    owner = st.session_state.owner
    if owner is None or not owner.get_all_tasks():
        st.warning("Add an owner, at least one pet, and at least one task first.")
    else:
        scheduler = Scheduler(owner)
        scheduler.build_plan()

        # --- Conflict warnings (shown before the schedule) ---
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.error(f"{len(conflicts)} scheduling conflict(s) detected — review before proceeding:")
            for c in conflicts:
                st.warning(c)

        # --- Schedule table sorted by start time ---
        sorted_schedule = scheduler.sort_by_time()
        if sorted_schedule:
            st.success(f"Schedule ready — {sum(t.duration_minutes for _, t in sorted_schedule)} of "
                       f"{owner.available_minutes} minutes planned.")

            rows = []
            for pet, task in sorted_schedule:
                hours, mins = divmod(task.start_time, 60)
                period = "am" if hours < 12 else "pm"
                display_hour = hours if 1 <= hours <= 12 else (12 if hours == 0 else hours - 12)
                priority_upper = task.priority.upper()
                priority_display = f"{PRIORITY_EMOJI.get(priority_upper, '')} {priority_upper}"
                species_emoji = SPECIES_EMOJI.get(pet.species, "🐾")
                rows.append({
                    "Time": f"{display_hour}:{mins:02d}{period}",
                    "Task": task.title,
                    "Pet": f"{species_emoji} {pet.name}",
                    "Duration (min)": task.duration_minutes,
                    "Priority": priority_display,
                    "Frequency": task.frequency,
                })
            st.table(rows)

        # --- Filter: show tasks by pet ---
        st.markdown("**Filter by pet:**")
        filter_pet = st.selectbox("Show tasks for", [p.name for p in owner.pets],
                                  key="filter_pet")
        pet_tasks = scheduler.filter_by_pet(filter_pet)
        if pet_tasks:
            st.table([{"Task": t.title, "Priority": t.priority.upper(),
                       "Duration (min)": t.duration_minutes} for t in pet_tasks])
        else:
            st.info(f"No scheduled tasks for {filter_pet}.")
