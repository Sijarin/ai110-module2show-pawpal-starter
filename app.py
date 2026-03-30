import streamlit as st
from pawpal_system import CareTask, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state setup ---
if "owner" not in st.session_state:
    st.session_state.owner = None

# --- Step 1: Create Owner ---
st.subheader("Step 1: Owner")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_minutes = st.number_input("Available time (minutes)", min_value=10, max_value=480, value=120)

if st.button("Save owner"):
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
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
        # Calls owner.add_pet() — the UI action maps directly to the class method
        new_pet = Pet(name=pet_name, species=species, age=age)
        st.session_state.owner.add_pet(new_pet)
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

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        # Calls pet.add_task() — directly wired to the class method
        task = CareTask(title=task_title, duration_minutes=int(duration), priority=priority)
        selected_pet.add_task(task)
        st.success(f"Added '{task_title}' to {selected_pet_name}!")

    pending = selected_pet.get_pending_tasks()
    if pending:
        st.write(f"Tasks for {selected_pet_name}:")
        st.table([{"title": t.title, "duration (min)": t.duration_minutes,
                   "priority": t.priority} for t in pending])
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
        st.success("Schedule generated!")
        st.text(scheduler.explain_plan())
