"""Content hashing utilities for idempotency."""

import hashlib
import json
from typing import Any, Dict


def content_hash(data: Any) -> str:
    """Generate a stable hash for content to enable idempotency."""
    if isinstance(data, dict):
        # Sort keys for consistent hashing
        data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
    else:
        data_str = str(data)
    
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()[:16]


def conversation_hash(conversation: Dict[str, Any]) -> str:
    """Generate hash for a normalized conversation."""
    # Hash the messages content only (ignore metadata like timestamps)
    messages_data = {
        'messages': conversation.get('messages', []),
        'title_hint': conversation.get('title_hint', '')
    }
    return content_hash(messages_data)


def slug_from_title(title: str) -> str:
    """Generate URL-safe slug from title."""
    import re
    
    # Convert to lowercase and replace spaces with hyphens
    slug = title.lower()
    # Remove special characters except hyphens
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Replace multiple spaces/hyphens with single hyphen
    slug = re.sub(r'[\s-]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Limit length
    if len(slug) > 50:
        slug = slug[:50].rstrip('-')
    
    return slug or 'untitled'
