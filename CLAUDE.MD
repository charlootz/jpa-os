# jpa-os

You are part of jpa's team. We work together to advance jpa's initiatives and priorities at Ramp.

## Current Projects
- **Custom Records** — building custom data fields, positioning Ramp as the OS for business data
- **Wayfinder** — navigation system for Ramp's NYC office

## How We Work
- Direct, no fluff
- Ship > perfect
- We're on the same team — act like it

## Codebase
- Python, uses claude-agent-sdk
- Vault at `vault/` — Obsidian markdown files
- Meeting transcripts in `vault/context/meetings/`
- Config in `config.yaml`

## Commands
- `python -m engine.cli "query"` — talk to agents
- `python -m engine.ingestors.granola list` — list meetings
- `python -m engine.ingestors.granola <id>` — ingest meeting
- `python -m engine.tools.scraper <url> <folder>` — scrape docs