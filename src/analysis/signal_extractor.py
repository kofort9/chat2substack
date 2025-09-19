"""Heuristic signal extraction for better content analysis."""

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import Counter


@dataclass
class ContentSignal:
    """A detected content signal."""
    signal_type: str
    content: str
    confidence: float
    context: str
    position: int


class SignalExtractor:
    """Extract meaningful signals from conversation content."""
    
    def __init__(self):
        # Problem/solution patterns
        self.problem_patterns = [
            r'(?:problem|issue|challenge|difficulty|trouble|error|bug|obstacle|stuck|confused|unsure|help)\s+(?:is|with|that|about)\s+([^.!?]+)',
            r'(?:i need|i want|i\'m looking for|i\'m trying to|i can\'t|i don\'t know)\s+([^.!?]+)',
            r'(?:how do|how can|how to|what is|what are|why is|why does)\s+([^.!?]+)',
            r'(?:stuck|blocked|failing|not working|broken|incorrect)\s+(?:on|with|because)\s+([^.!?]+)'
        ]
        
        self.solution_patterns = [
            r'(?:solution|answer|fix|resolve|solve|approach|method|technique|strategy|recommend|suggest)\s+(?:is|was|for|to)\s+([^.!?]+)',
            r'(?:try|use|implement|apply|do|run|execute|install|configure)\s+([^.!?]+)',
            r'(?:you can|we can|i can|it should|this will|that will)\s+([^.!?]+)',
            r'(?:here\'s|this is|the way|the solution|the fix)\s+([^.!?]+)'
        ]
        
        # Decision patterns
        self.decision_patterns = [
            r'(?:decided|chose|selected|picked|went with|opted for)\s+([^.!?]+)',
            r'(?:we\'ll|i\'ll|let\'s)\s+(?:use|go with|choose|pick|select)\s+([^.!?]+)',
            r'(?:best|better|preferred|recommended)\s+(?:option|choice|approach|method)\s+(?:is|was)\s+([^.!?]+)',
            r'(?:instead of|rather than|over)\s+([^.!?]+?)\s+(?:we\'ll|i\'ll|let\'s)\s+([^.!?]+)'
        ]
        
        # Insight patterns
        self.insight_patterns = [
            r'(?:key insight|important|crucial|essential|significant|notable|interesting|learned|discovered)\s+([^.!?]+)',
            r'(?:the main|key|important|primary)\s+(?:point|thing|takeaway|lesson)\s+(?:is|was)\s+([^.!?]+)',
            r'(?:this shows|this means|this indicates|this suggests)\s+([^.!?]+)',
            r'(?:i realized|i learned|i discovered|i found)\s+([^.!?]+)'
        ]
        
        # Action patterns
        self.action_patterns = [
            r'(?:next step|next|then|after that|following|subsequent)\s+(?:is|will be|should be)\s+([^.!?]+)',
            r'(?:todo|task|action item|need to|should|must)\s+([^.!?]+)',
            r'(?:implement|build|create|develop|design|setup|configure)\s+([^.!?]+)',
            r'(?:test|verify|check|validate|confirm)\s+([^.!?]+)'
        ]
        
        # Technical patterns
        self.technical_patterns = [
            r'(?:using|implementing|applying|based on|built on)\s+([^.!?]+?)\s+(?:framework|library|tool|technology|approach)',
            r'(?:install|setup|configure|run|execute)\s+([^.!?]+)',
            r'(?:command|script|code|function|method|class)\s+(?:is|was|for)\s+([^.!?]+)',
            r'(?:api|endpoint|service|database|server|client)\s+(?:is|was|for)\s+([^.!?]+)'
        ]
    
    def extract_all_signals(self, text: str) -> List[ContentSignal]:
        """Extract all types of content signals from text."""
        signals = []
        
        # Extract different types of signals
        signals.extend(self._extract_signals(text, self.problem_patterns, "problem", 0.8))
        signals.extend(self._extract_signals(text, self.solution_patterns, "solution", 0.8))
        signals.extend(self._extract_signals(text, self.decision_patterns, "decision", 0.7))
        signals.extend(self._extract_signals(text, self.insight_patterns, "insight", 0.9))
        signals.extend(self._extract_signals(text, self.action_patterns, "action", 0.7))
        signals.extend(self._extract_signals(text, self.technical_patterns, "technical", 0.8))
        
        # Sort by confidence and position
        signals.sort(key=lambda x: (x.confidence, -x.position), reverse=True)
        
        return signals
    
    def _extract_signals(self, text: str, patterns: List[str], signal_type: str, base_confidence: float) -> List[ContentSignal]:
        """Extract signals of a specific type."""
        signals = []
        sentences = re.split(r'[.!?]+', text)
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            for pattern in patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        # Handle multiple capture groups
                        content = ' '.join(m for m in match if m.strip())
                    else:
                        content = match.strip()
                    
                    if len(content) > 5 and len(content) < 200:
                        # Calculate confidence based on pattern specificity and content quality
                        confidence = self._calculate_confidence(content, signal_type, base_confidence)
                        
                        signals.append(ContentSignal(
                            signal_type=signal_type,
                            content=content,
                            confidence=confidence,
                            context=sentence[:100] + "..." if len(sentence) > 100 else sentence,
                            position=i
                        ))
        
        return signals
    
    def _calculate_confidence(self, content: str, signal_type: str, base_confidence: float) -> float:
        """Calculate confidence score for a signal."""
        confidence = base_confidence
        
        # Adjust based on content length (sweet spot around 20-50 chars)
        content_len = len(content)
        if 20 <= content_len <= 50:
            confidence += 0.1
        elif content_len < 10 or content_len > 100:
            confidence -= 0.2
        
        # Adjust based on signal type specific indicators
        if signal_type == "problem":
            if any(word in content.lower() for word in ['error', 'bug', 'issue', 'problem', 'stuck']):
                confidence += 0.1
        elif signal_type == "solution":
            if any(word in content.lower() for word in ['fix', 'solve', 'resolve', 'work', 'correct']):
                confidence += 0.1
        elif signal_type == "technical":
            if any(word in content.lower() for word in ['api', 'code', 'function', 'command', 'install']):
                confidence += 0.1
        
        # Cap confidence between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def extract_high_confidence_signals(self, text: str, min_confidence: float = 0.7) -> List[ContentSignal]:
        """Extract only high-confidence signals."""
        all_signals = self.extract_all_signals(text)
        return [s for s in all_signals if s.confidence >= min_confidence]
    
    def group_signals_by_type(self, signals: List[ContentSignal]) -> Dict[str, List[ContentSignal]]:
        """Group signals by their type."""
        grouped = {}
        for signal in signals:
            if signal.signal_type not in grouped:
                grouped[signal.signal_type] = []
            grouped[signal.signal_type].append(signal)
        return grouped
    
    def get_signal_summary(self, signals: List[ContentSignal]) -> Dict[str, Any]:
        """Get a summary of extracted signals."""
        if not signals:
            return {
                "total_signals": 0,
                "signal_types": {},
                "high_confidence_count": 0,
                "average_confidence": 0.0
            }
        
        grouped = self.group_signals_by_type(signals)
        high_confidence = [s for s in signals if s.confidence >= 0.7]
        
        return {
            "total_signals": len(signals),
            "signal_types": {signal_type: len(sigs) for signal_type, sigs in grouped.items()},
            "high_confidence_count": len(high_confidence),
            "average_confidence": sum(s.confidence for s in signals) / len(signals),
            "top_signals": [
                {
                    "type": s.signal_type,
                    "content": s.content[:100] + "..." if len(s.content) > 100 else s.content,
                    "confidence": s.confidence
                }
                for s in sorted(signals, key=lambda x: x.confidence, reverse=True)[:10]
            ]
        }


def extract_content_signals(text: str) -> List[ContentSignal]:
    """Public interface for signal extraction."""
    extractor = SignalExtractor()
    return extractor.extract_all_signals(text)


def extract_high_confidence_signals(text: str, min_confidence: float = 0.7) -> List[ContentSignal]:
    """Public interface for high-confidence signal extraction."""
    extractor = SignalExtractor()
    return extractor.extract_high_confidence_signals(text, min_confidence)
