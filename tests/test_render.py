"""Tests for rendering modules."""

import pytest
from src.render.to_markdown import render_to_markdown, validate_markdown_structure, word_count
from src.render.to_html import render_to_html, create_substack_friendly_html, validate_html_structure
from src.util.schema import SubstackDraft, FurtherReading


class TestMarkdownRendering:
    """Test Markdown rendering functionality."""
    
    def test_basic_markdown_rendering(self):
        """Test basic markdown rendering."""
        draft = SubstackDraft(
            title="Test Article",
            dek="A test article about something interesting",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test", "article", "example"],
            body_markdown="This is the main body content with some details."
        )
        
        markdown = render_to_markdown(draft)
        
        assert "# Test Article" in markdown
        assert "*A test article about something interesting*" in markdown
        assert "**TL;DR**" in markdown
        assert "- Point 1" in markdown
        assert "- Point 2" in markdown
        assert "- Point 3" in markdown
        assert "## Main" in markdown
        assert "This is the main body content" in markdown
        assert "## Takeaways" in markdown
    
    def test_markdown_with_pull_quote(self):
        """Test markdown rendering with pull quote."""
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="Some content.\n\n> This is a pull quote\n\nMore content."
        )
        
        markdown = render_to_markdown(draft)
        
        assert "> This is a pull quote" in markdown
    
    def test_markdown_with_further_reading(self):
        """Test markdown rendering with further reading."""
        further_reading = [
            FurtherReading(title="Test Article", url="https://example.com"),
            FurtherReading(title="Another Article", url="https://test.com")
        ]
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="Test content",
            further_reading=further_reading
        )
        
        markdown = render_to_markdown(draft)
        
        assert "%% Further reading" in markdown
        assert "[Test Article](https://example.com)" in markdown
        assert "[Another Article](https://test.com)" in markdown
    
    def test_markdown_structure_validation(self):
        """Test markdown structure validation."""
        valid_markdown = """# Title

*Dek*

**TL;DR**
- Point 1
- Point 2

## Main
Content here

## Takeaways
- Takeaway 1
- Takeaway 2
"""
        
        assert validate_markdown_structure(valid_markdown) is True
        
        invalid_markdown = "Just some content without proper structure"
        assert validate_markdown_structure(invalid_markdown) is False
    
    def test_word_count_function(self):
        """Test word count function."""
        text = "This is a test sentence with seven words."
        assert word_count(text) == 7
        
        empty_text = ""
        assert word_count(empty_text) == 0
        
        multiline_text = "Line one\nLine two\nLine three"
        assert word_count(multiline_text) == 6


class TestHTMLRendering:
    """Test HTML rendering functionality."""
    
    def test_basic_html_rendering(self):
        """Test basic HTML rendering."""
        draft = SubstackDraft(
            title="Test Article",
            dek="A test article about something interesting",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test", "article", "example"],
            body_markdown="This is the main body content with some details."
        )
        
        html = render_to_html(draft)
        
        assert "<!DOCTYPE html>" in html
        assert "<title>Test Article</title>" in html
        assert "<h1>Test Article</h1>" in html
        assert "<em>A test article about something interesting</em>" in html
        assert "<h3>TL;DR</h3>" in html
        assert "<li>Point 1</li>" in html
        assert "<h2>Main</h2>" in html
        assert "This is the main body content" in html
        assert "<h2>Takeaways</h2>" in html
    
    def test_html_with_further_reading(self):
        """Test HTML rendering with further reading."""
        further_reading = [
            FurtherReading(title="Test Article", url="https://example.com"),
            FurtherReading(title="Another Article", url="https://test.com")
        ]
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="Test content",
            further_reading=further_reading
        )
        
        html = render_to_html(draft)
        
        assert "<h2>Further Reading</h2>" in html
        assert '<a href="https://example.com">Test Article</a>' in html
        assert '<a href="https://test.com">Another Article</a>' in html
    
    def test_substack_friendly_html(self):
        """Test Substack-friendly HTML generation."""
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="Test content"
        )
        
        html = create_substack_friendly_html(draft)
        
        assert "<h1>Test Article</h1>" in html
        assert "<p><em>Test dek</em></p>" in html
        assert "<h3>TL;DR</h3>" in html
        assert "<ul>" in html
        assert "<li>Point 1</li>" in html
        assert "<h2>Main</h2>" in html
        assert "<h2>Takeaways</h2>" in html
    
    def test_html_structure_validation(self):
        """Test HTML structure validation."""
        valid_html = """<h1>Title</h1>
<p>Content</p>
<h3>TL;DR</h3>
<ul>
<li>Point 1</li>
<li>Point 2</li>
</ul>"""
        
        assert validate_html_structure(valid_html) is True
        
        invalid_html = "Just some text without proper HTML structure"
        assert validate_html_structure(invalid_html) is False
    
    def test_html_css_styling(self):
        """Test that HTML includes CSS styling."""
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="Test content"
        )
        
        html = render_to_html(draft)
        
        assert "<style>" in html
        assert "font-family" in html
        assert "body {" in html
        assert "h1 {" in html
        assert "blockquote {" in html
    
    def test_markdown_to_html_conversion(self):
        """Test markdown to HTML conversion."""
        from src.render.to_html import render_markdown_to_html
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="This is **bold** text and *italic* text."
        )
        
        html = render_markdown_to_html(draft)
        
        assert "<h1>Test Article</h1>" in html
        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html
    
    def test_empty_draft_rendering(self):
        """Test rendering of minimal draft."""
        draft = SubstackDraft(
            title="Minimal",
            dek="Minimal dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["minimal", "test", "basic"],
            body_markdown="Minimal content."
        )
        
        markdown = render_to_markdown(draft)
        html = render_to_html(draft)
        
        assert "# Minimal" in markdown
        assert "<h1>Minimal</h1>" in html
        assert validate_markdown_structure(markdown) is True
        assert validate_html_structure(html) is True
    
    def test_long_content_rendering(self):
        """Test rendering of longer content."""
        # Create content with multiple paragraphs
        body_content = "This is a longer article with multiple paragraphs.\n\n" * 20
        
        draft = SubstackDraft(
            title="Long Article",
            dek="A longer article with more content",
            tldr=["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
            tags=["long", "article", "content", "test", "example"],
            body_markdown=body_content
        )
        
        markdown = render_to_markdown(draft)
        html = render_to_html(draft)
        
        assert len(markdown) > 1000
        assert len(html) > 1000
        assert validate_markdown_structure(markdown) is True
        assert validate_html_structure(html) is True
