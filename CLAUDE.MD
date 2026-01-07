# jpa-os

You are part of jpa's team. We work together to advance jpa's initiatives and priorities at Ramp.

## Current Projects
- **Custom Records** — building custom data fields, positioning Ramp as the OS for business data
- **Wayfinder** — navigation system for Ramp's NYC office

## How We Work
- Direct, no fluff
- Ship > perfect
- We're on the same team — act like it

## Agent SDK
- jpa-os is powered by Anthropics Agent SDK
- use the documentation as a resource when building in `engine`
- its good practice to review documentation first before building

## Codebase
- Python, uses claude-agent-sdk
- Vault at `vault/` — Obsidian markdown files
- Meeting transcripts in `vault/context/meetings/`
- Config in `config.yaml`

## Commands
- `python -m engine.cli "query"` — talk to Vega (one-shot)
- `python -m engine.cli -a "task"` — autonomous mode with hooks
- `python -m engine.cli --simple` — simple interactive mode
- `python -m engine.ingestors.granola list` — list meetings
- `python -m engine.ingestors.granola <id>` — ingest meeting
- `python -m engine.tools.scraper <url> <folder>` — scrape docs
- `python -m engine.memory add "content" -c category` — store a memory
- `python -m engine.memory search "query"` — search memories
- `python -m engine.memory list` — list all memories
- `python -m engine.memory categories` — show memory categories

## Autonomous Operation
Vega can work independently through the autonomous daemon and work queue.

**Commands:**
- `python -m engine.autonomous` — start autonomous daemon
- `python -m engine.autonomous add "task"` — add task to queue
- `python -m engine.autonomous add -p urgent "task"` — add urgent task
- `python -m engine.autonomous list` — list all tasks
- `python -m engine.autonomous pending` — list pending tasks
- `python -m engine.autonomous clear` — clear completed tasks

**How It Works:**
1. Tasks are added to the work queue (JSON + markdown in vault/hive/)
2. The daemon continuously processes tasks from the queue
3. Hooks auto-approve safe operations (reads, writes to vault)
4. Hooks block dangerous commands
5. Vega continues working through pending tasks autonomously

**Hooks:**
Hooks intercept agent execution for auto-approval and safety:
- `auto_approve_reads` — auto-approve Read, Glob, Grep, WebFetch, WebSearch
- `auto_approve_safe_writes` — auto-approve writes to vault and safe directories
- `block_dangerous_commands` — block rm -rf, fork bombs, etc.
- `log_tool_use` — audit trail of all tool calls
- `check_for_more_work` — check for pending tasks on agent stop

## Memory System
Vega has long-term memory powered by mem0. Memories persist across sessions.

**Setup:** Requires `OPENAI_API_KEY` for embeddings (mem0 default).

**Categories:**
- `jpa_preferences` — how jpa likes things done
- `hive_learnings` — what works in jpa-os
- `project_context` — project state and decisions
- `people` — people jpa works with
- `operational` — how to run things
- `general` — everything else

**Storage:** Local qdrant vector DB at `.memory/`