"""Tests for PII redaction module."""

import pytest
from src.redact.scrub import PIIRedactor, redact_conversation
from src.util.schema import NormalizedConversation, SourceInfo, Message


class TestPIIRedaction:
    """Test PII redaction functionality."""
    
    def test_email_redaction(self):
        """Test email address redaction."""
        redactor = PIIRedactor()
        
        text = "Contact me at john@example.com or jane.doe@company.org"
        redacted = redactor.redact_email(text)
        
        assert "[email-redacted]" in redacted
        assert "john@example.com" not in redacted
        assert "jane.doe@company.org" not in redacted
        assert redactor.redaction_stats['emails'] == 2
    
    def test_phone_redaction(self):
        """Test phone number redaction."""
        redactor = PIIRedactor()
        
        text = "Call me at (555) 123-4567 or +1-555-987-6543"
        redacted = redactor.redact_phone(text)
        
        assert "[phone-redacted]" in redacted
        assert "(555) 123-4567" not in redacted
        assert "+1-555-987-6543" not in redacted
        assert redactor.redaction_stats['phones'] >= 2  # May match overlapping patterns
    
    def test_address_redaction(self):
        """Test address redaction."""
        redactor = PIIRedactor()
        
        text = "I live at 123 Main Street, New York, NY 10001"
        redacted = redactor.redact_address(text)
        
        assert "[address-redacted]" in redacted
        assert "123 Main Street" not in redacted
        assert "10001" not in redacted
        assert redactor.redaction_stats['addresses'] >= 2
    
    def test_id_redaction(self):
        """Test ID number redaction."""
        redactor = PIIRedactor()
        
        text = "My SSN is 123-45-6789 and credit card is 1234-5678-9012-3456"
        redacted = redactor.redact_ids(text)
        
        assert "[id-redacted]" in redacted
        assert "123-45-6789" not in redacted
        assert "1234-5678-9012-3456" not in redacted
        assert redactor.redaction_stats['ids'] == 2
    
    def test_private_name_redaction(self):
        """Test private name redaction."""
        private_names = ["John Smith", "Jane Doe"]
        redactor = PIIRedactor(private_names=private_names)
        
        text = "John Smith and Jane Doe discussed the project"
        redacted = redactor.redact_private_names(text)
        
        assert "J(pseudonym)" in redacted
        assert "John Smith" not in redacted
        assert "Jane Doe" not in redacted
        assert redactor.redaction_stats['private_names'] == 2
    
    def test_public_figure_preservation(self):
        """Test that public figures are preserved."""
        private_names = ["Elon Musk", "John Smith"]
        redactor = PIIRedactor(private_names=private_names, allow_public_figures=True)
        
        text = "Elon Musk and John Smith discussed AI"
        redacted = redactor.redact_private_names(text)
        
        assert "Elon Musk" in redacted  # Should be preserved
        assert "J(pseudonym)" in redacted  # John Smith should be redacted
        assert "John Smith" not in redacted
    
    def test_full_text_redaction(self):
        """Test redacting all PII types in one text."""
        redactor = PIIRedactor(private_names=["John Smith"])
        
        text = """
        Hi, I'm John Smith. You can reach me at john@example.com or (555) 123-4567.
        I live at 123 Main Street, New York, NY 10001.
        My SSN is 123-45-6789.
        """
        
        redacted = redactor.redact_text(text)
        
        assert "[email-redacted]" in redacted
        assert "[phone-redacted]" in redacted
        assert "[address-redacted]" in redacted
        assert "[id-redacted]" in redacted
        assert "J(pseudonym)" in redacted
        
        # Check stats
        assert redactor.redaction_stats['emails'] == 1
        assert redactor.redaction_stats['phones'] == 1
        assert redactor.redaction_stats['addresses'] >= 1
        assert redactor.redaction_stats['ids'] == 1
        assert redactor.redaction_stats['private_names'] == 1
    
    def test_conversation_redaction(self):
        """Test redacting entire conversation."""
        conversation = NormalizedConversation(
            id="test-123",
            source=SourceInfo(type="manual_text", path="test.txt"),
            title_hint="Test",
            messages=[
                Message(role="user", text="My email is john@example.com"),
                Message(role="assistant", text="I understand. Your phone is (555) 123-4567")
            ]
        )
        
        redacted, stats = redact_conversation(conversation)
        
        assert len(redacted.messages) == 2
        assert "[email-redacted]" in redacted.messages[0].text
        assert "[phone-redacted]" in redacted.messages[1].text
        assert stats['emails'] == 1
        assert stats['phones'] == 1
    
    def test_empty_private_names_list(self):
        """Test redaction with empty private names list."""
        redactor = PIIRedactor(private_names=[])
        
        text = "John Smith and Jane Doe discussed the project"
        redacted = redactor.redact_private_names(text)
        
        # Should not redact anything
        assert redacted == text
        assert redactor.redaction_stats['private_names'] == 0
    
    def test_case_insensitive_name_redaction(self):
        """Test that name redaction is case insensitive."""
        redactor = PIIRedactor(private_names=["John Smith"])
        
        text = "john smith and JOHN SMITH discussed the project"
        redacted = redactor.redact_private_names(text)
        
        assert "J(pseudonym)" in redacted
        assert "john smith" not in redacted.lower()
        assert "JOHN SMITH" not in redacted
        assert redactor.redaction_stats['private_names'] == 2
