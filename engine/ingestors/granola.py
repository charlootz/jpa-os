"""
Granola transcript ingestor.
Reads from local Granola cache and writes markdown to vault.
"""

import json
from pathlib import Path
from datetime import datetime

GRANOLA_CACHE = Path.home() / "Library/Application Support/Granola/cache-v3.json"
VAULT_MEETINGS = Path(__file__).parent.parent.parent / "vault/context/meetings"


def load_cache():
    """Load and parse the Granola cache."""
    with open(GRANOLA_CACHE) as f:
        data = json.load(f)
    cache = json.loads(data['cache'])
    return cache['state']


def get_meetings_with_transcripts():
    """Return list of meetings that have transcripts."""
    state = load_cache()
    docs = state.get('documents', {})
    transcripts = state.get('transcripts', {})
    
    meetings = []
    for doc_id, doc in docs.items():
        if doc_id in transcripts and len(transcripts[doc_id]) > 0:
            meetings.append({
                'id': doc_id,
                'title': doc.get('title', 'Untitled'),
                'segments': len(transcripts[doc_id]),
                'doc': doc,
                'transcript': transcripts[doc_id]
            })
    
    return sorted(meetings, key=lambda x: x['segments'], reverse=True)


def format_transcript(transcript: list) -> str:
    """Convert transcript segments to readable text."""
    lines = []
    for seg in transcript:
        source = seg.get('source', '?')
        speaker = 'Me' if source == 'microphone' else 'Them'
        text = seg.get('text', '').strip()
        if text:
            lines.append(f"**{speaker}:** {text}")
    return "\n\n".join(lines)


def get_meeting_date(transcript: list) -> str:
    """Extract date from first transcript segment."""
    if transcript and len(transcript) > 0:
        ts = transcript[0].get('start_timestamp', '')
        if ts:
            return ts[:10]  # YYYY-MM-DD
    return datetime.now().strftime('%Y-%m-%d')


def slugify(title: str) -> str:
    """Convert title to filename-safe slug."""
    return "".join(c if c.isalnum() or c in ' -' else '' for c in title).strip().replace(' ', '-').lower()


def ingest_meeting(doc_id: str) -> Path:
    """Ingest a single meeting by ID and save to vault."""
    state = load_cache()
    docs = state.get('documents', {})
    transcripts = state.get('transcripts', {})
    
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found")
    
    doc = docs[doc_id]
    transcript = transcripts.get(doc_id, [])
    
    title = doc.get('title', 'Untitled')
    date = get_meeting_date(transcript)
    slug = slugify(title)
    
    # Build markdown
    md = f"""# {title}

**Date:** {date}
**Segments:** {len(transcript)}

---

## Transcript

{format_transcript(transcript)}
"""
    
    # Save to vault
    VAULT_MEETINGS.mkdir(parents=True, exist_ok=True)
    filename = f"{date}-{slug}.md"
    filepath = VAULT_MEETINGS / filename
    filepath.write_text(md)
    
    return filepath


def list_meetings():
    """Print available meetings with transcripts."""
    meetings = get_meetings_with_transcripts()
    print(f"Found {len(meetings)} meetings with transcripts:\n")
    for m in meetings[:15]:
        print(f"  {m['segments']:4d} segments | {m['title'][:45]:<45} | {m['id']}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_meetings()
        else:
            # Assume it's a doc ID
            path = ingest_meeting(sys.argv[1])
            print(f"✓ Saved to {path}")
    else:
        print("Usage:")
        print("  python -m engine.ingestors.granola list")
        print("  python -m engine.ingestors.granola <doc_id>")