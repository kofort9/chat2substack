"""Tests for HTML ingestion module."""

import pytest
import tempfile
from pathlib import Path
from src.ingest.from_shared_html import ingest_shared_html, extract_messages_from_html


class TestHTMLIngestion:
    """Test HTML ingestion functionality."""
    
    def test_extract_messages_simple(self):
        """Test extracting messages from simple HTML."""
        html = """
        <html>
        <body>
            <div class="conversation-turn">
                <div data-message-author-role="user">What is AI?</div>
            </div>
            <div class="conversation-turn">
                <div data-message-author-role="assistant">AI is artificial intelligence.</div>
            </div>
        </body>
        </html>
        """
        
        messages = extract_messages_from_html(html)
        assert len(messages) == 2
        assert messages[0] == ('user', 'What is AI?')
        assert messages[1] == ('assistant', 'AI is artificial intelligence.')
    
    def test_extract_messages_with_role_prefix(self):
        """Test extracting messages with role prefixes."""
        html = """
        <html>
        <body>
            <div>User: Hello, how are you?</div>
            <div>Assistant: I'm doing well, thank you!</div>
        </body>
        </html>
        """
        
        messages = extract_messages_from_html(html)
        assert len(messages) == 2
        assert messages[0] == ('user', 'Hello, how are you?')
        assert messages[1] == ('assistant', "I'm doing well, thank you!")
    
    def test_extract_title_hint(self):
        """Test extracting title from HTML."""
        html = """
        <html>
        <head><title>AI Discussion - ChatGPT</title></head>
        <body>
            <h1>Understanding Artificial Intelligence</h1>
            <div class="conversation-turn">
                <div data-message-author-role="user">What is AI?</div>
            </div>
        </body>
        </html>
        """
        
        from src.ingest.from_shared_html import extract_title_hint
        title = extract_title_hint(html)
        assert "Understanding Artificial Intelligence" in title
    
    def test_ingest_shared_html_file(self):
        """Test ingesting from actual HTML file."""
        html_content = """
        <html>
        <head><title>Test Conversation</title></head>
        <body>
            <div class="conversation-turn">
                <div data-message-author-role="user">What is machine learning?</div>
            </div>
            <div class="conversation-turn">
                <div data-message-author-role="assistant">Machine learning is a subset of AI.</div>
            </div>
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            conversation = ingest_shared_html(temp_path)
            
            assert conversation.source.type == "shared_html"
            assert len(conversation.messages) == 2
            assert conversation.messages[0].role == "user"
            assert conversation.messages[0].text == "What is machine learning?"
            assert conversation.messages[1].role == "assistant"
            assert conversation.messages[1].text == "Machine learning is a subset of AI."
            
        finally:
            Path(temp_path).unlink()
    
    def test_ingest_empty_html(self):
        """Test ingesting empty HTML file."""
        html_content = "<html><body></body></html>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="No messages found"):
                ingest_shared_html(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_ingest_nonexistent_file(self):
        """Test ingesting non-existent file."""
        with pytest.raises(FileNotFoundError):
            ingest_shared_html("nonexistent.html")
    
    def test_message_role_normalization(self):
        """Test that role names are normalized correctly."""
        html = """
        <html>
        <body>
            <div data-message-author-role="Human">Hello</div>
            <div data-message-author-role="AI">Hi there</div>
            <div data-message-author-role="ChatGPT">How can I help?</div>
        </body>
        </html>
        """
        
        messages = extract_messages_from_html(html)
        assert len(messages) == 3
        assert messages[0][0] == 'user'  # Human -> user
        assert messages[1][0] == 'assistant'  # AI -> assistant
        assert messages[2][0] == 'assistant'  # ChatGPT -> assistant
