"""
Vault tools for reading/writing markdown files.
"""

from pathlib import Path

VAULT_ROOT = Path(__file__).parent.parent.parent / "vault"


def read_file(path: str) -> str:
    """Read a file from the vault. Path is relative to vault root."""
    filepath = VAULT_ROOT / path
    if filepath.exists():
        return filepath.read_text()
    return ""


def write_file(path: str, content: str) -> Path:
    """Write content to a file in the vault. Creates directories if needed."""
    filepath = VAULT_ROOT / path
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content)
    return filepath


def append_file(path: str, content: str) -> Path:
    """Append content to a file in the vault."""
    filepath = VAULT_ROOT / path
    filepath.parent.mkdir(parents=True, exist_ok=True)
    existing = filepath.read_text() if filepath.exists() else ""
    filepath.write_text(existing + "\n" + content)
    return filepath


def list_files(folder: str, pattern: str = "*.md") -> list[str]:
    """List files in a vault folder matching pattern."""
    folderpath = VAULT_ROOT / folder
    if not folderpath.exists():
        return []
    return [str(f.relative_to(VAULT_ROOT)) for f in folderpath.glob(pattern)]


def search_meetings(query: str, limit: int = 3) -> str:
    """Search meeting transcripts for a query. Returns matching excerpts."""
    meetings_dir = VAULT_ROOT / "context" / "meetings"
    if not meetings_dir.exists():
        return "(no meetings found)"
    
    results = []
    query_lower = query.lower()
    
    for filepath in meetings_dir.glob("*.md"):
        content = filepath.read_text()
        if query_lower in content.lower():
            # Extract title and relevant snippet
            lines = content.split("\n")
            title = lines[0].replace("# ", "") if lines else filepath.stem
            
            # Find lines containing the query
            matching_lines = []
            for i, line in enumerate(lines):
                if query_lower in line.lower():
                    # Get some context around the match
                    start = max(0, i - 1)
                    end = min(len(lines), i + 2)
                    snippet = "\n".join(lines[start:end])
                    matching_lines.append(snippet)
                    if len(matching_lines) >= 2:
                        break
            
            results.append({
                'title': title,
                'file': filepath.name,
                'snippets': matching_lines
            })
            
            if len(results) >= limit:
                break
    
    if not results:
        return f"(no meetings found matching '{query}')"
    
    output = []
    for r in results:
        output.append(f"### {r['title']}\n_File: {r['file']}_\n")
        for snippet in r['snippets']:
            output.append(f">{snippet}\n")
    
    return "\n".join(output)


def get_recent_meetings(limit: int = 3) -> str:
    """Get the most recent meeting transcripts."""
    meetings_dir = VAULT_ROOT / "context" / "meetings"
    if not meetings_dir.exists():
        return "(no meetings found)"
    
    # Sort by filename (which starts with date)
    files = sorted(meetings_dir.glob("*.md"), reverse=True)[:limit]
    
    output = []
    for f in files:
        content = f.read_text()
        lines = content.split("\n")
        
        # Get title and first ~500 chars
        title = lines[0].replace("# ", "") if lines else f.stem
        preview = content[:500] + "..." if len(content) > 500 else content
        
        output.append(f"### {title}\n_File: {f.name}_\n\n{preview}\n")
    
    return "\n---\n".join(output)