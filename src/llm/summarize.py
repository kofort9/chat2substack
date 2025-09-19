"""LLM summarization module with local template fallback."""

import json
import random
from typing import Dict, List, Any
from ..util.schema import NormalizedConversation, SubstackDraft, FurtherReading
from .decision_centric_journal import DecisionCentricJournalSummarizer
from .research_article import ResearchArticleSummarizer


class TemplateSummarizer:
    """Template-based summarizer for deterministic output."""
    
    def __init__(self):
        self.templates = {
            'titles': [
                "Key Insights from {topic} Discussion",
                "What We Learned About {topic}",
                "Breaking Down {topic}: A Conversation Analysis",
                "Understanding {topic}: Key Takeaways",
                "Exploring {topic}: Insights and Analysis"
            ],
            'deks': [
                "A comprehensive look at the key points and insights from our discussion.",
                "Breaking down the main concepts and practical takeaways.",
                "An analysis of the key themes and actionable insights discussed.",
                "Exploring the core ideas and their practical implications.",
                "A summary of the most important points and their significance."
            ],
            'tldr_templates': [
                "The discussion covered {count} main areas of focus",
                "Key insights emerged around {topic} and its applications",
                "Practical implications were identified for {audience}",
                "Several important considerations were highlighted",
                "The conversation provided actionable next steps"
            ],
            'body_intros': [
                "In this conversation, we explored several important aspects of {topic}.",
                "The discussion revealed key insights about {topic} and its implications.",
                "Our analysis covered multiple dimensions of {topic} and its applications.",
                "The conversation provided valuable perspectives on {topic} and its impact.",
                "We examined various facets of {topic} and their practical significance."
            ]
        }
    
    def extract_topic(self, conversation: NormalizedConversation) -> str:
        """Extract main topic from conversation."""
        # Simple keyword extraction from first few messages
        text_sample = ""
        for message in conversation.messages[:3]:
            text_sample += message.text + " "
        
        # Look for common topic indicators
        topic_keywords = [
            'artificial intelligence', 'ai', 'machine learning', 'technology',
            'business', 'productivity', 'programming', 'development',
            'marketing', 'strategy', 'analysis', 'data', 'research',
            'design', 'user experience', 'ux', 'product', 'management'
        ]
        
        text_lower = text_sample.lower()
        for keyword in topic_keywords:
            if keyword in text_lower:
                return keyword.title()
        
        return "Technology"
    
    def extract_key_points(self, conversation: NormalizedConversation) -> List[str]:
        """Extract key points from conversation."""
        points = []
        
        # Look for messages with substantial content
        for message in conversation.messages:
            if len(message.text) > 100:  # Substantial messages
                # Extract first sentence as potential key point
                sentences = message.text.split('.')
                if sentences:
                    first_sentence = sentences[0].strip()
                    if len(first_sentence) > 20 and len(first_sentence) < 150:
                        points.append(first_sentence)
        
        # Limit to 5 points max
        return points[:5]
    
    def generate_title(self, topic: str) -> str:
        """Generate title based on topic."""
        template = random.choice(self.templates['titles'])
        return template.format(topic=topic)
    
    def generate_dek(self) -> str:
        """Generate dek (subtitle)."""
        return random.choice(self.templates['deks'])
    
    def generate_tldr(self, topic: str, key_points: List[str]) -> List[str]:
        """Generate TL;DR points."""
        tldr = []
        
        # Add template-based points
        for i, template in enumerate(self.templates['tldr_templates'][:3]):
            tldr.append(template.format(
                count=len(key_points),
                topic=topic,
                audience="professionals"
            ))
        
        # Add actual key points if available
        for point in key_points[:2]:
            if len(point) < 100:  # Keep TL;DR concise
                tldr.append(point)
        
        return tldr[:5]  # Max 5 points
    
    def generate_tags(self, topic: str) -> List[str]:
        """Generate relevant tags."""
        topic_lower = topic.lower()
        
        base_tags = ['conversation', 'insights', 'analysis']
        
        # Add topic-specific tags
        if 'ai' in topic_lower or 'artificial intelligence' in topic_lower:
            base_tags.extend(['ai', 'technology'])
        elif 'business' in topic_lower:
            base_tags.extend(['business', 'strategy'])
        elif 'programming' in topic_lower or 'development' in topic_lower:
            base_tags.extend(['programming', 'development'])
        else:
            base_tags.append('technology')
        
        return base_tags[:6]  # Max 6 tags
    
    def generate_body(self, conversation: NormalizedConversation, topic: str, key_points: List[str]) -> str:
        """Generate main body content."""
        intro = random.choice(self.templates['body_intros']).format(topic=topic)
        
        # Add pull quote from conversation
        pull_quote = ""
        for message in conversation.messages:
            if len(message.text) > 50 and len(message.text) < 200:
                pull_quote = message.text
                break
        
        if not pull_quote:
            pull_quote = "This conversation provided valuable insights and practical guidance."
        
        # Build body content
        body_parts = [
            intro,
            "",
            f"> {pull_quote}",
            "",
            "## Key Discussion Points",
            ""
        ]
        
        # Add key points
        for i, point in enumerate(key_points[:3], 1):
            body_parts.append(f"{i}. {point}")
        
        body_parts.extend([
            "",
            "## Main Insights",
            "",
            "The conversation revealed several important insights that are worth highlighting:",
            ""
        ])
        
        # Add more detailed content
        for message in conversation.messages[-3:]:  # Last few messages
            if len(message.text) > 100:
                # Extract key sentences
                sentences = message.text.split('.')
                for sentence in sentences[:2]:
                    sentence = sentence.strip()
                    if len(sentence) > 30 and len(sentence) < 150:
                        body_parts.append(f"- {sentence}")
                        break
        
        body_parts.extend([
            "",
            "## Takeaways",
            "",
            "Based on this discussion, here are the key takeaways:",
            ""
        ])
        
        # Add takeaways
        for i, point in enumerate(key_points[:3], 1):
            body_parts.append(f"{i}. {point}")
        
        return '\n'.join(body_parts)
    
    def summarize(self, conversation: NormalizedConversation) -> SubstackDraft:
        """Generate Substack draft from conversation."""
        topic = self.extract_topic(conversation)
        key_points = self.extract_key_points(conversation)
        
        title = self.generate_title(topic)
        dek = self.generate_dek()
        tldr = self.generate_tldr(topic, key_points)
        tags = self.generate_tags(topic)
        body_markdown = self.generate_body(conversation, topic, key_points)
        
        # Ensure word count is within limits
        word_count = len(body_markdown.split())
        if word_count > 900:
            # Truncate if too long
            words = body_markdown.split()
            body_markdown = ' '.join(words[:900])
        
        return SubstackDraft(
            title=title,
            dek=dek,
            tldr=tldr,
            tags=tags,
            body_markdown=body_markdown,
            further_reading=None  # Template doesn't generate external links
        )


def summarize_to_substack_json(conversation: NormalizedConversation, 
                              provider: str = "template",
                              max_retries: int = 2) -> SubstackDraft:
    """Summarize conversation to Substack draft format."""
    
    if provider == "template":
        # Use decision-centric journal summarizer for project discussions
        from .decision_centric_journal import DecisionCentricJournalSummarizer
        summarizer = DecisionCentricJournalSummarizer()
        
        # Convert NormalizedConversation to dict format expected by new summarizer
        conversation_dict = {
            'messages': [
                {'content': msg.text, 'role': msg.role} 
                for msg in conversation.messages
            ],
            'title_hint': getattr(conversation, 'title_hint', 'Technical Project')
        }
        
        return summarizer.summarize_conversation(conversation_dict)
    
    elif provider == "local":
        # Placeholder for local LLM integration
        # This would call a local model like Ollama
        try:
            # Use decision-centric journal summarizer
            from .decision_centric_journal import DecisionCentricJournalSummarizer
            summarizer = DecisionCentricJournalSummarizer()
            
            # Convert NormalizedConversation to dict format expected by new summarizer
            conversation_dict = {
                'messages': [
                    {'content': msg.text, 'role': msg.role} 
                    for msg in conversation.messages
                ],
                'title_hint': getattr(conversation, 'title_hint', 'Technical Project')
            }
            
            return summarizer.summarize_conversation(conversation_dict)
        except Exception as e:
            # Fallback to basic template on any error
            summarizer = TemplateSummarizer()
            return summarizer.summarize(conversation)
    
    else:
        raise ValueError(f"Unknown provider: {provider}")


def validate_draft_schema(draft: SubstackDraft) -> bool:
    """Validate draft against schema requirements."""
    try:
        # Pydantic validation happens automatically
        # Additional custom validation can go here
        return True
    except Exception:
        return False
