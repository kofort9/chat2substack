"""Local PII redaction system."""

import re
from typing import Dict, List, Tuple
from ..util.schema import NormalizedConversation, Message


class PIIRedactor:
    """Redacts PII from conversation text."""
    
    def __init__(self, private_names: List[str] = None, allow_public_figures: bool = True):
        self.private_names = private_names or []
        self.allow_public_figures = allow_public_figures
        self.redaction_stats = {
            'emails': 0,
            'phones': 0,
            'addresses': 0,
            'ids': 0,
            'private_names': 0
        }
        
        # Public figures whitelist (common names that should be preserved)
        self.public_figures = {
            'elon musk', 'jeff bezos', 'bill gates', 'steve jobs', 'mark zuckerberg',
            'tim cook', 'sundar pichai', 'satya nadella', 'warren buffett',
            'oprah winfrey', 'taylor swift', 'beyonce', 'lebron james',
            'michael jordan', 'tom brady', 'serena williams', 'roger federer'
        }
    
    def redact_email(self, text: str) -> str:
        """Redact email addresses."""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)
        self.redaction_stats['emails'] += len(matches)
        return re.sub(pattern, '[email-redacted]', text)
    
    def redact_phone(self, text: str) -> str:
        """Redact phone numbers (US and international formats)."""
        # US phone numbers
        us_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        us_matches = re.findall(us_pattern, text)
        
        # International E.164 format
        intl_pattern = r'\+\d{1,3}[-.\s]?\d{1,14}'
        intl_matches = re.findall(intl_pattern, text)
        
        total_matches = len(us_matches) + len(intl_matches)
        self.redaction_stats['phones'] += total_matches
        
        text = re.sub(us_pattern, '[phone-redacted]', text)
        text = re.sub(intl_pattern, '[phone-redacted]', text)
        return text
    
    def redact_address(self, text: str) -> str:
        """Redact addresses and GPS coordinates."""
        # Street addresses
        address_pattern = r'\b\d+\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl|Court|Ct)\b'
        address_matches = re.findall(address_pattern, text, re.IGNORECASE)
        
        # GPS coordinates
        gps_pattern = r'\b-?\d+\.\d+,\s*-?\d+\.\d+\b'
        gps_matches = re.findall(gps_pattern, text)
        
        # ZIP codes
        zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
        zip_matches = re.findall(zip_pattern, text)
        
        total_matches = len(address_matches) + len(gps_matches) + len(zip_matches)
        self.redaction_stats['addresses'] += total_matches
        
        text = re.sub(address_pattern, '[address-redacted]', text, flags=re.IGNORECASE)
        text = re.sub(gps_pattern, '[address-redacted]', text)
        text = re.sub(zip_pattern, '[address-redacted]', text)
        return text
    
    def redact_ids(self, text: str) -> str:
        """Redact various ID numbers."""
        # Credit card numbers (basic pattern)
        cc_pattern = r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b'
        cc_matches = re.findall(cc_pattern, text)
        
        # SSN pattern
        ssn_pattern = r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b'
        ssn_matches = re.findall(ssn_pattern, text)
        
        # Long numeric IDs (12+ digits)
        long_id_pattern = r'\b\d{12,}\b'
        long_id_matches = re.findall(long_id_pattern, text)
        
        total_matches = len(cc_matches) + len(ssn_matches) + len(long_id_matches)
        self.redaction_stats['ids'] += total_matches
        
        text = re.sub(cc_pattern, '[id-redacted]', text)
        text = re.sub(ssn_pattern, '[id-redacted]', text)
        text = re.sub(long_id_pattern, '[id-redacted]', text)
        return text
    
    def redact_private_names(self, text: str) -> str:
        """Redact private names while preserving public figures."""
        if not self.private_names:
            return text
        
        for name in self.private_names:
            if not name.strip():
                continue
                
            # Check if it's a public figure
            if self.allow_public_figures and name.lower() in self.public_figures:
                continue
            
            # Create pattern for the name (case insensitive)
            pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
            matches = pattern.findall(text)
            
            if matches:
                self.redaction_stats['private_names'] += len(matches)
                # Replace with first initial + (pseudonym)
                first_initial = name[0].upper() if name else 'X'
                replacement = f"{first_initial}(pseudonym)"
                text = pattern.sub(replacement, text)
        
        return text
    
    def redact_text(self, text: str) -> str:
        """Apply all redaction rules to text."""
        text = self.redact_email(text)
        text = self.redact_phone(text)
        text = self.redact_address(text)
        text = self.redact_ids(text)
        text = self.redact_private_names(text)
        return text
    
    def redact_conversation(self, conversation: NormalizedConversation) -> NormalizedConversation:
        """Redact PII from entire conversation."""
        redacted_messages = []
        
        for message in conversation.messages:
            redacted_text = self.redact_text(message.text)
            redacted_messages.append(Message(
                role=message.role,
                text=redacted_text
            ))
        
        return NormalizedConversation(
            id=conversation.id,
            source=conversation.source,
            title_hint=conversation.title_hint,
            messages=redacted_messages
        )


def redact_conversation(conversation: NormalizedConversation, 
                       private_names: List[str] = None,
                       allow_public_figures: bool = True) -> Tuple[NormalizedConversation, Dict[str, int]]:
    """Redact PII from conversation and return stats."""
    redactor = PIIRedactor(private_names, allow_public_figures)
    redacted = redactor.redact_conversation(conversation)
    return redacted, redactor.redaction_stats
