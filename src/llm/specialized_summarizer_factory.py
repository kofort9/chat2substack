"""Factory for creating specialized summarizers based on content type."""

from typing import Dict, Any, List
from enum import Enum
from ..util.schema import NormalizedConversation, SubstackDraft

from .comprehensive_summarizer import ComprehensiveTechnicalJournalSummarizer
from .research_article_summarizer import ResearchArticleSummarizer
from .critique_summarizer import CritiqueSummarizer


class ContentType(Enum):
    """Supported content types for summarization."""
    TECHNICAL_JOURNAL = "technical_journal"
    RESEARCH_ARTICLE = "research_article"
    CRITIQUE = "critique"
    TUTORIAL_GUIDE = "tutorial_guide"
    CODE_REVIEW = "code_review"
    PROCESS_DOCUMENTATION = "process_documentation"


class SummarizerFactory:
    """Factory for creating appropriate summarizers based on content type."""
    
    def __init__(self):
        self.summarizers = {
            ContentType.TECHNICAL_JOURNAL: ComprehensiveTechnicalJournalSummarizer(),
            ContentType.RESEARCH_ARTICLE: ResearchArticleSummarizer(),
            ContentType.CRITIQUE: CritiqueSummarizer(),
            # TODO: Implement remaining summarizers
            # ContentType.TUTORIAL_GUIDE: TutorialGuideSummarizer(),
            # ContentType.CODE_REVIEW: CodeReviewSummarizer(),
            # ContentType.PROCESS_DOCUMENTATION: ProcessDocumentationSummarizer(),
        }
    
    def get_summarizer(self, content_type: ContentType):
        """Get the appropriate summarizer for the content type."""
        if content_type not in self.summarizers:
            # Fallback to technical journal for unknown types
            return self.summarizers[ContentType.TECHNICAL_JOURNAL]
        return self.summarizers[content_type]
    
    def get_supported_types(self) -> List[ContentType]:
        """Get list of supported content types."""
        return list(self.summarizers.keys())
    
    def summarize_conversation(self, conversation: NormalizedConversation, content_type: ContentType) -> SubstackDraft:
        """Summarize conversation using the appropriate summarizer."""
        summarizer = self.get_summarizer(content_type)
        return summarizer.summarize(conversation)


class ContentTypeDetector:
    """Enhanced content type detection with confidence scoring."""
    
    def __init__(self):
        self.type_indicators = {
            ContentType.TECHNICAL_JOURNAL: {
                'keywords': [
                    'project', 'build', 'create', 'develop', 'implement', 'code',
                    'sentry', 'testsentry', 'docsentry', 'development', 'programming',
                    'technical', 'architecture', 'system', 'tool', 'automation'
                ],
                'patterns': [
                    r'building\s+(?:a|an|the)\s+([^.!?]+)',
                    r'creating\s+(?:a|an|the)\s+([^.!?]+)',
                    r'developing\s+(?:a|an|the)\s+([^.!?]+)',
                    r'project\s+(?:called|named|titled)\s+([^.!?]+)',
                    r'working on\s+(?:a|an|the)\s+([^.!?]+)'
                ],
                'weight': 1.0
            },
            ContentType.RESEARCH_ARTICLE: {
                'keywords': [
                    'research', 'study', 'analysis', 'investigation', 'findings',
                    'data', 'results', 'conclusion', 'hypothesis', 'methodology',
                    'experiment', 'survey', 'interview', 'observation', 'evidence'
                ],
                'patterns': [
                    r'research\s+(?:on|about|into)\s+([^.!?]+)',
                    r'study\s+(?:of|on|about)\s+([^.!?]+)',
                    r'analysis\s+(?:of|on|about)\s+([^.!?]+)',
                    r'findings\s+(?:show|indicate|suggest)\s+([^.!?]+)',
                    r'conclusion\s+(?:is|was)\s+([^.!?]+)'
                ],
                'weight': 1.0
            },
            ContentType.CRITIQUE: {
                'keywords': [
                    'critique', 'review', 'opinion', 'evaluation', 'assessment',
                    'criticism', 'feedback', 'judgment', 'analysis', 'commentary',
                    'perspective', 'viewpoint', 'stance', 'position', 'argument'
                ],
                'patterns': [
                    r'critique\s+(?:of|on|about)\s+([^.!?]+)',
                    r'review\s+(?:of|on|about)\s+([^.!?]+)',
                    r'opinion\s+(?:on|about|regarding)\s+([^.!?]+)',
                    r'evaluation\s+(?:of|on|about)\s+([^.!?]+)',
                    r'my\s+(?:thoughts|views|perspective)\s+(?:on|about)\s+([^.!?]+)'
                ],
                'weight': 1.0
            }
        }
    
    def detect_content_type(self, conversation: NormalizedConversation) -> tuple[ContentType, float]:
        """Detect content type with confidence score."""
        all_text = ' '.join([msg.text for msg in conversation.messages]).lower()
        
        scores = {}
        for content_type, indicators in self.type_indicators.items():
            score = 0.0
            total_weight = 0.0
            
            # Keyword matching
            for keyword in indicators['keywords']:
                if keyword in all_text:
                    score += 1.0
                total_weight += 1.0
            
            # Pattern matching
            import re
            for pattern in indicators['patterns']:
                matches = re.findall(pattern, all_text, re.IGNORECASE)
                if matches:
                    score += len(matches) * 0.5
                total_weight += 1.0
            
            # Normalize score
            if total_weight > 0:
                scores[content_type] = (score / total_weight) * indicators['weight']
            else:
                scores[content_type] = 0.0
        
        # Find best match
        if not scores or max(scores.values()) == 0:
            return ContentType.TECHNICAL_JOURNAL, 0.0
        
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        return best_type, confidence


def create_specialized_summarizer(content_type: ContentType):
    """Create a specialized summarizer for the given content type."""
    factory = SummarizerFactory()
    return factory.get_summarizer(content_type)


def detect_and_summarize(conversation: NormalizedConversation, auto_detect: bool = True, content_type: ContentType = None) -> tuple[SubstackDraft, ContentType, float]:
    """Detect content type and summarize conversation."""
    if auto_detect:
        detector = ContentTypeDetector()
        detected_type, confidence = detector.detect_content_type(conversation)
    else:
        detected_type = content_type or ContentType.TECHNICAL_JOURNAL
        confidence = 1.0
    
    factory = SummarizerFactory()
    draft = factory.summarize_conversation(conversation, detected_type)
    
    return draft, detected_type, confidence
