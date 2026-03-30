import streamlit as st
from pawpal_system import CareTask, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state setup ---
# st.session_state acts like a dictionary that survives reruns.
# We check "owner" exists before creating it so it isn't reset on every click.
if "owner" not in st.session_state:
    st.session_state.owner = None  # set after the owner form is submitted

if "pet" not in st.session_state:
    st.session_state.pet = None    # set after the pet form is submitted

# --- Owner & Pet setup ---
st.subheader("Setup")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Available time (minutes)", min_value=10, max_value=480, value=120)
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Pet age", min_value=0, max_value=30, value=3)

if st.button("Save owner & pet"):
    pet = Pet(name=pet_name, species=species, age=age)
    owner = Owner(name=owner_name, available_minutes=available_minutes)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.success(f"Saved {owner_name} with pet {pet_name}!")

st.divider()

# --- Task input ---
st.subheader("Add Tasks")

if st.session_state.pet is None:
    st.info("Save an owner and pet above before adding tasks.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        task = CareTask(title=task_title, duration_minutes=int(duration), priority=priority)
        st.session_state.pet.add_task(task)
        st.success(f"Added: {task_title}")

    pending = st.session_state.pet.get_pending_tasks()
    if pending:
        st.write("Current tasks:")
        st.table([{"title": t.title, "duration": t.duration_minutes, "priority": t.priority} for t in pending])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    owner = st.session_state.owner
    if owner is None or not owner.get_all_tasks():
        st.warning("Add an owner, a pet, and at least one task first.")
    else:
        scheduler = Scheduler(owner)
        scheduler.build_plan()
        st.success("Schedule generated!")
        st.text(scheduler.explain_plan())
