
# engine/tools/scraper.py
"""
Web scraper for ingesting documentation into jpa-os.
Uses Firecrawl to crawl sites and convert to markdown.
"""

from firecrawl import Firecrawl
from dotenv import load_dotenv
from pathlib import Path
import os
import re

load_dotenv()

DOCS_ROOT = Path(__file__).parent.parent.parent / "docs"


def slugify(text: str) -> str:
    """Convert text to filename-safe slug."""
    return re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-')) or "index"


def scrape_docs(url: str, output_folder: str, limit: int = 50) -> list[Path]:
    """
    Crawl a documentation site and save as markdown.
    
    Args:
        url: Base URL to crawl (e.g., "https://docs.example.com/")
        output_folder: Folder name under docs/ (e.g., "agent-sdk")
        limit: Max pages to crawl
    
    Returns:
        List of saved file paths
    """
    app = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
    
    result = app.crawl(
        url,
        limit=limit,
        scrape_options={"formats": ["markdown"]}
    )
    
    docs_dir = DOCS_ROOT / output_folder
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    saved = []
    for page in result.data:
        source_url = page.metadata.source_url if page.metadata else ""
        markdown = page.markdown or ""
        title = page.metadata.title if page.metadata else ""
        
        # Create filename from URL path
        path_parts = source_url.replace(url, "").strip("/").split("/")
        slug = slugify(path_parts[-1] if path_parts else "index")
        
        # Add title as h1 if not present
        if markdown and not markdown.startswith("# "):
            markdown = f"# {title}\n\n{markdown}"
        
        filepath = docs_dir / f"{slug}.md"
        filepath.write_text(markdown)
        saved.append(filepath)
    
    return saved


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python -m engine.tools.scraper <url> <folder> [limit]")
        print("Example: python -m engine.tools.scraper https://docs.example.com/ my-docs 20")
        sys.exit(1)
    
    url = sys.argv[1]
    folder = sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    
    print(f"Crawling {url}...")
    paths = scrape_docs(url, folder, limit)
    print(f"✓ Saved {len(paths)} pages to docs/{folder}/")