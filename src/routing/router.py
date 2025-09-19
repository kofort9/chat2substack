"""Deterministic router with abstain logic."""

from typing import Optional, List, Dict, Any
from ..analysis.anchors import Anchor, AnchorExtractor

class DeterministicRouter:
    """Deterministic content type router based on anchor analysis."""
    
    def __init__(self):
        self.anchor_extractor = AnchorExtractor()
        
        # Research domain terms pattern
        self.research_terms_pattern = r'\b(dataset|benchmark|paper|citation|RAG|graphRAG|Ray|Anyscale|architecture|method|methodology|experiment|reading\s+list|evaluation|ablation|baseline|fine-?tuning)\b'
        
        # Critique tokens pattern
        self.critique_tokens_pattern = r'\b(thesis|claim|counterpoint|counter-?argument|stance|agree|disagree|critique|opinion|believe|think|argue|contend)\b'
    
    def route_content(self, content: str, anchors: List[Anchor]) -> str:
        """Route content to appropriate type or BLOCKED."""
        
        # Check for technical journal indicators
        if self._is_technical_journal(anchors, content):
            return "technical_journal"
        
        # Check for research article indicators
        if self._is_research_article(anchors, content):
            return "research_article"
        
        # Check for critique indicators
        if self._is_critique(anchors, content):
            return "critique"
        
        # If no clear indicators, check for tie-breaker scenarios
        tie_result = self._handle_ties(anchors, content)
        if tie_result:
            return tie_result
        
        # Default to BLOCKED if unclear
        return "BLOCKED: Unclear genre (insufficient signals)"
    
    def _is_technical_journal(self, anchors: List[Anchor], content: str) -> bool:
        """Check if content is a technical journal."""
        # Check for commands
        has_commands = self.anchor_extractor.has_commands(anchors) >= 1
        
        # Check for decision verbs
        has_decisions = self.anchor_extractor.has_decision_verbs(anchors)
        
        # Check for technical tools
        has_ollama = self.anchor_extractor.mentions(anchors, "ollama")
        has_litellm = self.anchor_extractor.mentions(anchors, "litellm")
        has_technical_tools = has_ollama or has_litellm
        
        # Check for system building keywords
        system_keywords = [
            "summarizer", "pipeline", "system", "build", "develop", "create", "implement",
            "failure modes", "alignment", "redundancy", "hallucinations", "golden set",
            "heuristics", "signal extraction", "sprint plan", "validation rules",
            "input features", "templates", "automated routing", "testing steps"
        ]
        
        system_keyword_count = sum(1 for keyword in system_keywords if keyword.lower() in content.lower())
        has_system_building = system_keyword_count >= 2
        
        # Check for technical decision patterns
        decision_patterns = [
            "decided", "chose", "selected", "picked", "went with", "using", "we'll use", "we used",
            "shipped", "rollback", "bypass", "revert", "implemented", "deployed"
        ]
        has_decision_patterns = any(pattern in content.lower() for pattern in decision_patterns)
        
        # Technical journal if: (commands AND decisions) OR (system building) OR (technical tools AND decision patterns) OR (commands AND decision patterns)
        return (has_commands and has_decisions) or has_system_building or (has_technical_tools and has_decision_patterns) or (has_commands and has_decision_patterns)
    
    def _is_research_article(self, anchors: List[Anchor], content: str) -> bool:
        """Check if content is a research article."""
        # Must have research domain terms
        research_terms_count = self.anchor_extractor.count_regex(anchors, self.research_terms_pattern)
        has_research_terms = research_terms_count >= 3
        
        # Must have citations or reading list
        has_citations = self.anchor_extractor.has_citations_or_reading_list(anchors)
        
        # Check for research-specific patterns
        research_patterns = [
            "research findings", "study results", "data analysis", "statistical analysis",
            "hypothesis testing", "research methodology", "literature review", "academic paper",
            "peer-reviewed", "published study", "research paper", "empirical evidence"
        ]
        
        research_pattern_count = sum(1 for pattern in research_patterns if pattern.lower() in content.lower())
        has_research_patterns = research_pattern_count >= 2
        
        return has_research_terms and (has_citations or has_research_patterns)
    
    def _is_critique(self, anchors: List[Anchor], content: str) -> bool:
        """Check if content is a critique."""
        # Must have opinion markers
        has_opinion_markers = self.anchor_extractor.has_opinion_markers(anchors)
        
        # Must have critique tokens
        critique_tokens_count = self.anchor_extractor.count_regex(anchors, self.critique_tokens_pattern)
        has_critique_tokens = critique_tokens_count >= 2
        
        # Check for critique-specific patterns
        critique_patterns = [
            "I argue", "I contend", "I agree", "I disagree", "My thesis", "The claim",
            "however", "but", "on the other hand", "critics might", "steelman",
            "in my opinion", "I believe", "I think"
        ]
        
        critique_pattern_count = sum(1 for pattern in critique_patterns if pattern.lower() in content.lower())
        has_critique_patterns = critique_pattern_count >= 1
        
        return has_opinion_markers and (has_critique_tokens or has_critique_patterns)
    
    def _handle_ties(self, anchors: List[Anchor], content: str) -> Optional[str]:
        """Handle tie-breaking scenarios."""
        # Check if both research and critique indicators are present
        research_score = self._calculate_research_score(anchors, content)
        critique_score = self._calculate_critique_score(anchors, content)
        
        if research_score > 0 and critique_score > 0:
            # Prefer research when there are datasets/benchmarks/frameworks
            has_research_indicators = any([
                "dataset" in content.lower(),
                "benchmark" in content.lower(),
                "ray" in content.lower(),
                "anyscale" in content.lower(),
                "rag" in content.lower()
            ])
            
            if has_research_indicators:
                return "research_article"
            else:
                return "critique"
        
        return None
    
    def _calculate_research_score(self, anchors: List[Anchor], content: str) -> int:
        """Calculate research article score."""
        score = 0
        
        # Research domain terms
        research_terms_count = self.anchor_extractor.count_regex(anchors, self.research_terms_pattern)
        score += research_terms_count * 2
        
        # Citations
        if self.anchor_extractor.has_citations_or_reading_list(anchors):
            score += 5
        
        # Research patterns
        research_patterns = [
            "research findings", "study results", "data analysis", "statistical analysis",
            "hypothesis testing", "research methodology", "literature review", "academic paper"
        ]
        
        for pattern in research_patterns:
            if pattern.lower() in content.lower():
                score += 2
        
        return score
    
    def _calculate_critique_score(self, anchors: List[Anchor], content: str) -> int:
        """Calculate critique score."""
        score = 0
        
        # Opinion markers
        if self.anchor_extractor.has_opinion_markers(anchors):
            score += 5
        
        # Critique tokens
        critique_tokens_count = self.anchor_extractor.count_regex(anchors, self.critique_tokens_pattern)
        score += critique_tokens_count * 2
        
        # Critique patterns
        critique_patterns = [
            "I argue", "I contend", "I agree", "I disagree", "My thesis", "The claim",
            "however", "but", "on the other hand", "critics might", "steelman"
        ]
        
        for pattern in critique_patterns:
            if pattern.lower() in content.lower():
                score += 1
        
        return score
    
    def get_route_confidence(self, content: str, anchors: List[Anchor]) -> Dict[str, Any]:
        """Get routing confidence and reasoning."""
        technical_score = self._calculate_technical_score(anchors, content)
        research_score = self._calculate_research_score(anchors, content)
        critique_score = self._calculate_critique_score(anchors, content)
        
        total_score = technical_score + research_score + critique_score
        
        if total_score == 0:
            return {
                'confidence': 0,
                'reasoning': 'No clear indicators found',
                'scores': {
                    'technical_journal': technical_score,
                    'research_article': research_score,
                    'critique': critique_score
                }
            }
        
        # Calculate confidence as percentage of total
        max_score = max(technical_score, research_score, critique_score)
        confidence = (max_score / total_score) * 100 if total_score > 0 else 0
        
        # Determine reasoning
        if technical_score == max_score:
            reasoning = f'Technical journal indicators: {technical_score} points'
        elif research_score == max_score:
            reasoning = f'Research article indicators: {research_score} points'
        elif critique_score == max_score:
            reasoning = f'Critique indicators: {critique_score} points'
        else:
            reasoning = 'Tie detected, using tie-breaker rules'
        
        return {
            'confidence': confidence,
            'reasoning': reasoning,
            'scores': {
                'technical_journal': technical_score,
                'research_article': research_score,
                'critique': critique_score
            }
        }
    
    def _calculate_technical_score(self, anchors: List[Anchor], content: str) -> int:
        """Calculate technical journal score."""
        score = 0
        
        # Commands
        command_count = self.anchor_extractor.has_commands(anchors)
        score += command_count * 3
        
        # Decisions
        if self.anchor_extractor.has_decision_verbs(anchors):
            score += 5
        
        # Technical tools
        if self.anchor_extractor.mentions(anchors, "ollama"):
            score += 3
        if self.anchor_extractor.mentions(anchors, "litellm"):
            score += 3
        
        # System building keywords
        system_keywords = [
            "summarizer", "pipeline", "system", "build", "develop", "create", "implement",
            "failure modes", "alignment", "redundancy", "hallucinations", "golden set"
        ]
        
        for keyword in system_keywords:
            if keyword.lower() in content.lower():
                score += 1
        
        return score
