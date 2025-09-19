"""Ingest manual text input."""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from ..util.schema import NormalizedConversation, SourceInfo, Message


def parse_text_conversation(text: str) -> List[Tuple[str, str]]:
    """Parse text into (role, text) pairs."""
    messages = []
    
    # Try to split by common delimiters
    delimiters = [
        r'^User:\s*',
        r'^Assistant:\s*',
        r'^Human:\s*',
        r'^AI:\s*',
        r'^ChatGPT:\s*',
        r'^Q:\s*',
        r'^A:\s*'
    ]
    
    # Find all delimiter matches
    pattern = '|'.join(f'({d})' for d in delimiters)
    parts = re.split(pattern, text, flags=re.MULTILINE)
    
    current_role = None
    current_text = []
    
    for part in parts:
        if not part:
            continue
            
        # Check if this part is a role delimiter
        role_match = None
        for i, delimiter in enumerate(delimiters):
            if re.match(delimiter, part, re.IGNORECASE):
                role_match = i
                break
        
        if role_match is not None:
            # Save previous message if exists
            if current_role and current_text:
                messages.append((current_role, '\n'.join(current_text).strip()))
            
            # Start new message
            if role_match < 2:  # User delimiters
                current_role = 'user'
            else:  # Assistant delimiters
                current_role = 'assistant'
            current_text = []
        else:
            # This is text content
            if current_role:
                current_text.append(part.strip())
            else:
                # No role specified yet, treat as user message
                if not current_role:
                    current_role = 'user'
                current_text.append(part.strip())
    
    # Add final message
    if current_role and current_text:
        messages.append((current_role, '\n'.join(current_text).strip()))
    
    # If no delimiters found, treat entire text as user message
    if not messages:
        messages.append(('user', text.strip()))
    
    return messages


def ingest_manual_text(file_path: str, max_chars: int = 10000) -> NormalizedConversation:
    """Ingest a manual text file."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    if len(text_content) > max_chars:
        raise ValueError(f"Text file exceeds {max_chars} character limit: {len(text_content)} chars")
    
    messages_data = parse_text_conversation(text_content)
    
    if not messages_data:
        raise ValueError("No content found in text file")
    
    # Convert to Message objects
    messages = [
        Message(role=role, text=text) 
        for role, text in messages_data
    ]
    
    # Generate conversation ID
    conversation_id = datetime.now().isoformat()
    
    return NormalizedConversation(
        id=conversation_id,
        source=SourceInfo(
            type="manual_text",
            path=str(path.absolute()),
            url=None
        ),
        title_hint="",
        messages=messages
    )
