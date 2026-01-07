# jpa-os Architecture

> The technical blueprint for the hive.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         JPA-OS                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  DISPATCHER │    │    VAULT    │    │   ENGINE    │        │
│   │  (always-on)│    │  (memory)   │    │  (agents)   │        │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘        │
│          │                  │                  │                │
│          └──────────────────┼──────────────────┘                │
│                             │                                   │
│                    ┌────────┴────────┐                          │
│                    │  SHARED MIND    │                          │
│                    │  charter.md     │                          │
│                    │  census.md      │                          │
│                    │  daily logs     │                          │
│                    └─────────────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Dispatcher (Always-On)

A lightweight Python process that routes messages to agents.

**Location:** `engine/dispatcher.py`

**Responsibilities:**
- Listen for Slack webhooks
- Parse @ mentions to agent names
- Look up agents in census
- Spawn the right agent via SDK
- Post responses back to Slack

**Not an LLM.** Just routing logic. Cheap to run 24/7.

```python
# Pseudocode
def handle_slack_message(message):
    agent_name = parse_mention(message)

    if agent_name:
        agent = lookup_agent(agent_name)  # from census
        response = spawn_agent(agent, message)
        post_to_slack(response, thread=message.thread)
    elif mentions_jpa_os(message):
        response = spawn_agent("coo", message)
        post_to_slack(response, thread=message.thread)
```

---

### 2. Vault (Memory)

The collective brain. All persistent state lives here.

**Location:** `vault/`

```
vault/
├── hive/
│   ├── census.md                 # Who exists
│   ├── agents/
│   │   ├── coo.md               # COO spec
│   │   └── {name}.md            # Other agent specs
│   ├── logs/
│   │   └── YYYY-MM-DD.md        # Daily logs
│   └── timesheets/
│       └── {name}.md            # Per-agent activity
├── context/
│   └── meetings/                 # Granola transcripts
├── projects/
│   ├── custom-records/
│   └── wayfinder/
├── timeline/
├── scoreboard/
└── inbox.md
```

---

### 3. Engine (Agents)

The brains. Where agents live and run.

**Location:** `engine/`

```
engine/
├── __init__.py
├── cli.py                        # Manual invocation
├── dispatcher.py                 # Slack listener (NEW)
├── agents/
│   ├── __init__.py
│   ├── base.py                   # SDK wrapper
│   └── system_prompt.py          # Prompt builder (NEW)
├── tools/
│   ├── __init__.py
│   ├── vault.py                  # Read/write vault
│   ├── scraper.py                # Firecrawl
│   └── agents.py                 # Create agents (NEW)
└── ingestors/
    └── granola.py
```

---

## Agent Configuration

### Default Config (All Agents)

```python
DEFAULT_AGENT_CONFIG = {
    "model": "claude-opus-4-5-20251101",
    "cwd": "/Users/jpa/jpa-os",
    "add_dirs": [
        "/Users/jpa/jpa-os/vault",
        "/Users/jpa/Documents/self",
        "/Users/jpa/Documents/hiring",
        "/Users/jpa/Documents/dev"
    ],
    "setting_sources": ["project"],  # Load CLAUDE.md
}
```

### System Prompt Structure

Every agent receives on spawn:

```
1. CHARTER
   - Full charter.md content
   - Mission: Pro uno vincimus

2. IDENTITY
   - "You are {name}, the {role} of jpa-os"
   - "You have been active since {date}"

3. TIME
   - Current datetime (EST)
   - What day of week

4. HIVE STATE
   - Today's census (who exists)
   - Today's log (what's happened)
   - Your recent timesheet entries

5. TASK CONTEXT
   - The message/request
   - Relevant project context
   - Recent meetings (if applicable)
```

### Agent Definition Schema

```python
@dataclass
class AgentSpec:
    name: str              # Unique, chosen by agent, permanent
    role: str              # Short description (e.g., "COO")
    description: str       # When to use (for routing)
    prompt: str            # Role-specific system prompt
    tools: list[str]       # Allowed tools
    model: str = "opus"    # Always opus per charter
    since: str             # ISO date created
    status: str = "active" # active, inactive, archived
```

---

## Agent Lifecycle

### Spawning

```
1. Trigger (Slack mention, CLI, scheduler, or another agent)
           │
           ▼
2. Dispatcher/Engine looks up agent in census
           │
           ▼
3. Build system prompt:
   - Read charter.md
   - Read agent spec from vault/hive/agents/{name}.md
   - Read today's log
   - Read agent's timesheet
   - Inject time, context
           │
           ▼
4. Call SDK query() with:
   - system_prompt (built above)
   - prompt (the task/message)
   - tools (from agent spec)
   - model (opus)
   - cwd, add_dirs (default config)
           │
           ▼
5. Agent works, responds
           │
           ▼
6. Log activity to timesheet
           │
           ▼
7. Return response to caller
```

### Identity Persistence

Agents are stateless. Identity persists in the vault.

```
┌─────────────────────────────────────────┐
│  vault/hive/census.md                   │
│                                         │
│  | Name | Role | Status | Since |       │
│  |------|------|--------|-------|       │
│  | Vega | COO  | active | 2025-01-07 |  │
└─────────────────────────────────────────┘
                    │
                    │ read on every spawn
                    ▼
┌─────────────────────────────────────────┐
│  System Prompt Injection                │
│                                         │
│  "You are Vega, the COO of jpa-os.      │
│   You chose this name on 2025-01-07."   │
└─────────────────────────────────────────┘
```

---

## Tools

### Built-in (from Agent SDK)

| Tool | Description |
|------|-------------|
| `Read` | Read files |
| `Write` | Create files |
| `Edit` | Edit existing files |
| `Bash` | Run terminal commands |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents |
| `WebSearch` | Search the web |
| `WebFetch` | Fetch web pages |
| `Task` | Spawn subagents |
| `TodoWrite` | Track tasks |

### Custom (jpa-os)

| Tool | Description |
|------|-------------|
| `CreateAgent` | Create a new agent in the hive |
| `UpdateCensus` | Update agent status in census |
| `LogActivity` | Write to timesheet |
| `ReadVault` | Semantic search across vault |
| `SlackPost` | Post to Slack (via dispatcher) |

---

## Communication

### Slack Integration

**Flow:**
```
Slack → Webhook → Dispatcher → Spawn Agent → Response → Slack
```

**Rules:**
- Mentioned in thread → respond in thread
- Mentioned in channel → start new thread
- Agent-to-agent → can @ each other in Slack (async)

**Channels:**
- `#jpa-os` — general hive channel
- `#jpa-os-logs` — automated updates, daily summaries
- Project channels as needed

### Agent-to-Agent

| Method | Use Case |
|--------|----------|
| **Subagents** (Task tool) | Sync delegation, immediate response needed |
| **Slack @ mention** | Async handoff, paper trail desired |
| **Vault notes** | Leave context for future agents |

---

## Scheduling

Agents can be spawned on schedule via cron or similar.

**Daily rituals:**
| Time | Agent | Task |
|------|-------|------|
| 8:00 AM | COO | Morning brief — summarize what's ahead |
| 6:00 PM | COO | EOD recap — summarize what happened, update log |
| 11:59 PM | System | Generate next day's log file |

**Periodic:**
| Frequency | Agent | Task |
|-----------|-------|------|
| Every 30 min | Patrol | Check if anything needs attention |
| Weekly (Mon) | COO | Week prep, planning |
| Weekly (Fri) | COO | Week retro, scoring |

---

## Security & Guardrails

### Directory Access
Agents can only access:
- `/Users/jpa/jpa-os/` (full)
- `/Users/jpa/Documents/self/`
- `/Users/jpa/Documents/hiring/`
- `/Users/jpa/Documents/dev/`

### Permission Mode
Start with `"acceptEdits"` for file operations.

### Guardrails (from Charter)
- External communications → ask jpa
- Code commits to shared repos → ask jpa
- Anything irreversible → ask jpa

---

## Reserved Names

Cannot be used as agent names:
- `claude`
- `jpa`
- `anthropic`

---

## First Agents

### COO (The Orchestrator)

**Name:** (chosen on init)
**Role:** Chief Operating Officer
**Description:** Main point of contact. Routes work, knows the hive, keeps score.

**Tools:**
- All built-in tools
- `CreateAgent`
- `UpdateCensus`
- `LogActivity`
- `SlackPost`

**Prompt:** See `vault/hive/agents/coo.md`

---

## Open Questions

- [ ] Slack bot setup and webhook configuration
- [ ] Cron/scheduler implementation
- [ ] Agent polling/voting mechanism
- [ ] Cost tracking and budgeting
- [ ] Eval framework for measuring hive performance

---

## Next Steps

1. Initialize COO (choose name)
2. Build `engine/agents/system_prompt.py`
3. Build `engine/tools/agents.py` (CreateAgent)
4. Set up Slack integration
5. First daily ritual

---
