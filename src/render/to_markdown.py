"""Markdown rendering for Substack drafts."""

from typing import List, Optional
from ..util.schema import SubstackDraft, FurtherReading


def render_to_markdown(draft: SubstackDraft) -> str:
    """Render Substack draft to Markdown format."""
    
    # Title
    markdown = f"# {draft.title}\n\n"
    
    # Dek (subtitle)
    markdown += f"*{draft.dek}*\n\n"
    
    # TL;DR section
    markdown += "**TL;DR**\n"
    for point in draft.tldr:
        markdown += f"- {point}\n"
    markdown += "\n"
    
    # Main content
    markdown += "## Main\n"
    
    # Add pull quote if present in body
    if ">" in draft.body_markdown:
        # Extract first blockquote
        lines = draft.body_markdown.split('\n')
        for line in lines:
            if line.strip().startswith('>'):
                markdown += f"\n{line}\n\n"
                break
    
    # Body content
    markdown += f"\n{draft.body_markdown}\n\n"
    
    # Takeaways section
    markdown += "## Takeaways\n"
    
    # Extract takeaways from TL;DR or generate from body
    takeaways = draft.tldr[:3]  # Use first 3 TL;DR points as takeaways
    
    for i, takeaway in enumerate(takeaways, 1):
        markdown += f"- {takeaway}\n"
    
    # Further reading section (if present)
    if draft.further_reading:
        markdown += "\n%% Further reading\n"
        for item in draft.further_reading:
            markdown += f"- [{item.title}]({item.url})\n"
    
    return markdown


def extract_pull_quote(body: str) -> Optional[str]:
    """Extract pull quote from body content."""
    lines = body.split('\n')
    for line in lines:
        if line.strip().startswith('>'):
            return line.strip()
    return None


def format_tags(tags: List[str]) -> str:
    """Format tags for display."""
    return ', '.join(tags)


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def validate_markdown_structure(markdown: str) -> bool:
    """Validate that markdown has required sections."""
    required_sections = ['# ', '**TL;DR**', '## Main', '## Takeaways']
    
    for section in required_sections:
        if section not in markdown:
            return False
    
    return True
