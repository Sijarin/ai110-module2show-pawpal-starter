# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Answer: Four classes — Pet (animal info), Owner (name + availability, has-a Pet), CareTask (title, duration, priority — data only), and Scheduler (builds and explains the daily plan using priority and time constraints).

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Answer: After AI review, three changes were noted. First, added `start_time` to `CareTask` so the scheduler can record when each task begins. Second, added a guard in `explain_plan()` to raise an error if `build_plan()` hasn't been called first. Third, the AI flagged that `owner.available_minutes` was never read inside `build_plan()` — this wasn't a code change yet, but a reminder to use it as a time cap when implementing the scheduling logic.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Answer: The scheduler considers priority level (high/medium/low), task duration, and the owner's total available minutes. Priority was the most important constraint because a pet owner needs to know that critical tasks like medication always happen first. Duration was added as a secondary sort so shorter tasks fill remaining gaps in the budget — maximizing how many tasks get done in the available time.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Answer: The conflict detector checks all pairs of tasks (O(n²)) rather than sorting by start time first and only checking neighbors (O(n log n)). For a pet care app with a small number of daily tasks, the simpler pairwise approach is fine and easier to read. A more efficient algorithm would only pay off with hundreds of tasks, which isn't a realistic scenario here.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

Answer: AI was used across every phase — brainstorming the initial four-class UML, generating class skeletons, suggesting edge cases for testing, and reviewing methods for readability. The most useful prompts were specific and scoped: asking about a single method ("how should Scheduler retrieve tasks from Owner?") gave cleaner answers than broad questions. Asking for a "lightweight" approach (as in conflict detection) also helped steer away from over-engineered solutions.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Answer: AI suggested replacing the `detect_conflicts()` loop with an `itertools.combinations` one-liner. The logic was correct but the overlap condition buried inside a list comprehension was hard to read at a glance. I kept the explicit loop version with named variables (`end_a`, `end_b`) and a comment explaining the interval logic. I verified the decision by reading both versions side-by-side and choosing the one a future reader could debug without needing to think twice.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Answer: 12 tests covering priority sorting, time budget enforcement, daily and weekly recurrence, no recurrence for `as_needed` tasks, conflict detection (both positive and negative cases), and edge cases like empty pets and zero available minutes. These were important because the scheduler has several interdependent behaviors — a bug in sorting affects recurrence, which affects filtering — so each layer needed independent verification.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Answer: 4/5. The logic layer is well-covered. Next I would test: a pet with 10+ tasks to verify budget cutoff order, two pets with the same task title to check `mark_completed()` ambiguity, and a task whose `due_date` is in the past to verify recurrence still calculates correctly.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

Answer: The recurring task logic. Having `mark_completed()` automatically create the next occurrence using `timedelta` made the system feel genuinely useful rather than just a demo — it models how real pet care actually works.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Answer: I would add persistent storage so tasks survive a page refresh in Streamlit. Right now all data resets when the app restarts. A simple JSON file or SQLite database would make the app usable day to day rather than just as a demo.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Answer: AI is best used as a fast second opinion, not a first author. Every time I brought a specific, concrete question  a method signature, an edge case, a readability tradeoff the suggestions were useful. When the question was too open-ended, the output needed heavy editing. The clearest lesson: the human has to own the architecture. AI fills in the gaps faster, but it doesn't know what matters to the project unless you tell it.

---

## 6. Prompt Comparison (Challenge 5)

**The prompt used:**

"Write a Python function that automatically reschedules a completed weekly care task to its next occurrence, one week later."

---

**What GPT-4 returned:**

GPT-4 produced a standalone utility function placed outside any class:

```python
def reschedule_weekly_task(task, today=None):
    from datetime import date, timedelta
    if today is None:
        today = date.today()
    new_task = {
        "title": task["title"],
        "duration_minutes": task["duration_minutes"],
        "priority": task["priority"],
        "frequency": "weekly",
        "due_date": (today + timedelta(days=7)).isoformat(),
        "completed": False,
    }
    return new_task
```

The function accepts and returns plain dicts. It imports `timedelta` inline, requires the caller to manually append the result to whatever list stores tasks, and has no awareness of the existing `CareTask`, `Pet`, or `Scheduler` classes. To use it in PawPal+ the caller would need to convert a `CareTask` to a dict, call the function, convert the result back to a `CareTask`, and append it to `pet.tasks` — four steps that the existing class design could handle in one.

---

**What Claude returned:**

Claude integrated the logic directly into `Scheduler.mark_completed()` as an extension of the existing method:

```python
if task.frequency in RECURRENCE_DAYS:
    days_ahead = RECURRENCE_DAYS[task.frequency]
    next_due = (task.due_date or date.today()) + timedelta(days=days_ahead)
    next_task = CareTask(
        title=task.title,
        duration_minutes=task.duration_minutes,
        priority=task.priority,
        frequency=task.frequency,
        due_date=next_due,
    )
    pet.add_task(next_task)
```

This version reuses the existing `RECURRENCE_DAYS` dict (so daily and weekly are handled by the same branch), constructs a proper `CareTask` dataclass instance, and calls `pet.add_task()` — the method already defined for this purpose. No new imports, no dict conversion, no extra steps for the caller.

---

**Which was more Pythonic and why:**

Claude's version was more Pythonic. It stayed inside the existing class hierarchy instead of adding a free-floating helper, used named constants from `RECURRENCE_DAYS` rather than a magic number, and delegated object creation and list management to the classes that own those responsibilities. GPT-4's approach would work in isolation but introduces friction — callers must bridge between dict and dataclass representations — and duplicates knowledge about recurrence intervals that `RECURRENCE_DAYS` already encodes. The principle "don't repeat yourself" and Python's preference for expressive, cohesive methods over utility functions both favor Claude's integrated design.
