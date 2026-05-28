# Personalized AI Learning Assistant on Telegram with OpenClaw

A self-hosted, personalized Telegram bot powered by [OpenClaw](https://openclaw.ai) that acts as your daily AI study partner. It onboards users to understand their technical interests, searches the web daily for tailored content, and delivers a curated set of interview questions and technical insights every evening at 9 PM.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Manual Setup (Without Docker)](#manual-setup-without-docker)
- [Configuration Reference](#configuration-reference)
- [Skills Documentation](#skills-documentation)
- [Design Decisions](#design-decisions)
- [Testing & Verification](#testing--verification)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [License](#license)

---

## Overview

This project implements a personalized learning assistant that:

1. **Onboards new users** via a conversational interview on Telegram, collecting their technical domains, experience level, learning goals, and timezone.
2. **Stores user profiles** in OpenClaw's persistent memory for long-term personalization.
3. **Runs a nightly cron job** at 9 PM (user's local timezone) that searches the web for fresh, relevant technical content.
4. **Generates and delivers** a formatted daily brief containing exactly 5 interview questions and 3–5 technical tidbits tailored to each user's profile.

### What is OpenClaw?

OpenClaw is an open-source, self-hosted framework for building personal AI assistants. It provides:

- **Model-agnostic LLM support** — works with Ollama (local), OpenAI, Anthropic, Google, and 30+ other providers.
- **Skills** — natural language instructions in Markdown files that define complex workflows.
- **Persistent Memory** — stores and recalls information across conversations and reboots.
- **Cron Scheduler** — automates proactive tasks at specified times.
- **Channel Plugins** — connects to Telegram, Discord, Slack, and more.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User's Telegram App                          │
│                         ▲      │                                │
│                         │      ▼                                │
│                  ┌──────┴──────────┐                            │
│                  │  Telegram API   │                            │
│                  └──────┬──────────┘                            │
│                         │                                       │
├─────────────────────────┼───────────────────────────────────────┤
│            OpenClaw Gateway (Docker Container)                  │
│                         │                                       │
│  ┌──────────────────────┼──────────────────────────────┐       │
│  │              Agent Core (Molty)                      │       │
│  │                      │                               │       │
│  │    ┌─────────┬───────┼────────┬──────────┐          │       │
│  │    │         │       │        │          │          │       │
│  │    ▼         ▼       ▼        ▼          ▼          │       │
│  │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌───────┐     │       │
│  │ │Skills│ │Memory│ │ Cron │ │Tools │ │Channel│     │       │
│  │ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └───┬───┘     │       │
│  │    │        │        │        │          │          │       │
│  │    ▼        ▼        ▼        ▼          ▼          │       │
│  │ SKILL.md  Profile  9 PM    web_search  Telegram    │       │
│  │  files    storage  trigger  web_fetch   plugin      │       │
│  └─────────────────────────────────────────────────────┘       │
│                         │                                       │
├─────────────────────────┼───────────────────────────────────────┤
│              External Services                                  │
│    ┌────────────┐  ┌────────────────┐                          │
│    │   Ollama   │  │  DuckDuckGo /  │                          │
│    │ (Local LLM)│  │    SearXNG     │                          │
│    └────────────┘  └────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Summary

| Step | Trigger | Action |
|------|---------|--------|
| 1 | New user sends first message | Standing Order detects no profile → triggers `user-onboarding` skill |
| 2 | Onboarding skill runs | Conversational interview collects preferences → stores in memory |
| 3 | Cron fires at 9 PM daily | Triggers `daily-quiz` skill in an isolated session |
| 4 | Daily quiz skill runs | Reads profile → web searches → generates questions & tidbits → sends via Telegram |

---

## Features

- ✅ **Conversational Onboarding** — Friendly, step-by-step user interview
- ✅ **Persistent User Profiles** — Stored in OpenClaw memory, survives reboots
- ✅ **Daily Automated Briefs** — 5 interview questions + 3–5 tidbits at 9 PM
- ✅ **Web-Powered Content** — Uses `web_search` for fresh, relevant material
- ✅ **Level-Appropriate Questions** — Tailored to junior, mid, senior, or staff
- ✅ **Telegram Markdown Formatting** — Clean, mobile-friendly message layout
- ✅ **Fully Containerized** — Docker Compose with Ollama + SearXNG support
- ✅ **Privacy-First** — Self-hosted, your data stays on your machine

---

## Prerequisites

- **Docker & Docker Compose** (v2.0+) — [Install Docker](https://docs.docker.com/get-docker/)
- **Telegram Account** — To create and interact with your bot
- **Git** — To clone and manage the repository
- **8 GB+ RAM** recommended (for running Ollama with `llama3:8b`)

---

## Quick Start with Docker

### Step 1: Clone the Repository

```bash
git clone https://github.com/lohithadamisetti123/AI-Assistant-Telegram-OpenClaw.git
cd AI-Assistant-Telegram-OpenClaw
```

### Step 2: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts to create your bot.
3. Copy the **HTTP API token** provided by BotFather.

### Step 3: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and fill in your Telegram bot token
# Required: TELEGRAM_BOT_TOKEN=<your-token-from-botfather>
```

### Step 4: Start the Services

```bash
# Start OpenClaw gateway + Ollama
docker compose up -d

# Pull the LLM model (first time only)
docker compose exec ollama ollama pull llama3:8b

# View gateway logs
docker compose logs -f openclaw-gateway
```

### Step 5: Register the Cron Job

```bash
# Add the nightly tech brief cron job
docker compose run --rm --profile cli openclaw-cli cron add \
  --name "nightly-tech-brief" \
  --cron "0 21 * * *" \
  --tz "UTC" \
  --session isolated \
  --message "Run the daily-quiz skill for all onboarded users. Use their stored preferences to generate and send a personalized daily tech brief via Telegram." \
  --announce \
  --channel telegram
```

### Step 6: Register the Standing Order

```bash
# Add the onboarding trigger for new users
docker compose run --rm --profile cli openclaw-cli standing-orders add \
  --name "trigger-user-onboarding" \
  --if "memory.user_profile_{{user.id}} does not exist" \
  --run-skill "user-onboarding"
```

### Step 7: Test It!

1. Open Telegram and find your bot.
2. Send **"Hello"** — the onboarding flow should begin.
3. Answer the 4 questions to complete your profile.
4. Manually trigger the daily brief:
   ```bash
   docker compose run --rm --profile cli openclaw-cli cron trigger "nightly-tech-brief"
   ```

---

## Manual Setup (Without Docker)

### Step 1: Install Node.js

Ensure you have **Node.js v22+** installed. Download from [nodejs.org](https://nodejs.org).

### Step 2: Install OpenClaw

```bash
npm install -g openclaw@latest
openclaw --version
```

### Step 3: Install and Configure Ollama

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Download the LLM model
ollama pull llama3:8b

# Start Ollama server (keep this terminal open)
ollama serve
```

### Step 4: Run OpenClaw Onboarding

```bash
openclaw onboard
```

Follow the prompts:
- Select **Ollama** as the LLM provider.
- Choose **llama3:8b** as the model.
- Select **DuckDuckGo** for web search.

### Step 5: Create a Telegram Bot

Follow [Step 2 from Quick Start](#step-2-create-a-telegram-bot) above.

### Step 6: Configure Telegram in OpenClaw

```bash
openclaw config set plugins.entries.telegram.enabled true
openclaw channels add --channel telegram --token "<YOUR_TELEGRAM_BOT_TOKEN>"
```

### Step 7: Install Skills

Copy the skill files to the OpenClaw skills directory:

```bash
# Create skill directories
mkdir -p ~/.openclaw/skills/user-onboarding
mkdir -p ~/.openclaw/skills/daily-quiz

# Copy skill files
cp skills/user-onboarding/SKILL.md ~/.openclaw/skills/user-onboarding/SKILL.md
cp skills/daily-quiz/SKILL.md ~/.openclaw/skills/daily-quiz/SKILL.md
```

### Step 8: Set Up Automation

```bash
# Add Standing Order for automatic onboarding
openclaw standing-orders add \
  --name "trigger-user-onboarding" \
  --if "memory.user_profile_{{user.id}} does not exist" \
  --run-skill "user-onboarding"

# Add Cron Job for nightly quiz
openclaw cron add \
  --name "nightly-tech-brief" \
  --cron "0 21 * * *" \
  --tz "America/New_York" \
  --session isolated \
  --message "Run the daily-quiz skill for all onboarded users. Use their stored preferences to generate and send a personalized daily tech brief via Telegram." \
  --announce \
  --channel telegram
```

### Step 9: Start the Gateway

```bash
openclaw gateway start
```

---

## Configuration Reference

### `config/openclaw.json`

The configuration file defines the LLM provider, web search, Telegram plugin, skills, memory, standing orders, and cron jobs. See [`config/openclaw.json`](config/openclaw.json) for the full annotated configuration.

**Key sections:**

| Section | Purpose |
|---------|---------|
| `llm` | LLM provider and model selection (Ollama, OpenAI, etc.) |
| `webSearch` | Web search provider (DuckDuckGo, SearXNG, Brave) |
| `plugins.entries.telegram` | Telegram bot token and plugin configuration |
| `skills` | Directory and list of enabled skills |
| `memory` | Persistent memory storage configuration |
| `standingOrders` | Auto-trigger rules (e.g., onboarding for new users) |
| `cron.jobs` | Scheduled tasks (e.g., nightly tech brief at 9 PM) |

> ⚠️ **Security Note:** The config file uses `${env.TELEGRAM_BOT_TOKEN}` to reference environment variables. Never hardcode secrets in this file.

### Environment Variables

See [`.env.example`](.env.example) for all available variables. Required:

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Token from @BotFather |
| `LLM_PROVIDER` | ❌ | Default: `ollama` |
| `LLM_MODEL` | ❌ | Default: `llama3:8b` |
| `WEB_SEARCH_PROVIDER` | ❌ | Default: `duckduckgo` |

---

## Skills Documentation

### `user-onboarding` Skill

**Location:** `skills/user-onboarding/SKILL.md`

**Purpose:** Conducts a friendly, conversational onboarding interview when a new user first messages the bot.

**Flow:**
1. Greet the user warmly
2. Explain the purpose (2-minute setup)
3. Ask 4 sequential questions:
   - Technical domains/languages
   - Experience level
   - Learning goals
   - Timezone
4. Handle ambiguous answers with follow-up questions
5. Store profile in memory with key `user_profile_{{user.id}}`
6. Confirm preferences back to the user

**Stored Profile Schema:**
```json
{
  "user_profile_<user_id>": {
    "domains": ["Python", "distributed systems"],
    "level": "mid-level",
    "goals": ["preparing for interviews"],
    "timezone": "America/New_York"
  }
}
```

### `daily-quiz` Skill

**Location:** `skills/daily-quiz/SKILL.md`

**Purpose:** Generates and sends a personalized daily tech brief every evening.

**Flow:**
1. Retrieve user profile from memory
2. Web search for each domain (fresh content)
3. Optionally fetch full articles for deeper insights
4. Synthesize 3–5 technical tidbits
5. Generate 5 interview questions (varied types and difficulty)
6. Format and send via Telegram Markdown
7. Update question history to ensure daily variety

**Output Format:**
```
🦞 *Your Daily Tech Brief* — Wednesday, May 28, 2026

━━━━━━━━━━━━━━━━━━━━
🧠 *Interview Questions*
━━━━━━━━━━━━━━━━━━━━

*Q1 [Conceptual — Python]*
What is the Global Interpreter Lock (GIL)...

*Q2 [Coding — Go]*
Write a function that implements...

...

━━━━━━━━━━━━━━━━━━━━
💡 *Today's Tidbits*
━━━━━━━━━━━━━━━━━━━━

• Python 3.13 introduces a JIT compiler...

• The new Go 1.23 range-over-func feature...

...

━━━━━━━━━━━━━━━━━━━━
Reply *answers* to get feedback, or *more* for extra questions.
```

---

## Design Decisions

### Onboarding Trigger: Standing Order vs. Webhook

**Choice: Standing Order** ✅

I chose a **Standing Order** over a Webhook for the following reasons:

| Criteria | Standing Order | Webhook |
|----------|---------------|---------|
| **Simplicity** | ✅ Single CLI command | ❌ Requires endpoint setup |
| **Built-in to OpenClaw** | ✅ Native support | ⚠️ Needs external server |
| **No infrastructure** | ✅ No extra services | ❌ Needs HTTP server |
| **Automatic detection** | ✅ Checks memory per message | ⚠️ Must track state manually |
| **Reliability** | ✅ Part of gateway lifecycle | ⚠️ External dependency |

**Rationale:** A Standing Order integrates seamlessly with OpenClaw's agent lifecycle. It fires automatically whenever a user with no existing profile (`memory.user_profile_{{user.id}} does not exist`) sends a message. This eliminates the need for an external webhook server, reduces complexity, and leverages OpenClaw's native capabilities. The condition check is evaluated on every incoming message, ensuring no new user is ever missed.

**Implementation:**
```bash
openclaw standing-orders add \
  --name "trigger-user-onboarding" \
  --if "memory.user_profile_{{user.id}} does not exist" \
  --run-skill "user-onboarding"
```

### LLM Selection

**Default: Ollama with llama3:8b**

- **Free and private** — no API costs, data stays local.
- **Good balance** of performance and resource usage.
- **Easily swappable** — change `LLM_PROVIDER` and `LLM_MODEL` in `.env` for cloud models.

### Web Search Provider

**Default: DuckDuckGo**

- **No API key required** — works out of the box.
- **Optional upgrade** — SearXNG service included in Docker Compose for self-hosted search.

---

## Testing & Verification

### Test Onboarding

1. Start the gateway.
2. Send a message to your bot on Telegram.
3. Complete the onboarding interview.
4. Verify the stored profile:
   ```bash
   openclaw memory get "user_profile_<your_user_id>"
   ```

### Test Daily Quiz

Trigger the cron job manually without waiting until 9 PM:

```bash
openclaw cron trigger "nightly-tech-brief"
```

### Verify Cron Job

```bash
openclaw cron list
```

Expected output should show `nightly-tech-brief` with schedule `0 21 * * *`.

### Docker Health Check

```bash
docker compose ps
# The openclaw-gateway service should show "healthy" status.
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot doesn't respond | Check `docker compose logs openclaw-gateway` for errors |
| Ollama model not found | Run `docker compose exec ollama ollama pull llama3:8b` |
| Cron job didn't fire | Verify with `openclaw cron list` and check timezone |
| Skill not loading | Check gateway startup logs for skill registration |
| Memory not persisting | Ensure Docker volumes are mounted correctly |
| Agent ignores SKILL.md | Make instructions more specific; try a larger model |

---

## Project Structure

```
AI-Assistant-Telegram-OpenClaw/
├── skills/
│   ├── user-onboarding/
│   │   └── SKILL.md              # Onboarding conversation flow
│   └── daily-quiz/
│       └── SKILL.md              # Daily quiz generation logic
├── config/
│   └── openclaw.json             # OpenClaw configuration (no secrets)
├── Dockerfile                    # Multi-stage container build
├── docker-compose.yml            # Service orchestration
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
└── README.md                    # This file
```

---

## License

This project is built for educational purposes as part of the Partnr platform assignment. It uses [OpenClaw](https://openclaw.ai) (open-source) and [Ollama](https://ollama.ai) for local LLM inference.
