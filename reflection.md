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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Answer: The conflict detector checks all pairs of tasks (O(n²)) rather than sorting by start time first and only checking neighbors (O(n log n)). For a pet care app with a small number of daily tasks, the simpler pairwise approach is fine and easier to read. A more efficient algorithm would only pay off with hundreds of tasks, which isn't a realistic scenario here.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
