# JPA-OS

> Agents working together to advance jpa's initiatives.

**Location:** `~/jpa-os/`
**Vault:** `~/jpa-os/vault/` (Obsidian)

---

## Mission

jpa is building products at Ramp. The agents are on his team. They work at all costs to advance jpa's initiatives and priorities.

This is not a tool jpa uses. This is a team jpa is on.

---

## Architecture

```
~/jpa-os/
├── engine/
│   ├── __init__.py
│   ├── context.py              ✅ builds prompt context
│   ├── cli.py                  ✅ python -m engine.cli "query"
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   └── base.py             ✅ claude-agent-sdk wrapper
│   │
│   ├── ingestors/
│   │   ├── __init__.py
│   │   └── granola.py          ✅ meeting transcripts → vault
│   │
│   └── tools/
│       ├── __init__.py
│       ├── vault.py            ✅ read/write/search markdown
│       └── scraper.py          ✅ firecrawl doc scraper
│
├── vault/                      ✅ Obsidian vault
│   ├── context/
│   │   └── meetings/           ✅ granola transcripts
│   ├── projects/
│   │   ├── custom-records/
│   │   └── wayfinder/
│   ├── timeline/
│   ├── scoreboard/
│   └── inbox.md
│
├── docs/
│   └── agent-sdk/              ✅ scraped claude agent sdk docs
│
├── config.yaml                 ✅ projects, people, context
├── .env                        ✅ API keys
└── .gitignore                  ✅
```

---

## What Works

```bash
cd ~/jpa-os
source .venv/bin/activate

# Talk to agent
python -m engine.cli "what's going on with custom records"

# Ingest meetings
python -m engine.ingestors.granola list
python -m engine.ingestors.granola <doc_id>

# Scrape docs
python -m engine.tools.scraper "https://example.com/docs/" folder-name 20
```

---

## Data Sources

| Source | Access | Status |
|--------|--------|--------|
| Granola | Local cache | ✅ Working |
| Slack | MCP | 🔲 TODO |
| Ramp Repos | Local filesystem | 🔲 TODO |
| Calendar | API | 🔲 TODO |

---

## Dependencies

```
claude-agent-sdk
pyyaml
pytz
python-dotenv
textual
firecrawl-py
```

---

## Environment

```bash
# Always activate venv (Nix requirement)
cd ~/jpa-os
source .venv/bin/activate
```

```
# .env
ANTHROPIC_API_KEY=sk-ant-...
FIRECRAWL_API_KEY=fc-...
```

---

## Next: Build the Product

Open Claude Code. Build.

```bash
cd ~/jpa-os
claude
```
