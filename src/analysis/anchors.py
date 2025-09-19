"""Canonical anchor extraction for all content types."""

import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Anchor:
    """A canonical anchor extracted from conversation."""
    msg_id: int
    type: str  # decision, command, citation, error, model, ship_action, research_noun, opinion
    text: str
    tags: List[str]
    context: str = ""

class AnchorExtractor:
    """Extracts canonical anchors from conversation messages."""
    
    def __init__(self):
        # Regex patterns for different anchor types
        self.patterns = {
            'decision': [
                r'\b(decided|chose|selected|picked|went with|using|we\'ll use|we used)\b',
                r'\b(shipped|rollback|bypass|revert|implemented|deployed)\b',
                r'\b(architecture|approach|strategy|method|solution)\b'
            ],
            'command': [
                r'(?m)^(?:\$|\s{0,3}(?:curl|bash|sh|ollama|litellm|pytest|git|python3?|docker|brew)\b).*',
                r'```(?:bash|sh|zsh|shell)?\n[\s\S]*?```',
                r'\b(install|run|execute|pull|push|build|test)\b.*'
            ],
            'citation': [
                r'\(msg\s+\d+\)',
                r'\b(paper|study|research|article|book|author|citation|reference)\b',
                r'\b(reading list|literature|academic|scholarly)\b'
            ],
            'error': [
                r'\b(error|failed|exception|timeout|crash|bug|issue|problem)\b',
                r'\b(debug|fix|resolve|troubleshoot|investigate)\b'
            ],
            'model': [
                r'\b(ollama|litellm|llama|gpt|claude|model|ai|llm)\b',
                r'\b(q[45]_K_M|quantized|fine-tuned|trained)\b'
            ],
            'ship_action': [
                r'\b(shipped|deployed|released|launched|published|live|production)\b',
                r'\b(rollback|revert|undo|backout|released)\b'
            ],
            'research_noun': [
                r'\b(dataset|benchmark|paper|citation|RAG|graphRAG|Ray|Anyscale|architecture|method|methodology|experiment|reading\s+list|evaluation|ablation|baseline|fine-?tuning)\b'
            ],
            'opinion': [
                r'\b(thesis|claim|counterpoint|counter-?argument|stance|agree|disagree|critique|opinion|believe|think|argue|contend)\b',
                r'\b(however|but|on the other hand|critics might|steelman)\b'
            ]
        }
        
        # Banned filler phrases
        self.banned_phrases = [
            "Key technical component in the research discussion",
            "An analysis of X exploring what are the key insights",
            "The methodology employed ensures comprehensive coverage",
            "cross-cultural and longitudinal studies",
            "Key technical component in the discussion",
            "comprehensive discussion and analysis",
            "This research analysis examines",
            "Academic research methodology or concept",
            "Societal or policy aspect of the research",
            "through comprehensive discussion and analysis",
            "ensures comprehensive coverage of key concepts",
            "reveals important insights about the topic and its implications"
        ]
    
    def extract_anchors(self, messages: List[Dict[str, Any]]) -> List[Anchor]:
        """Extract all anchors from conversation messages."""
        anchors = []
        
        for i, msg in enumerate(messages):
            content = msg.get('content', '')
            role = msg.get('role', '')
            
            # Extract anchors by type
            for anchor_type, patterns in self.patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Get context around the match
                        start = max(0, match.start() - 50)
                        end = min(len(content), match.end() + 50)
                        context = content[start:end].strip()
                        
                        # Create tags based on content
                        tags = self._extract_tags(content, anchor_type)
                        
                        anchor = Anchor(
                            msg_id=i,
                            type=anchor_type,
                            text=match.group(0),
                            tags=tags,
                            context=context
                        )
                        anchors.append(anchor)
        
        return anchors
    
    def _extract_tags(self, content: str, anchor_type: str) -> List[str]:
        """Extract relevant tags for an anchor."""
        tags = []
        
        if anchor_type == 'command':
            if 'ollama' in content.lower():
                tags.append('ollama')
            if 'litellm' in content.lower():
                tags.append('litellm')
            if 'curl' in content.lower():
                tags.append('api')
            if 'docker' in content.lower():
                tags.append('container')
            if 'pytest' in content.lower():
                tags.append('testing')
        
        elif anchor_type == 'model':
            if 'q4_K_M' in content or 'q5_K_M' in content:
                tags.append('quantized')
            if 'ollama' in content.lower():
                tags.append('local')
            if 'litellm' in content.lower():
                tags.append('proxy')
        
        elif anchor_type == 'research_noun':
            if 'ray' in content.lower():
                tags.append('distributed')
            if 'rag' in content.lower():
                tags.append('retrieval')
            if 'dataset' in content.lower():
                tags.append('data')
            if 'benchmark' in content.lower():
                tags.append('evaluation')
        
        return tags
    
    def has_commands(self, anchors: List[Anchor]) -> int:
        """Count runnable commands in anchors."""
        return len([a for a in anchors if a.type == 'command'])
    
    def has_decision_verbs(self, anchors: List[Anchor]) -> bool:
        """Check if anchors contain decision-making verbs."""
        decision_anchors = [a for a in anchors if a.type == 'decision']
        return len(decision_anchors) > 0
    
    def mentions(self, anchors: List[Anchor], term: str) -> bool:
        """Check if any anchor mentions a specific term."""
        return any(term.lower() in a.text.lower() for a in anchors)
    
    def count_regex(self, anchors: List[Anchor], pattern: str) -> int:
        """Count anchors matching a regex pattern."""
        count = 0
        for anchor in anchors:
            if re.search(pattern, anchor.text, re.IGNORECASE):
                count += 1
        return count
    
    def has_citations_or_reading_list(self, anchors: List[Anchor]) -> bool:
        """Check if anchors contain citations or reading list references."""
        citation_anchors = [a for a in anchors if a.type == 'citation']
        return len(citation_anchors) > 0
    
    def has_opinion_markers(self, anchors: List[Anchor]) -> bool:
        """Check if anchors contain opinion markers."""
        opinion_anchors = [a for a in anchors if a.type == 'opinion']
        return len(opinion_anchors) > 0
    
    def get_anchor_coverage(self, anchors: List[Anchor], output_text: str) -> Dict[str, Any]:
        """Calculate anchor coverage in output text."""
        # Find all (msg N) citations in output
        citation_pattern = r'\(msg\s+(\d+)\)'
        cited_msg_ids = set()
        for match in re.finditer(citation_pattern, output_text):
            cited_msg_ids.add(int(match.group(1)))
        
        # Count anchors that are referenced
        referenced_anchors = [a for a in anchors if a.msg_id in cited_msg_ids]
        
        total_anchors = len(anchors)
        referenced_count = len(referenced_anchors)
        coverage_pct = (referenced_count / total_anchors * 100) if total_anchors > 0 else 0
        
        return {
            'anchors_total': total_anchors,
            'anchors_referenced': referenced_count,
            'anchor_coverage_pct': coverage_pct,
            'referenced_msg_ids': list(cited_msg_ids)
        }
    
    def detect_banned_phrases(self, text: str) -> List[str]:
        """Detect banned filler phrases in text."""
        found_phrases = []
        text_lower = text.lower()
        
        for phrase in self.banned_phrases:
            if phrase.lower() in text_lower:
                found_phrases.append(phrase)
        
        return found_phrases
