"""Tests for Pydantic schemas."""

import pytest
from datetime import datetime
from src.util.schema import (
    Message, SourceInfo, NormalizedConversation, 
    SubstackDraft, FurtherReading, GuardrailResult, RunReport
)


class TestMessageSchema:
    """Test Message schema validation."""
    
    def test_valid_message(self):
        """Test valid message creation."""
        message = Message(role="user", text="Hello world")
        assert message.role == "user"
        assert message.text == "Hello world"
    
    def test_invalid_role(self):
        """Test invalid role validation."""
        with pytest.raises(ValueError):
            Message(role="invalid", text="Hello world")
    
    def test_message_serialization(self):
        """Test message serialization."""
        message = Message(role="assistant", text="Hi there")
        data = message.model_dump()
        assert data["role"] == "assistant"
        assert data["text"] == "Hi there"


class TestSourceInfoSchema:
    """Test SourceInfo schema validation."""
    
    def test_valid_source_info(self):
        """Test valid source info creation."""
        source = SourceInfo(type="shared_html", path="/path/to/file.html")
        assert source.type == "shared_html"
        assert source.path == "/path/to/file.html"
        assert source.url is None
    
    def test_source_info_with_url(self):
        """Test source info with URL."""
        source = SourceInfo(
            type="shared_html", 
            path="/path/to/file.html",
            url="https://chat.openai.com/share/abc123"
        )
        assert source.url == "https://chat.openai.com/share/abc123"
    
    def test_invalid_source_type(self):
        """Test invalid source type validation."""
        with pytest.raises(ValueError):
            SourceInfo(type="invalid", path="/path/to/file.html")


class TestNormalizedConversationSchema:
    """Test NormalizedConversation schema validation."""
    
    def test_valid_conversation(self):
        """Test valid conversation creation."""
        conversation = NormalizedConversation(
            id="2024-01-01T12:00:00",
            source=SourceInfo(type="manual_text", path="test.txt"),
            title_hint="Test Conversation",
            messages=[
                Message(role="user", text="Hello"),
                Message(role="assistant", text="Hi there")
            ]
        )
        assert len(conversation.messages) == 2
        assert conversation.title_hint == "Test Conversation"
    
    def test_empty_messages_validation(self):
        """Test validation of empty messages list."""
        with pytest.raises(ValueError, match="Conversation must have at least one message"):
            NormalizedConversation(
                id="2024-01-01T12:00:00",
                source=SourceInfo(type="manual_text", path="test.txt"),
                title_hint="Test",
                messages=[]
            )


class TestSubstackDraftSchema:
    """Test SubstackDraft schema validation."""
    
    def test_valid_draft(self):
        """Test valid draft creation."""
        draft = SubstackDraft(
            title="Test Article",
            dek="A test article about something interesting",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test", "article", "example"],
            body_markdown="This is the body content with enough words to be valid."
        )
        assert draft.title == "Test Article"
        assert len(draft.tldr) == 3
        assert len(draft.tags) == 3
    
    def test_title_length_validation(self):
        """Test title length validation."""
        long_title = "A" * 81  # 81 characters
        
        with pytest.raises(ValueError, match="String should have at most 80 characters"):
            SubstackDraft(
                title=long_title,
                dek="Test dek",
                tldr=["Point 1", "Point 2", "Point 3"],
                tags=["test", "article", "example"],
                body_markdown="Test body"
            )
    
    def test_dek_length_validation(self):
        """Test dek length validation."""
        long_dek = "A" * 201  # 201 characters
        
        with pytest.raises(ValueError, match="String should have at most 200 characters"):
            SubstackDraft(
                title="Test Title",
                dek=long_dek,
                tldr=["Point 1", "Point 2", "Point 3"],
                tags=["test", "article", "example"],
                body_markdown="Test body"
            )
    
    def test_tldr_count_validation(self):
        """Test TL;DR count validation."""
        # Too few TL;DR points
        with pytest.raises(ValueError, match="List should have at least 3 items"):
            SubstackDraft(
                title="Test Title",
                dek="Test dek",
                tldr=["Point 1", "Point 2"],  # Only 2 points
                tags=["test", "article", "example"],
                body_markdown="Test body"
            )
        
        # Too many TL;DR points
        with pytest.raises(ValueError, match="List should have at most 5 items"):
            SubstackDraft(
                title="Test Title",
                dek="Test dek",
                tldr=["Point 1", "Point 2", "Point 3", "Point 4", "Point 5", "Point 6"],  # 6 points
                tags=["test", "article", "example"],
                body_markdown="Test body"
            )
    
    def test_tags_validation(self):
        """Test tags validation."""
        # Too few tags
        with pytest.raises(ValueError, match="List should have at least 3 items"):
            SubstackDraft(
                title="Test Title",
                dek="Test dek",
                tldr=["Point 1", "Point 2", "Point 3"],
                tags=["test"],  # Only 1 tag
                body_markdown="Test body"
            )
        
        # Too many tags
        with pytest.raises(ValueError, match="List should have at most 6 items"):
            SubstackDraft(
                title="Test Title",
                dek="Test dek",
                tldr=["Point 1", "Point 2", "Point 3"],
                tags=["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7"],  # 7 tags
                body_markdown="Test body"
            )
    
    def test_tags_lowercase_conversion(self):
        """Test that tags are converted to lowercase."""
        draft = SubstackDraft(
            title="Test Title",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["TAG1", "Tag2", "tag3"],
            body_markdown="Test body"
        )
        assert draft.tags == ["tag1", "tag2", "tag3"]
    
    def test_body_word_count_validation(self):
        """Test body word count validation."""
        # Create a body with more than 900 words
        long_body = "word " * 901  # 901 words
        
        with pytest.raises(ValueError, match="Body exceeds 900 word limit"):
            SubstackDraft(
                title="Test Title",
                dek="Test dek",
                tldr=["Point 1", "Point 2", "Point 3"],
                tags=["test"],
                body_markdown=long_body
            )
    
    def test_empty_tldr_validation(self):
        """Test empty TL;DR item validation."""
        with pytest.raises(ValueError, match="TL;DR items cannot be empty"):
            SubstackDraft(
                title="Test Title",
                dek="Test dek",
                tldr=["Point 1", "", "Point 3"],  # Empty item
                tags=["test"],
                body_markdown="Test body"
            )
    
    def test_further_reading_validation(self):
        """Test further reading validation."""
        further_reading = [
            FurtherReading(title="Test Article", url="https://example.com"),
            FurtherReading(title="Another Article", url="https://test.com")
        ]
        
        draft = SubstackDraft(
            title="Test Title",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test", "article", "example"],
            body_markdown="Test body",
            further_reading=further_reading
        )
        assert len(draft.further_reading) == 2
        assert draft.further_reading[0].title == "Test Article"
        assert draft.further_reading[0].url == "https://example.com"
    
    def test_invalid_further_reading_url(self):
        """Test invalid further reading URL validation."""
        with pytest.raises(ValueError, match="String should match pattern"):
            FurtherReading(title="Test", url="invalid-url")


class TestGuardrailResultSchema:
    """Test GuardrailResult schema validation."""
    
    def test_valid_guardrail_result(self):
        """Test valid guardrail result creation."""
        result = GuardrailResult(
            ok=True,
            issues=["Issue 1", "Issue 2"],
            patch="Fixed content"
        )
        assert result.ok is True
        assert len(result.issues) == 2
        assert result.patch == "Fixed content"
    
    def test_guardrail_result_without_patch(self):
        """Test guardrail result without patch."""
        result = GuardrailResult(ok=False, issues=["Issue 1"])
        assert result.ok is False
        assert result.patch is None


class TestRunReportSchema:
    """Test RunReport schema validation."""
    
    def test_valid_run_report(self):
        """Test valid run report creation."""
        report = RunReport(
            run_id="test-123",
            slug="test-article",
            content_hash="abc123",
            word_counts={"title": 2, "body": 100},
            redaction_stats={"emails": 1, "phones": 0},
            created_at=datetime.now()
        )
        assert report.run_id == "test-123"
        assert report.slug == "test-article"
        assert report.content_hash == "abc123"
        assert report.draft_url is None
        assert len(report.errors) == 0
    
    def test_run_report_with_draft_url(self):
        """Test run report with draft URL."""
        report = RunReport(
            run_id="test-123",
            slug="test-article",
            content_hash="abc123",
            word_counts={"title": 2, "body": 100},
            redaction_stats={"emails": 1},
            created_at=datetime.now(),
            draft_url="https://substack.com/draft/123"
        )
        assert report.draft_url == "https://substack.com/draft/123"
