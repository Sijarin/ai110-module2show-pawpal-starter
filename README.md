# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ includes algorithmic scheduling logic beyond a simple sorted list:

- **Priority + duration sort** — high-priority tasks run first; among equal-priority tasks, shorter ones are scheduled first to fit more into the available time budget.
- **Recurring tasks** — daily tasks auto-generate the next occurrence (due tomorrow) when marked complete; weekly tasks reschedule 7 days out using Python's `timedelta`.
- **Conflict detection** — after a plan is built, `detect_conflicts()` checks every pair of tasks for overlapping time windows and returns human-readable warnings instead of crashing.
- **Filtering** — `filter_by_pet(name)` returns tasks for a specific pet; `filter_by_status(completed)` returns pending or finished tasks.
- **Sort by time** — `sort_by_time()` re-orders the schedule by actual start time for display purposes.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
