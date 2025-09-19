"""Automated routing logic for intelligent summarizer selection."""

import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from ..util.schema import NormalizedConversation, SubstackDraft
from .specialized_summarizer_factory import ContentType, SummarizerFactory, ContentTypeDetector


@dataclass
class RoutingDecision:
    """Result of automated routing decision."""
    content_type: ContentType
    confidence: float
    reasoning: List[str]
    alternative_types: List[Tuple[ContentType, float]]
    fallback_used: bool = False


class AdvancedContentAnalyzer:
    """Advanced content analysis for better routing decisions."""
    
    def __init__(self):
        self.content_indicators = {
            ContentType.TECHNICAL_JOURNAL: {
                'strong_indicators': [
                    'project', 'build', 'create', 'develop', 'implement', 'code',
                    'sentry', 'testsentry', 'docsentry', 'development', 'programming',
                    'technical', 'architecture', 'system', 'tool', 'automation',
                    'github', 'repository', 'commit', 'pull request', 'deployment'
                ],
                'weak_indicators': [
                    'working on', 'building', 'creating', 'developing', 'implementing',
                    'setup', 'configuration', 'installation', 'testing', 'debugging'
                ],
                'patterns': [
                    r'building\s+(?:a|an|the)\s+([^.!?]+)',
                    r'creating\s+(?:a|an|the)\s+([^.!?]+)',
                    r'developing\s+(?:a|an|the)\s+([^.!?]+)',
                    r'project\s+(?:called|named|titled)\s+([^.!?]+)',
                    r'working on\s+(?:a|an|the)\s+([^.!?]+)',
                    r'github\.com/[^/]+/[^/]+',  # GitHub URLs
                    r'git clone', r'git push', r'git pull'
                ],
                'weight': 1.0
            },
            ContentType.RESEARCH_ARTICLE: {
                'strong_indicators': [
                    'research', 'study', 'analysis', 'investigation', 'findings',
                    'data', 'results', 'conclusion', 'hypothesis', 'methodology',
                    'experiment', 'survey', 'interview', 'observation', 'evidence',
                    'statistics', 'survey', 'poll', 'study shows', 'research indicates'
                ],
                'weak_indicators': [
                    'according to', 'studies show', 'research suggests', 'data shows',
                    'findings indicate', 'analysis reveals', 'investigation shows'
                ],
                'patterns': [
                    r'research\s+(?:on|about|into)\s+([^.!?]+)',
                    r'study\s+(?:of|on|about)\s+([^.!?]+)',
                    r'analysis\s+(?:of|on|about)\s+([^.!?]+)',
                    r'findings\s+(?:show|indicate|suggest)\s+([^.!?]+)',
                    r'conclusion\s+(?:is|was)\s+([^.!?]+)',
                    r'according to\s+([^.!?]+)',
                    r'studies show\s+([^.!?]+)'
                ],
                'weight': 1.0
            },
            ContentType.CRITIQUE: {
                'strong_indicators': [
                    'critique', 'review', 'opinion', 'evaluation', 'assessment',
                    'criticism', 'feedback', 'judgment', 'analysis', 'commentary',
                    'perspective', 'viewpoint', 'stance', 'position', 'argument',
                    'disagree', 'agree', 'think', 'believe', 'feel', 'consider'
                ],
                'weak_indicators': [
                    'in my opinion', 'i think', 'i believe', 'i feel', 'i consider',
                    'my view', 'my perspective', 'my stance', 'my position'
                ],
                'patterns': [
                    r'critique\s+(?:of|on|about)\s+([^.!?]+)',
                    r'review\s+(?:of|on|about)\s+([^.!?]+)',
                    r'opinion\s+(?:on|about|regarding)\s+([^.!?]+)',
                    r'evaluation\s+(?:of|on|about)\s+([^.!?]+)',
                    r'my\s+(?:thoughts|views|perspective)\s+(?:on|about)\s+([^.!?]+)',
                    r'i\s+(?:think|believe|feel|consider)\s+([^.!?]+)'
                ],
                'weight': 1.0
            }
        }
        
        # Context-based indicators
        self.context_indicators = {
            'technical_context': [
                'api', 'database', 'server', 'client', 'framework', 'library',
                'algorithm', 'function', 'class', 'method', 'variable', 'code',
                'debug', 'test', 'error', 'bug', 'fix', 'patch', 'version'
            ],
            'research_context': [
                'data', 'statistics', 'survey', 'interview', 'observation',
                'hypothesis', 'theory', 'model', 'prediction', 'correlation',
                'causation', 'sample', 'population', 'variable', 'control'
            ],
            'opinion_context': [
                'should', 'shouldn\'t', 'must', 'mustn\'t', 'better', 'worse',
                'good', 'bad', 'excellent', 'terrible', 'amazing', 'awful',
                'recommend', 'suggest', 'advise', 'warn', 'caution'
            ]
        }
    
    def analyze_content(self, conversation: NormalizedConversation) -> Dict[str, Any]:
        """Perform comprehensive content analysis for routing."""
        all_text = ' '.join([msg.text for msg in conversation.messages]).lower()
        user_messages = [msg.text for msg in conversation.messages if msg.role == "user"]
        assistant_messages = [msg.text for msg in conversation.messages if msg.role == "assistant"]
        
        analysis = {
            'text_length': len(all_text),
            'message_count': len(conversation.messages),
            'user_message_count': len(user_messages),
            'assistant_message_count': len(assistant_messages),
            'content_scores': {},
            'context_scores': {},
            'pattern_matches': {},
            'confidence_factors': []
        }
        
        # Analyze each content type
        for content_type, indicators in self.content_indicators.items():
            score = self._calculate_content_score(all_text, indicators)
            analysis['content_scores'][content_type] = score
        
        # Analyze context indicators
        for context_type, indicators in self.context_indicators.items():
            score = self._calculate_context_score(all_text, indicators)
            analysis['context_scores'][context_type] = score
        
        # Find pattern matches
        for content_type, indicators in self.content_indicators.items():
            matches = self._find_pattern_matches(all_text, indicators['patterns'])
            analysis['pattern_matches'][content_type] = matches
        
        # Calculate confidence factors
        analysis['confidence_factors'] = self._calculate_confidence_factors(analysis)
        
        return analysis
    
    def _calculate_content_score(self, text: str, indicators: Dict[str, Any]) -> float:
        """Calculate content score for a specific type."""
        score = 0.0
        total_weight = 0.0
        
        # Strong indicators (weight 2.0)
        for indicator in indicators['strong_indicators']:
            if indicator in text:
                score += 2.0
            total_weight += 2.0
        
        # Weak indicators (weight 1.0)
        for indicator in indicators['weak_indicators']:
            if indicator in text:
                score += 1.0
            total_weight += 1.0
        
        # Pattern matches (weight 1.5)
        for pattern in indicators['patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                score += len(matches) * 1.5
            total_weight += 1.5
        
        return (score / total_weight) * indicators['weight'] if total_weight > 0 else 0.0
    
    def _calculate_context_score(self, text: str, indicators: List[str]) -> float:
        """Calculate context score for a specific context type."""
        matches = sum(1 for indicator in indicators if indicator in text)
        return matches / len(indicators) if indicators else 0.0
    
    def _find_pattern_matches(self, text: str, patterns: List[str]) -> List[str]:
        """Find pattern matches in text."""
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches.extend(found)
        return matches
    
    def _calculate_confidence_factors(self, analysis: Dict[str, Any]) -> List[str]:
        """Calculate factors that affect routing confidence."""
        factors = []
        
        # Text length factor
        if analysis['text_length'] > 5000:
            factors.append("high_text_length")
        elif analysis['text_length'] < 500:
            factors.append("low_text_length")
        
        # Message count factor
        if analysis['message_count'] > 20:
            factors.append("high_message_count")
        elif analysis['message_count'] < 3:
            factors.append("low_message_count")
        
        # Content score distribution
        scores = list(analysis['content_scores'].values())
        if scores:
            max_score = max(scores)
            if max_score > 0.5:
                factors.append("strong_content_indicators")
            if max_score < 0.1:
                factors.append("weak_content_indicators")
        
        # Context score distribution
        context_scores = list(analysis['context_scores'].values())
        if context_scores:
            max_context = max(context_scores)
            if max_context > 0.3:
                factors.append("strong_context_indicators")
        
        return factors


class AutomatedRouter:
    """Automated routing system for intelligent summarizer selection."""
    
    def __init__(self):
        self.analyzer = AdvancedContentAnalyzer()
        self.factory = SummarizerFactory()
        self.detector = ContentTypeDetector()
        
        # Routing thresholds
        self.confidence_threshold = 0.6
        self.minimum_confidence = 0.3
        self.fallback_type = ContentType.TECHNICAL_JOURNAL
    
    def route_conversation(self, conversation: NormalizedConversation, 
                          user_preference: Optional[ContentType] = None) -> RoutingDecision:
        """Route conversation to appropriate summarizer with detailed reasoning."""
        
        # If user has a preference, use it with high confidence
        if user_preference:
            return RoutingDecision(
                content_type=user_preference,
                confidence=0.9,
                reasoning=[f"User explicitly requested {user_preference.value}"],
                alternative_types=[],
                fallback_used=False
            )
        
        # Perform comprehensive analysis
        analysis = self.analyzer.analyze_content(conversation)
        
        # Get content type scores
        content_scores = analysis['content_scores']
        
        # Sort by score
        sorted_types = sorted(content_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Determine primary type
        primary_type, primary_score = sorted_types[0]
        
        # Calculate confidence
        confidence = self._calculate_routing_confidence(analysis, primary_score, sorted_types)
        
        # Generate reasoning
        reasoning = self._generate_routing_reasoning(analysis, primary_type, primary_score)
        
        # Get alternative types
        alternative_types = [(t, score) for t, score in sorted_types[1:] if score > 0.1]
        
        # Determine if fallback is needed
        fallback_used = confidence < self.minimum_confidence
        
        if fallback_used:
            primary_type = self.fallback_type
            confidence = 0.5
            reasoning.append(f"Low confidence routing, using fallback: {self.fallback_type.value}")
        
        return RoutingDecision(
            content_type=primary_type,
            confidence=confidence,
            reasoning=reasoning,
            alternative_types=alternative_types,
            fallback_used=fallback_used
        )
    
    def _calculate_routing_confidence(self, analysis: Dict[str, Any], 
                                    primary_score: float, 
                                    sorted_types: List[Tuple[ContentType, float]]) -> float:
        """Calculate routing confidence based on analysis."""
        confidence = primary_score
        
        # Adjust based on score distribution
        if len(sorted_types) > 1:
            second_score = sorted_types[1][1]
            score_gap = primary_score - second_score
            if score_gap > 0.3:
                confidence += 0.1  # Bonus for clear winner
            elif score_gap < 0.1:
                confidence -= 0.2  # Penalty for close scores
        
        # Adjust based on confidence factors
        factors = analysis['confidence_factors']
        if 'high_text_length' in factors:
            confidence += 0.1
        if 'low_text_length' in factors:
            confidence -= 0.2
        if 'strong_content_indicators' in factors:
            confidence += 0.15
        if 'weak_content_indicators' in factors:
            confidence -= 0.2
        if 'strong_context_indicators' in factors:
            confidence += 0.1
        
        # Cap confidence between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _generate_routing_reasoning(self, analysis: Dict[str, Any], 
                                  content_type: ContentType, 
                                  score: float) -> List[str]:
        """Generate human-readable reasoning for routing decision."""
        reasoning = []
        
        # Primary score reasoning
        reasoning.append(f"Content type '{content_type.value}' scored {score:.2f}")
        
        # Pattern match reasoning
        pattern_matches = analysis['pattern_matches'].get(content_type, [])
        if pattern_matches:
            reasoning.append(f"Found {len(pattern_matches)} pattern matches: {pattern_matches[:2]}")
        
        # Context reasoning
        context_scores = analysis['context_scores']
        max_context = max(context_scores.items(), key=lambda x: x[1])
        if max_context[1] > 0.2:
            reasoning.append(f"Strong {max_context[0]} context indicators")
        
        # Confidence factor reasoning
        factors = analysis['confidence_factors']
        if 'high_text_length' in factors:
            reasoning.append("High text length provides good context")
        if 'strong_content_indicators' in factors:
            reasoning.append("Strong content indicators detected")
        
        return reasoning
    
    def summarize_with_routing(self, conversation: NormalizedConversation, 
                             user_preference: Optional[ContentType] = None) -> Tuple[SubstackDraft, RoutingDecision]:
        """Summarize conversation using automated routing."""
        routing_decision = self.route_conversation(conversation, user_preference)
        summarizer = self.factory.get_summarizer(routing_decision.content_type)
        draft = summarizer.summarize(conversation)
        
        return draft, routing_decision


def auto_route_and_summarize(conversation: NormalizedConversation, 
                           user_preference: Optional[ContentType] = None) -> Tuple[SubstackDraft, RoutingDecision]:
    """Public interface for automated routing and summarization."""
    router = AutomatedRouter()
    return router.summarize_with_routing(conversation, user_preference)
