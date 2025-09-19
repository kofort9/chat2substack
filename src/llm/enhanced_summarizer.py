"""Enhanced summarization module with sophisticated content analysis and prompt engineering."""

import re
import json
from typing import Dict, List, Any, Tuple
from ..util.schema import NormalizedConversation, SubstackDraft, FurtherReading


class ConversationAnalyzer:
    """Analyzes conversation content to extract meaningful insights."""
    
    def __init__(self):
        self.topic_keywords = {
            'education': ['education', 'teaching', 'school', 'university', 'student', 'teacher', 'learning', 'curriculum', 'academic'],
            'technology': ['technology', 'ai', 'artificial intelligence', 'machine learning', 'software', 'programming', 'digital', 'tech'],
            'business': ['business', 'company', 'startup', 'entrepreneur', 'strategy', 'marketing', 'sales', 'management'],
            'politics': ['politics', 'government', 'policy', 'election', 'democracy', 'republican', 'democrat', 'political'],
            'society': ['society', 'social', 'culture', 'community', 'people', 'human', 'society', 'social issues'],
            'science': ['science', 'research', 'study', 'data', 'analysis', 'experiment', 'scientific', 'evidence'],
            'philosophy': ['philosophy', 'ethics', 'moral', 'values', 'beliefs', 'philosophical', 'ethical', 'morality'],
            'health': ['health', 'medical', 'healthcare', 'medicine', 'wellness', 'fitness', 'mental health'],
            'economics': ['economics', 'economy', 'financial', 'money', 'investment', 'market', 'economic', 'finance']
        }
        
        self.sentiment_indicators = {
            'positive': ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'enjoy', 'benefit', 'helpful', 'useful'],
            'negative': ['bad', 'terrible', 'awful', 'hate', 'dislike', 'problem', 'issue', 'concern', 'worry', 'difficult', 'challenge'],
            'neutral': ['think', 'believe', 'consider', 'discuss', 'explore', 'analyze', 'examine', 'understand', 'explain']
        }
    
    def analyze_conversation(self, conversation: NormalizedConversation) -> Dict[str, Any]:
        """Perform comprehensive analysis of conversation content."""
        user_messages = [msg.text for msg in conversation.messages if msg.role == "user"]
        assistant_messages = [msg.text for msg in conversation.messages if msg.role == "assistant"]
        
        # Combine all text for analysis
        all_text = " ".join([msg.text for msg in conversation.messages])
        
        analysis = {
            'primary_topic': self._identify_primary_topic(all_text),
            'secondary_topics': self._identify_secondary_topics(all_text),
            'sentiment': self._analyze_sentiment(all_text),
            'key_questions': self._extract_questions(user_messages),
            'key_insights': self._extract_insights(assistant_messages),
            'controversial_topics': self._identify_controversial_topics(all_text),
            'practical_applications': self._extract_practical_applications(all_text),
            'word_count': len(all_text.split()),
            'message_count': len(conversation.messages),
            'conversation_depth': self._assess_conversation_depth(conversation.messages)
        }
        
        return analysis
    
    def _identify_primary_topic(self, text: str) -> str:
        """Identify the primary topic of discussion."""
        text_lower = text.lower()
        topic_scores = {}
        
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        return 'general'
    
    def _identify_secondary_topics(self, text: str) -> List[str]:
        """Identify secondary topics mentioned."""
        text_lower = text.lower()
        secondary_topics = []
        
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score >= 2:  # Threshold for secondary topics
                secondary_topics.append(topic)
        
        return secondary_topics[:3]  # Limit to 3 secondary topics
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze overall sentiment of the conversation."""
        text_lower = text.lower()
        positive_count = sum(1 for word in self.sentiment_indicators['positive'] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_indicators['negative'] if word in text_lower)
        
        if positive_count > negative_count * 1.5:
            return 'positive'
        elif negative_count > positive_count * 1.5:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_questions(self, user_messages: List[str]) -> List[str]:
        """Extract key questions from user messages."""
        questions = []
        for message in user_messages:
            # Look for question patterns
            sentences = re.split(r'[.!?]+', message)
            for sentence in sentences:
                sentence = sentence.strip()
                if '?' in sentence and len(sentence) > 10:
                    # Clean up the question
                    question = re.sub(r'^(I\'m|I am|I think|I believe|I need|I want|I have|I can|I should|I would|I don\'t|I can\'t|I won\'t|I\'ll|I\'ve|I\'d)\s+', '', sentence, flags=re.IGNORECASE)
                    question = question.strip()
                    if len(question) > 15 and len(question) < 200:
                        questions.append(question)
        
        return questions[:3]  # Limit to 3 key questions
    
    def _extract_insights(self, assistant_messages: List[str]) -> List[str]:
        """Extract key insights from assistant messages."""
        insights = []
        for message in assistant_messages:
            if len(message) > 100:  # Substantial messages
                # Look for numbered lists or bullet points
                lines = message.split('\n')
                for line in lines:
                    line = line.strip()
                    # Look for numbered items or bullet points
                    if re.match(r'^\d+\.', line) or re.match(r'^[-*•]', line):
                        insight = re.sub(r'^\d+\.\s*|^[-*•]\s*', '', line)
                        if len(insight) > 20 and len(insight) < 150:
                            insights.append(insight)
                    # Look for sentences that start with key insight indicators
                    elif any(indicator in line.lower() for indicator in ['key insight', 'important', 'crucial', 'essential', 'fundamental', 'the main point', 'the key is']):
                        if len(line) > 30 and len(line) < 200:
                            insights.append(line)
        
        return insights[:5]  # Limit to 5 key insights
    
    def _identify_controversial_topics(self, text: str) -> List[str]:
        """Identify potentially controversial topics."""
        controversial_keywords = [
            'politics', 'religion', 'gender', 'race', 'sexuality', 'abortion', 'gun control',
            'immigration', 'climate change', 'vaccine', 'covid', 'trump', 'biden',
            'lgbtq', 'transgender', 'feminism', 'conservative', 'liberal', 'democrat', 'republican'
        ]
        
        text_lower = text.lower()
        controversial_topics = []
        
        for keyword in controversial_keywords:
            if keyword in text_lower:
                controversial_topics.append(keyword)
        
        return controversial_topics
    
    def _extract_practical_applications(self, text: str) -> List[str]:
        """Extract practical applications or actionable insights."""
        practical_indicators = [
            'how to', 'steps to', 'ways to', 'tips for', 'best practices', 'recommendations',
            'actionable', 'practical', 'implement', 'apply', 'use', 'utilize', 'leverage'
        ]
        
        text_lower = text.lower()
        applications = []
        
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in practical_indicators):
                if len(sentence) > 20 and len(sentence) < 200:
                    applications.append(sentence)
        
        return applications[:3]  # Limit to 3 practical applications
    
    def _assess_conversation_depth(self, messages: List[Any]) -> str:
        """Assess the depth of the conversation."""
        total_words = sum(len(msg.text.split()) for msg in messages)
        avg_message_length = total_words / len(messages) if messages else 0
        
        if avg_message_length > 200:
            return 'deep'
        elif avg_message_length > 100:
            return 'moderate'
        else:
            return 'surface'


class EnhancedSummarizer:
    """Enhanced summarizer with sophisticated prompt engineering."""
    
    def __init__(self):
        self.analyzer = ConversationAnalyzer()
        self.topic_templates = {
            'education': {
                'titles': [
                    "The {topic} Debate: {subtitle}",
                    "Understanding {topic} in Education",
                    "Exploring {topic}: Educational Perspectives",
                    "The Future of {topic} in Learning",
                    "Breaking Down {topic}: What We Need to Know"
                ],
                'deks': [
                    "A deep dive into the educational implications of {topic}",
                    "Exploring how {topic} shapes modern education",
                    "Understanding the role of {topic} in learning environments",
                    "Analyzing the educational impact of {topic}",
                    "Examining {topic} through an educational lens"
                ]
            },
            'technology': {
                'titles': [
                    "The {topic} Revolution: {subtitle}",
                    "Understanding {topic}: A Technical Deep Dive",
                    "Exploring {topic}: Innovation and Impact",
                    "The Future of {topic}: What's Next",
                    "Breaking Down {topic}: Technical Insights"
                ],
                'deks': [
                    "A comprehensive look at {topic} and its implications",
                    "Exploring the technical aspects of {topic}",
                    "Understanding how {topic} is changing the landscape",
                    "Analyzing the impact of {topic} on technology",
                    "Examining {topic} from a technical perspective"
                ]
            },
            'politics': {
                'titles': [
                    "The {topic} Discussion: {subtitle}",
                    "Understanding {topic}: Political Perspectives",
                    "Exploring {topic}: Policy and Impact",
                    "The Politics of {topic}: What Matters",
                    "Breaking Down {topic}: Political Analysis"
                ],
                'deks': [
                    "A balanced look at the political implications of {topic}",
                    "Exploring how {topic} shapes political discourse",
                    "Understanding the political dimensions of {topic}",
                    "Analyzing the policy impact of {topic}",
                    "Examining {topic} through a political lens"
                ]
            },
            'society': {
                'titles': [
                    "The {topic} Conversation: {subtitle}",
                    "Understanding {topic}: Social Perspectives",
                    "Exploring {topic}: Community and Impact",
                    "The Social Side of {topic}: What We're Learning",
                    "Breaking Down {topic}: Social Analysis"
                ],
                'deks': [
                    "A thoughtful exploration of {topic} and its social impact",
                    "Understanding how {topic} affects communities",
                    "Exploring the social dimensions of {topic}",
                    "Analyzing the community impact of {topic}",
                    "Examining {topic} from a social perspective"
                ]
            }
        }
    
    def generate_title(self, analysis: Dict[str, Any], original_title: str) -> str:
        """Generate a compelling title based on analysis."""
        primary_topic = analysis['primary_topic']
        controversial_topics = analysis['controversial_topics']
        
        # Use original title if it's good
        if original_title and len(original_title) > 10 and original_title != "Untitled Conversation":
            return original_title[:80]  # Ensure it fits within limits
        
        # Generate based on topic
        if primary_topic in self.topic_templates:
            templates = self.topic_templates[primary_topic]['titles']
        else:
            templates = self.topic_templates['society']['titles']
        
        # Create subtitle based on controversial topics or key insights
        subtitle = ""
        if controversial_topics:
            subtitle = f"Navigating {controversial_topics[0].title()}"
        elif analysis['key_insights']:
            subtitle = "Key Insights and Analysis"
        else:
            subtitle = "A Deep Dive"
        
        template = templates[0]  # Use first template for consistency
        title = template.format(topic=primary_topic.title(), subtitle=subtitle)
        
        return title[:80]  # Ensure it fits within limits
    
    def generate_dek(self, analysis: Dict[str, Any]) -> str:
        """Generate a compelling dek (subtitle)."""
        primary_topic = analysis['primary_topic']
        key_questions = analysis['key_questions']
        
        if primary_topic in self.topic_templates:
            templates = self.topic_templates[primary_topic]['deks']
        else:
            templates = self.topic_templates['society']['deks']
        
        template = templates[0]  # Use first template for consistency
        dek = template.format(topic=primary_topic)
        
        # Add question if available
        if key_questions:
            question = key_questions[0]
            if len(question) < 100:
                dek += f" We explore: {question}"
        
        return dek[:200]  # Ensure it fits within limits
    
    def generate_tldr(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate TL;DR points based on analysis."""
        tldr = []
        
        # Add primary topic insight
        primary_topic = analysis['primary_topic']
        tldr.append(f"The discussion centers around {primary_topic} and its implications")
        
        # Add key insights
        for insight in analysis['key_insights'][:2]:
            if len(insight) < 100:
                tldr.append(insight)
        
        # Add practical applications
        for app in analysis['practical_applications'][:1]:
            if len(app) < 100:
                tldr.append(app)
        
        # Add conversation depth insight
        depth = analysis['conversation_depth']
        if depth == 'deep':
            tldr.append("The conversation provided in-depth analysis and detailed exploration")
        elif depth == 'moderate':
            tldr.append("The discussion covered multiple perspectives and key considerations")
        
        # Ensure we have at least 3 points
        while len(tldr) < 3:
            tldr.append("The conversation revealed important insights worth considering")
        
        return tldr[:5]  # Max 5 points
    
    def generate_tags(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate relevant tags based on analysis."""
        tags = []
        
        # Add primary topic
        primary_topic = analysis['primary_topic']
        tags.append(primary_topic)
        
        # Add secondary topics
        for topic in analysis['secondary_topics'][:2]:
            tags.append(topic)
        
        # Add sentiment-based tags
        sentiment = analysis['sentiment']
        if sentiment == 'positive':
            tags.append('insights')
        elif sentiment == 'negative':
            tags.append('analysis')
        else:
            tags.append('discussion')
        
        # Add depth-based tags
        depth = analysis['conversation_depth']
        if depth == 'deep':
            tags.append('deep-dive')
        elif depth == 'moderate':
            tags.append('analysis')
        
        # Add controversial topic tags
        if analysis['controversial_topics']:
            tags.append('controversial')
        
        # Ensure we have at least 3 tags
        while len(tags) < 3:
            tags.append('conversation')
        
        return tags[:6]  # Max 6 tags
    
    def generate_body(self, conversation: NormalizedConversation, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive body content."""
        primary_topic = analysis['primary_topic']
        key_questions = analysis['key_questions']
        key_insights = analysis['key_insights']
        practical_applications = analysis['practical_applications']
        controversial_topics = analysis['controversial_topics']
        
        body_parts = []
        
        # Introduction
        intro = f"In this conversation, we explored {primary_topic} and its various implications. "
        if key_questions:
            intro += f"The discussion centered around key questions like: {key_questions[0]}"
        else:
            intro += "The discussion provided valuable insights and perspectives."
        
        body_parts.append(intro)
        body_parts.append("")
        
        # Add pull quote from conversation
        pull_quote = self._extract_pull_quote(conversation.messages)
        if pull_quote:
            body_parts.append(f"> {pull_quote}")
            body_parts.append("")
        
        # Key Discussion Points
        body_parts.append("## Key Discussion Points")
        body_parts.append("")
        
        for i, insight in enumerate(key_insights[:3], 1):
            body_parts.append(f"{i}. {insight}")
        
        body_parts.append("")
        
        # Main Insights
        body_parts.append("## Main Insights")
        body_parts.append("")
        body_parts.append("The conversation revealed several important insights that are worth highlighting:")
        body_parts.append("")
        
        for insight in key_insights[3:6]:  # Additional insights
            body_parts.append(f"- {insight}")
        
        body_parts.append("")
        
        # Controversial Topics (if any)
        if controversial_topics:
            body_parts.append("## Navigating Complex Topics")
            body_parts.append("")
            body_parts.append(f"The discussion touched on {', '.join(controversial_topics)}, highlighting the nuanced nature of these topics and the importance of thoughtful dialogue.")
            body_parts.append("")
        
        # Practical Applications
        if practical_applications:
            body_parts.append("## Practical Applications")
            body_parts.append("")
            for app in practical_applications:
                body_parts.append(f"- {app}")
            body_parts.append("")
        
        # Takeaways
        body_parts.append("## Key Takeaways")
        body_parts.append("")
        body_parts.append("Based on this discussion, here are the key takeaways:")
        body_parts.append("")
        
        for i, insight in enumerate(key_insights[:3], 1):
            body_parts.append(f"{i}. {insight}")
        
        return '\n'.join(body_parts)
    
    def _extract_pull_quote(self, messages: List[Any]) -> str:
        """Extract a compelling pull quote from the conversation."""
        for message in messages:
            if len(message.text) > 50 and len(message.text) < 200:
                # Look for sentences that would make good pull quotes
                sentences = message.text.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 30 and len(sentence) < 150:
                        # Check if it's a good pull quote
                        if any(indicator in sentence.lower() for indicator in ['key', 'important', 'crucial', 'essential', 'fundamental', 'the main point', 'the key is', 'what matters', 'the truth is']):
                            return sentence
        
        # Fallback to any substantial message
        for message in messages:
            if len(message.text) > 50 and len(message.text) < 200:
                return message.text
        
        return "This conversation provided valuable insights and practical guidance."
    
    def generate_further_reading(self, analysis: Dict[str, Any]) -> List[FurtherReading]:
        """Generate further reading suggestions based on analysis."""
        primary_topic = analysis['primary_topic']
        
        # Topic-specific further reading suggestions
        further_reading_map = {
            'education': [
                FurtherReading(title="The Future of Education", url="https://example.com/education-future"),
                FurtherReading(title="Teaching in the Digital Age", url="https://example.com/digital-teaching")
            ],
            'technology': [
                FurtherReading(title="AI and Society", url="https://example.com/ai-society"),
                FurtherReading(title="The Impact of Technology", url="https://example.com/tech-impact")
            ],
            'politics': [
                FurtherReading(title="Political Analysis", url="https://example.com/political-analysis"),
                FurtherReading(title="Policy and Governance", url="https://example.com/policy-governance")
            ],
            'society': [
                FurtherReading(title="Social Issues Today", url="https://example.com/social-issues"),
                FurtherReading(title="Community and Society", url="https://example.com/community-society")
            ]
        }
        
        return further_reading_map.get(primary_topic, [])
    
    def summarize(self, conversation: NormalizedConversation) -> SubstackDraft:
        """Generate enhanced Substack draft from conversation."""
        # Analyze the conversation
        analysis = self.analyzer.analyze_conversation(conversation)
        
        # Generate components
        title = self.generate_title(analysis, conversation.title_hint)
        dek = self.generate_dek(analysis)
        tldr = self.generate_tldr(analysis)
        tags = self.generate_tags(analysis)
        body_markdown = self.generate_body(conversation, analysis)
        further_reading = self.generate_further_reading(analysis)
        
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
            further_reading=further_reading
        )


def summarize_conversation_enhanced(conversation: NormalizedConversation) -> SubstackDraft:
    """Enhanced conversation summarization."""
    summarizer = EnhancedSummarizer()
    return summarizer.summarize(conversation)
