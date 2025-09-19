"""HTML rendering for Substack drafts."""

import markdown
from typing import List
from ..util.schema import SubstackDraft


def render_to_html(draft: SubstackDraft) -> str:
    """Render Substack draft to HTML format."""
    
    # Convert markdown to HTML first
    markdown_content = render_markdown_to_html(draft)
    
    # Wrap in basic HTML structure
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{draft.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        .dek {{
            font-size: 1.1em;
            color: #666;
            margin-bottom: 20px;
        }}
        .tldr {{
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .tldr h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .further-reading {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 30px;
        }}
        .further-reading h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .further-reading a {{
            color: #3498db;
            text-decoration: none;
        }}
        .further-reading a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    {markdown_content}
</body>
</html>"""
    
    return html


def render_markdown_to_html(draft: SubstackDraft) -> str:
    """Convert draft to HTML using markdown library."""
    
    # Build markdown content
    markdown_content = f"# {draft.title}\n\n"
    markdown_content += f"*{draft.dek}*\n\n"
    
    # TL;DR section
    markdown_content += "**TL;DR**\n"
    for point in draft.tldr:
        markdown_content += f"- {point}\n"
    markdown_content += "\n"
    
    # Main content
    markdown_content += "## Main\n\n"
    markdown_content += draft.body_markdown
    markdown_content += "\n\n"
    
    # Takeaways section
    markdown_content += "## Takeaways\n"
    for point in draft.tldr[:3]:  # Use first 3 TL;DR points
        markdown_content += f"- {point}\n"
    
    # Further reading section
    if draft.further_reading:
        markdown_content += "\n## Further Reading\n"
        for item in draft.further_reading:
            markdown_content += f"- [{item.title}]({item.url})\n"
    
    # Convert to HTML
    html = markdown.markdown(
        markdown_content,
        extensions=['fenced_code', 'tables', 'toc']
    )
    
    return html


def create_substack_friendly_html(draft: SubstackDraft) -> str:
    """Create HTML optimized for Substack import."""
    
    # Substack prefers simple HTML without custom CSS
    html = f"""<h1>{draft.title}</h1>
<p><em>{draft.dek}</em></p>

<h3>TL;DR</h3>
<ul>
"""
    
    for point in draft.tldr:
        html += f"<li>{point}</li>\n"
    
    html += """</ul>

<h2>Main</h2>
"""
    
    # Convert body markdown to HTML
    body_html = markdown.markdown(draft.body_markdown)
    html += body_html
    
    html += """
<h2>Takeaways</h2>
<ul>
"""
    
    for point in draft.tldr[:3]:
        html += f"<li>{point}</li>\n"
    
    html += "</ul>\n"
    
    # Further reading
    if draft.further_reading:
        html += "<h2>Further Reading</h2>\n<ul>\n"
        for item in draft.further_reading:
            html += f'<li><a href="{item.url}">{item.title}</a></li>\n'
        html += "</ul>\n"
    
    return html


def validate_html_structure(html: str) -> bool:
    """Validate that HTML has required elements."""
    required_elements = ['<h1>', '<h3>', '<ul>', '<li>']
    
    for element in required_elements:
        if element not in html:
            return False
    
    return True
