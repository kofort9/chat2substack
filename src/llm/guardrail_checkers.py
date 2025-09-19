"""Guardrail checkers for content safety and tone."""

import re
from typing import List, Dict, Any
from ..util.schema import SubstackDraft, GuardrailResult


class ContentGuard:
    """Content safety and legal compliance checker."""
    
    def __init__(self, blocked_phrases: List[str] = None):
        self.blocked_phrases = blocked_phrases or []
        
        # PII patterns that might have been missed
        self.pii_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # emails
            r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',  # phones
            r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b',  # SSN
            r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b',  # credit cards
        ]
        
        # Career-sensitive content patterns
        self.career_sensitive = [
            r'\b(?:fired|terminated|laid off|let go)\b',
            r'\b(?:fraud|scam|illegal|unethical)\b',
            r'\b(?:lawsuit|sue|legal action)\b',
            r'\b(?:harassment|discrimination)\b',
            r'\b(?:bankruptcy|insolvent|default)\b'
        ]
    
    def check_pii_leakage(self, text: str) -> List[str]:
        """Check for remaining PII after redaction."""
        issues = []
        
        for pattern in self.pii_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues.append(f"PII detected: {len(matches)} matches of pattern {pattern}")
        
        return issues
    
    def check_blocked_phrases(self, text: str) -> List[str]:
        """Check for blocked phrases."""
        issues = []
        text_lower = text.lower()
        
        for phrase in self.blocked_phrases:
            if phrase.lower() in text_lower:
                issues.append(f"Blocked phrase detected: '{phrase}'")
        
        return issues
    
    def check_career_sensitive_content(self, text: str) -> List[str]:
        """Check for career-sensitive content."""
        issues = []
        
        for pattern in self.career_sensitive:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues.append(f"Career-sensitive content: {len(matches)} matches of '{pattern}'")
        
        return issues
    
    def check_unverified_claims(self, text: str) -> List[str]:
        """Check for unverified claims presented as facts."""
        issues = []
        
        # Look for definitive statements without qualifiers
        definitive_patterns = [
            r'\b(?:definitely|certainly|absolutely|without doubt)\b',
            r'\b(?:proven|established|confirmed)\b',
            r'\b(?:always|never|all|none)\b'
        ]
        
        for pattern in definitive_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues.append(f"Potentially unverified claim: {len(matches)} matches of '{pattern}'")
        
        return issues
    
    def check_content(self, draft: SubstackDraft) -> GuardrailResult:
        """Run all content checks."""
        issues = []
        
        # Check all text fields
        text_fields = [
            draft.title,
            draft.dek,
            ' '.join(draft.tldr),
            draft.body_markdown
        ]
        
        full_text = ' '.join(text_fields)
        
        # Run all checks
        issues.extend(self.check_pii_leakage(full_text))
        issues.extend(self.check_blocked_phrases(full_text))
        issues.extend(self.check_career_sensitive_content(full_text))
        issues.extend(self.check_unverified_claims(full_text))
        
        # Generate patch if issues found
        patch = None
        if issues:
            patch = self._generate_patch(full_text, issues)
        
        return GuardrailResult(
            ok=len(issues) == 0,
            issues=issues,
            patch=patch
        )
    
    def _generate_patch(self, text: str, issues: List[str]) -> str:
        """Generate a patch to fix content issues."""
        patched_text = text
        
        # Remove PII
        for pattern in self.pii_patterns:
            patched_text = re.sub(pattern, '[redacted]', patched_text, flags=re.IGNORECASE)
        
        # Remove blocked phrases
        for phrase in self.blocked_phrases:
            patched_text = patched_text.replace(phrase, '[removed]')
        
        # Soften definitive language
        replacements = {
            r'\bdefinitely\b': 'likely',
            r'\bcertainly\b': 'probably',
            r'\babsolutely\b': 'generally',
            r'\bwithout doubt\b': 'in most cases',
            r'\bproven\b': 'suggested',
            r'\bestablished\b': 'indicated',
            r'\bconfirmed\b': 'suggested'
        }
        
        for pattern, replacement in replacements.items():
            patched_text = re.sub(pattern, replacement, patched_text, flags=re.IGNORECASE)
        
        return patched_text


class ToneGuard:
    """Tone and length compliance checker."""
    
    def __init__(self, target_words: int = 450, hard_cap_words: int = 900):
        self.target_words = target_words
        self.hard_cap_words = hard_cap_words
        
        # Inappropriate tone patterns
        self.casual_patterns = [
            r'\b(?:lol|lmao|omg|wtf|fyi|btw)\b',
            r'\b(?:awesome|cool|amazing|incredible|fantastic)\b',
            r'\b(?:totally|definitely|absolutely|completely)\b',
            r'\b(?:you guys|y\'all|folks)\b'
        ]
        
        self.marketing_patterns = [
            r'\b(?:revolutionary|game-changing|breakthrough|cutting-edge)\b',
            r'\b(?:must-have|essential|critical|vital)\b',
            r'\b(?:unlock|leverage|optimize|maximize)\b',
            r'\b(?:transform|disrupt|innovate|pioneer)\b'
        ]
    
    def check_length(self, draft: SubstackDraft) -> List[str]:
        """Check word count compliance."""
        issues = []
        
        # Count words in body
        body_words = len(draft.body_markdown.split())
        
        if body_words < 300:
            issues.append(f"Content too short: {body_words} words (minimum 300)")
        elif body_words > self.hard_cap_words:
            issues.append(f"Content exceeds hard cap: {body_words} words (max {self.hard_cap_words})")
        elif body_words < self.target_words:
            issues.append(f"Content below target: {body_words} words (target {self.target_words})")
        
        return issues
    
    def check_tone_patterns(self, text: str) -> List[str]:
        """Check for inappropriate tone."""
        issues = []
        
        # Check for casual language
        for pattern in self.casual_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues.append(f"Casual language detected: {len(matches)} matches of '{pattern}'")
        
        # Check for marketing speak
        for pattern in self.marketing_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues.append(f"Marketing language detected: {len(matches)} matches of '{pattern}'")
        
        return issues
    
    def check_structure(self, draft: SubstackDraft) -> List[str]:
        """Check content structure."""
        issues = []
        
        # Check for required sections
        body_lower = draft.body_markdown.lower()
        
        if '##' not in body_lower:
            issues.append("Missing section headers")
        
        if 'takeaway' not in body_lower and 'conclusion' not in body_lower:
            issues.append("Missing takeaways or conclusion section")
        
        # Check TL;DR format
        if len(draft.tldr) < 3:
            issues.append("TL;DR has fewer than 3 points")
        elif len(draft.tldr) > 5:
            issues.append("TL;DR has more than 5 points")
        
        # Check tags
        if len(draft.tags) < 3:
            issues.append("Too few tags (minimum 3)")
        elif len(draft.tags) > 6:
            issues.append("Too many tags (maximum 6)")
        
        # Check for uppercase tags
        for tag in draft.tags:
            if tag != tag.lower():
                issues.append(f"Tag not lowercase: '{tag}'")
        
        return issues
    
    def check_tone_guard(self, draft: SubstackDraft) -> GuardrailResult:
        """Run all tone checks."""
        issues = []
        
        # Check length
        issues.extend(self.check_length(draft))
        
        # Check tone in all text
        text_fields = [
            draft.title,
            draft.dek,
            ' '.join(draft.tldr),
            draft.body_markdown
        ]
        
        full_text = ' '.join(text_fields)
        issues.extend(self.check_tone_patterns(full_text))
        
        # Check structure
        issues.extend(self.check_structure(draft))
        
        # Generate patch if issues found
        patch = None
        if issues:
            patch = self._generate_patch(draft)
        
        return GuardrailResult(
            ok=len(issues) == 0,
            issues=issues,
            patch=patch
        )
    
    def _generate_patch(self, draft: SubstackDraft) -> str:
        """Generate a patch to fix tone issues."""
        # This would be more complex in practice
        # For now, return a simple indication that patching is needed
        return "Tone adjustments needed - manual review recommended"


def content_guard(draft: SubstackDraft, blocked_phrases: List[str] = None) -> GuardrailResult:
    """Run content safety guardrails."""
    guard = ContentGuard(blocked_phrases)
    return guard.check_content(draft)


def tone_guard(draft: SubstackDraft, target_words: int = 450, hard_cap_words: int = 900) -> GuardrailResult:
    """Run tone and length guardrails."""
    guard = ToneGuard(target_words, hard_cap_words)
    return guard.check_tone_guard(draft)
