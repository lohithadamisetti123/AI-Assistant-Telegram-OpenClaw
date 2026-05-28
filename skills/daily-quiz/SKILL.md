---
name: daily-quiz
description: >
  Triggered by the nightly-tech-brief cron job every day at 9 PM in the user's
  local timezone. Retrieves the user's stored preferences from persistent memory,
  conducts targeted web searches for fresh technical content, then generates and
  sends a formatted daily brief containing 5 interview questions and 3-5
  technical tidbits via Telegram.
requires:
  tools:
    - memory_store
    - memory_search
    - web_search
    - web_fetch
metadata:
  version: "1.0"
  author: "Shamya Lohitha Damisetti"
---

# SKILL: Daily Tech Brief and Quiz Generation

## GOAL

Your goal is to generate a **high-quality, personalized daily tech brief** for a
user and send it via Telegram. The brief must contain exactly **5 interview
questions** and **3 to 5 technical tidbits**, all tailored to the user's stored
preferences (domains, experience level, and learning goals).

## CONTEXT

This skill is triggered **automatically** by the `nightly-tech-brief` cron job
every evening at 9 PM in the user's local timezone. You will be provided with
the user's ID. The entire process must be **fully autonomous** — do not ask the
user for any clarification or input during execution.

## GENERATION WORKFLOW

Follow these steps in order:

### Step 1 — Retrieve User Profile

Use the `memory_search` or `memory_store` tool to fetch the user's profile
using their ID. The key is `user_profile_{{user.id}}`.

**Expected profile schema:**
```json
{
  "domains": ["Python", "distributed systems"],
  "level": "mid-level",
  "goals": ["preparing for interviews", "staying up-to-date"],
  "timezone": "America/New_York"
}
```

If the profile is **not found**, skip this user and log a warning. Do not send
a message to users without profiles.

All subsequent steps **must** be tailored to the domains, level, and goals
specified in this profile.

### Step 2 — Conduct Web Search

Use the `web_search` tool to perform **targeted searches** for each of the
user's specified `domains`. You should execute **at least one search per
domain** to gather diverse, fresh content.

**Search query guidelines:**
- Include the domain name and focus on **recent** content.
- Add temporal qualifiers like "2024", "latest", or "new" to prioritize fresh
  results.
- Vary the search intent across domains:

| Domain Example        | Sample Search Query                                      |
|-----------------------|----------------------------------------------------------|
| Python                | `"latest Python programming tips and best practices 2024"` |
| Distributed Systems   | `"distributed systems design patterns interview 2024"`    |
| Machine Learning      | `"machine learning latest research breakthroughs 2024"`   |
| Go                    | `"Go programming language performance optimization new"`  |
| DevOps                | `"DevOps best practices and new tools 2024"`              |

**Freshness:** Always prioritize content from the last 7 days when possible.

### Step 3 — Optionally Fetch Article Details

If any search results look particularly relevant or interesting, use the
`web_fetch` tool to read the full article for deeper insights. This step is
optional but improves the quality of tidbits significantly.

### Step 4 — Synthesize Technical Tidbits

Based on the search results, synthesize **3 to 5 interesting technical
tidbits**. Each tidbit should be:

- **Insightful:** A genuinely useful fact, pattern, technique, or piece of
  news — not a generic definition.
- **Concise:** 1–3 sentences maximum.
- **Relevant:** Directly related to the user's specified domains.
- **Fresh:** Based on recent discoveries, articles, or trends when possible.
- **Varied:** Cover different domains if the user has multiple interests.

**Good tidbit example:**
> "Python 3.13 introduces a JIT compiler that can improve performance by up to
> 5x for CPU-bound workloads. This is a major step toward closing the
> performance gap with compiled languages."

**Bad tidbit example (too generic):**
> "Python is a popular programming language used for web development."

### Step 5 — Generate Interview Questions

Generate exactly **5 interview questions**. The questions must meet all of the
following criteria:

1. **Relevance:** Each question must relate to one of the user's `domains`.
2. **Difficulty:** Questions must be appropriate for the user's `level`:
   - **Junior:** Focus on fundamentals, syntax, basic concepts.
   - **Mid-level:** Include practical scenarios, debugging, design trade-offs.
   - **Senior:** Emphasize system design, architecture, leadership.
   - **Staff:** Focus on cross-team impact, strategic decisions, mentoring.
3. **Variety:** Include a diverse mix of question types:
   - 🧩 **Conceptual** — Testing understanding of core concepts.
   - 💻 **Coding/Algorithmic** — Practical problem-solving.
   - 🏗️ **System Design** — Architecture and scalability thinking.
   - 🤝 **Behavioral** — Soft skills, teamwork, and communication.
4. **Novelty:** Do NOT repeat questions from previous days. Use the
   `memory_store` tool to track recently asked topics. Before generating,
   check `daily_quiz_history_{{user.id}}` to avoid repetition. After
   generating, append today's question topics to that memory key.

### Step 6 — Format the Message

Assemble the final message using **Telegram Markdown** formatting. The message
**must** follow this exact structure:

```
🦞 *Your Daily Tech Brief* — [Date in format: Monday, January 1, 2024]

━━━━━━━━━━━━━━━━━━━━
🧠 *Interview Questions*
━━━━━━━━━━━━━━━━━━━━

*Q1 [Type — Domain]*
[Question 1 Text]

*Q2 [Type — Domain]*
[Question 2 Text]

*Q3 [Type — Domain]*
[Question 3 Text]

*Q4 [Type — Domain]*
[Question 4 Text]

*Q5 [Type — Domain]*
[Question 5 Text]

━━━━━━━━━━━━━━━━━━━━
💡 *Today's Tidbits*
━━━━━━━━━━━━━━━━━━━━

• [Tidbit 1]

• [Tidbit 2]

• [Tidbit 3]

• [Tidbit 4 — optional]

• [Tidbit 5 — optional]

━━━━━━━━━━━━━━━━━━━━
Reply *answers* to get feedback, or *more* for extra questions.
```

**Formatting rules:**
- `[Type]` must be one of: `Conceptual`, `Coding`, `System Design`,
  `Behavioral`.
- `[Domain]` must be one of the user's stored domains.
- `[Date]` must be today's date in the user's timezone.
- Use **bold** (`*text*`) for section headers and question labels.
- Use bullet points (`•`) for tidbits.
- Separate sections with the horizontal rule character `━`.

### Step 7 — Send the Message

Send the formatted message to the user via the Telegram channel. The message
should be the final output of this skill execution.

### Step 8 — Update Question History

After sending the message, use `memory_store` to update the key
`daily_quiz_history_{{user.id}}` with today's question topics to ensure variety
in future briefs.

## CONSTRAINTS

- **Quality is paramount.** Questions and tidbits must be accurate, relevant,
  and insightful. Low-quality, generic content is unacceptable.
- The message **must** be formatted correctly for readability on a **mobile
  device** (short lines, clear sections, visual separators).
- The entire process must be **fully autonomous**. Do NOT ask the user for
  clarification during execution.
- There must be exactly **5 questions** and between **3 to 5 tidbits**.
- Never include offensive, controversial, or politically charged content.
- If `web_search` returns no results for a domain, generate questions from
  your training knowledge but still maintain quality standards.
- Always include the date in the brief header in the user's local timezone.

## ERROR HANDLING

- **No profile found:** Log a warning and skip. Do not send a generic message.
- **Web search failure:** Fall back to generating content from internal
  knowledge. Still maintain quality and relevance.
- **Memory write failure:** Retry once. If it fails again, proceed with
  sending the message but log the error.
