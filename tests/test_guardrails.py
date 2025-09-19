"""Tests for guardrail checkers."""

import pytest
from src.llm.guardrail_checkers import ContentGuard, ToneGuard, content_guard, tone_guard
from src.util.schema import SubstackDraft


class TestContentGuard:
    """Test content safety guardrails."""
    
    def test_pii_leakage_detection(self):
        """Test PII leakage detection."""
        guard = ContentGuard()
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="Contact me at john@example.com or call (555) 123-4567"
        )
        
        result = guard.check_content(draft)
        assert not result.ok
        assert len(result.issues) > 0
        assert any("PII detected" in issue for issue in result.issues)
    
    def test_blocked_phrases_detection(self):
        """Test blocked phrases detection."""
        blocked_phrases = ["spam", "scam", "fraud"]
        guard = ContentGuard(blocked_phrases=blocked_phrases)
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="This is a spam message about fraud"
        )
        
        result = guard.check_content(draft)
        assert not result.ok
        assert any("Blocked phrase detected" in issue for issue in result.issues)
    
    def test_career_sensitive_content_detection(self):
        """Test career-sensitive content detection."""
        guard = ContentGuard()
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="The company is definitely committing fraud"
        )
        
        result = guard.check_content(draft)
        assert not result.ok
        assert any("Career-sensitive content" in issue for issue in result.issues)
    
    def test_unverified_claims_detection(self):
        """Test unverified claims detection."""
        guard = ContentGuard()
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="This is definitely proven to be true"
        )
        
        result = guard.check_content(draft)
        assert not result.ok
        assert any("Potentially unverified claim" in issue for issue in result.issues)
    
    def test_clean_content_passes(self):
        """Test that clean content passes guardrails."""
        guard = ContentGuard()
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="This is a clean article about technology trends"
        )
        
        result = guard.check_content(draft)
        assert result.ok
        assert len(result.issues) == 0
    
    def test_patch_generation(self):
        """Test patch generation for content issues."""
        guard = ContentGuard()
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="Contact me at john@example.com"
        )
        
        result = guard.check_content(draft)
        assert not result.ok
        assert result.patch is not None
        assert "[redacted]" in result.patch


class TestToneGuard:
    """Test tone and length guardrails."""
    
    def test_length_validation_short_content(self):
        """Test validation of content that's too short."""
        guard = ToneGuard(target_words=300, hard_cap_words=900)
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="Short content"  # Very short
        )
        
        result = guard.check_tone(draft)
        assert not result.ok
        assert any("Content too short" in issue for issue in result.issues)
    
    def test_length_validation_long_content(self):
        """Test validation of content that's too long."""
        guard = ToneGuard(target_words=300, hard_cap_words=900)
        
        # Create content with more than 900 words
        long_content = "word " * 901
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown=long_content
        )
        
        result = guard.check_tone(draft)
        assert not result.ok
        assert any("Content exceeds hard cap" in issue for issue in result.issues)
    
    def test_casual_language_detection(self):
        """Test detection of casual language."""
        guard = ToneGuard()
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="This is awesome and totally cool! You guys will love it."
        )
        
        result = guard.check_tone(draft)
        assert not result.ok
        assert any("Casual language detected" in issue for issue in result.issues)
    
    def test_marketing_language_detection(self):
        """Test detection of marketing language."""
        guard = ToneGuard()
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="This revolutionary breakthrough will transform your business"
        )
        
        result = guard.check_tone(draft)
        assert not result.ok
        assert any("Marketing language detected" in issue for issue in result.issues)
    
    def test_structure_validation_missing_sections(self):
        """Test validation of missing sections."""
        guard = ToneGuard()
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="Just some content without proper sections"
        )
        
        result = guard.check_tone(draft)
        assert not result.ok
        assert any("Missing section headers" in issue for issue in result.issues)
    
    def test_tldr_count_validation(self):
        """Test TL;DR count validation."""
        guard = ToneGuard()
        
        # Too few TL;DR points
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2"],  # Only 2 points
            tags=["test"],
            body_markdown="This is a test article with enough content to be valid."
        )
        
        result = guard.check_tone(draft)
        assert not result.ok
        assert any("TL;DR has fewer than 3 points" in issue for issue in result.issues)
    
    def test_tags_validation(self):
        """Test tags validation."""
        guard = ToneGuard()
        
        # Too few tags
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],  # Only 1 tag
            body_markdown="This is a test article with enough content to be valid."
        )
        
        result = guard.check_tone(draft)
        assert not result.ok
        assert any("Too few tags" in issue for issue in result.issues)
    
    def test_uppercase_tags_detection(self):
        """Test detection of uppercase tags."""
        guard = ToneGuard()
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["Test", "Article", "Example"],  # Uppercase tags
            body_markdown="This is a test article with enough content to be valid."
        )
        
        result = guard.check_tone(draft)
        assert not result.ok
        assert any("Tag not lowercase" in issue for issue in result.issues)
    
    def test_valid_content_passes(self):
        """Test that valid content passes tone guardrails."""
        guard = ToneGuard()
        
        # Create content with appropriate length
        body_content = "This is a well-structured article about technology trends. " * 50  # ~300 words
        
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test", "article", "example"],
            body_markdown=f"## Introduction\n\n{body_content}\n\n## Takeaways\n\n- Key insight 1\n- Key insight 2"
        )
        
        result = guard.check_tone(draft)
        assert result.ok
        assert len(result.issues) == 0


class TestGuardrailFunctions:
    """Test guardrail function interfaces."""
    
    def test_content_guard_function(self):
        """Test content_guard function interface."""
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="Contact me at john@example.com"
        )
        
        result = content_guard(draft, blocked_phrases=["spam"])
        assert not result.ok
        assert len(result.issues) > 0
    
    def test_tone_guard_function(self):
        """Test tone_guard function interface."""
        draft = SubstackDraft(
            title="Test Article",
            dek="Test dek",
            tldr=["Point 1", "Point 2", "Point 3"],
            tags=["test"],
            body_markdown="Short content"
        )
        
        result = tone_guard(draft, target_words=300, hard_cap_words=900)
        assert not result.ok
        assert any("Content too short" in issue for issue in result.issues)
