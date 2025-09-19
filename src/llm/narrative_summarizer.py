"""Narrative-style summarization module for creating engaging, thought-provoking posts."""

import re
from typing import Dict, List, Any, Optional
from ..util.schema import NormalizedConversation, SubstackDraft, FurtherReading
from .enhanced_summarizer import ConversationAnalyzer


class NarrativeSummarizer:
    """Creates narrative-style posts that engage readers and provoke thought."""
    
    def __init__(self):
        self.analyzer = ConversationAnalyzer()
        self.narrative_templates = {
            'education': {
                'hooks': [
                    "What if everything we thought we knew about {topic} was wrong?",
                    "The conversation that changed my perspective on {topic}",
                    "Why {topic} matters more than we think",
                    "The uncomfortable truth about {topic} that nobody wants to discuss"
                ],
                'transitions': [
                    "But here's where it gets interesting...",
                    "This raises a deeper question:",
                    "What struck me most was...",
                    "The real issue isn't what you think it is...",
                    "This got me thinking about..."
                ]
            },
            'technology': {
                'hooks': [
                    "The technology that's quietly reshaping our world",
                    "What happens when {topic} meets reality?",
                    "The hidden implications of {topic} that nobody talks about",
                    "Why {topic} is more complex than it appears"
                ],
                'transitions': [
                    "But the real story is...",
                    "Here's what most people miss:",
                    "The implications are staggering...",
                    "This raises a crucial question:",
                    "What's really happening here is..."
                ]
            },
            'society': {
                'hooks': [
                    "The conversation that made me question everything about {topic}",
                    "Why {topic} is the elephant in the room",
                    "The uncomfortable reality of {topic}",
                    "What we're not talking about when we talk about {topic}"
                ],
                'transitions': [
                    "But there's another layer to this...",
                    "What's really at stake here is...",
                    "This touches on something deeper...",
                    "The real question isn't...",
                    "Here's what's really happening..."
                ]
            }
        }
    
    def create_narrative_title(self, analysis: Dict[str, Any], original_title: str) -> str:
        """Create a compelling, narrative-style title."""
        primary_topic = analysis['primary_topic']
        controversial_topics = analysis['controversial_topics']
        
        # Use original title if it's good and specific
        if original_title and len(original_title) > 10 and original_title != "Untitled Conversation":
            # Clean up the title
            title = original_title.replace('ChatGPT - ', '').replace('ChatGPT:', '').strip()
            return title[:80]
        
        # Create narrative title based on topic
        if primary_topic in self.narrative_templates:
            templates = self.narrative_templates[primary_topic]['hooks']
        else:
            templates = self.narrative_templates['society']['hooks']
        
        # Use the first template and format it
        template = templates[0]
        if controversial_topics:
            topic = controversial_topics[0].title()
        else:
            topic = primary_topic.title()
        
        title = template.format(topic=topic)
        return title[:80]
    
    def create_narrative_dek(self, analysis: Dict[str, Any], conversation: NormalizedConversation) -> str:
        """Create an engaging dek that draws readers in."""
        key_questions = analysis['key_questions']
        controversial_topics = analysis['controversial_topics']
        
        if key_questions and len(key_questions) > 0:
            question = key_questions[0]
            if len(question) < 150:
                return f"A conversation that explores: {question}"
        
        if controversial_topics:
            return f"Exploring the complex realities of {', '.join(controversial_topics[:2])} and what they mean for us all."
        
        return "A thought-provoking conversation that challenges assumptions and opens new perspectives."
    
    def create_narrative_tldr(self, analysis: Dict[str, Any], conversation: NormalizedConversation) -> List[str]:
        """Create engaging TL;DR points that summarize key insights."""
        tldr = []
        
        # Extract key insights from the conversation
        key_insights = analysis['key_insights']
        practical_applications = analysis['practical_applications']
        controversial_topics = analysis['controversial_topics']
        
        # Create narrative-style TL;DR points
        if key_insights:
            for insight in key_insights[:2]:
                if len(insight) < 100:
                    tldr.append(insight)
        
        if practical_applications:
            for app in practical_applications[:1]:
                if len(app) < 100:
                    tldr.append(app)
        
        if controversial_topics:
            tldr.append(f"The discussion touches on sensitive topics like {', '.join(controversial_topics[:2])}")
        
        # Ensure we have at least 3 points
        while len(tldr) < 3:
            tldr.append("The conversation reveals important insights worth considering")
        
        return tldr[:5]
    
    def create_narrative_body(self, conversation: NormalizedConversation, analysis: Dict[str, Any]) -> str:
        """Create a narrative-style body that tells a story and provokes thought."""
        primary_topic = analysis['primary_topic']
        key_questions = analysis['key_questions']
        key_insights = analysis['key_insights']
        controversial_topics = analysis['controversial_topics']
        practical_applications = analysis['practical_applications']
        
        # Get the actual conversation content
        user_messages = [msg.text for msg in conversation.messages if msg.role == "user"]
        assistant_messages = [msg.text for msg in conversation.messages if msg.role == "assistant"]
        
        body_parts = []
        
        # Opening hook
        if key_questions and len(key_questions) > 0:
            hook = f"What if I told you that {key_questions[0].lower()}? This was the question that started a conversation that completely shifted my perspective on {primary_topic}."
        else:
            hook = f"Sometimes the most profound insights come from the most unexpected conversations. This discussion about {primary_topic} was one of those moments."
        
        body_parts.append(hook)
        body_parts.append("")
        
        # Add a compelling quote from the conversation
        pull_quote = self._extract_compelling_quote(conversation.messages)
        if pull_quote:
            body_parts.append(f"> {pull_quote}")
            body_parts.append("")
        
        # The conversation context
        body_parts.append("## The Conversation That Changed Everything")
        body_parts.append("")
        
        if user_messages and len(user_messages) > 0:
            # Extract the core question or concern from the user
            user_concern = self._extract_user_concern(user_messages[0])
            body_parts.append(f"The conversation began with a simple but profound question: {user_concern}")
            body_parts.append("")
        
        # The insights that emerged
        body_parts.append("## What We Discovered")
        body_parts.append("")
        
        if key_insights:
            for i, insight in enumerate(key_insights[:3], 1):
                body_parts.append(f"**{i}.** {insight}")
                body_parts.append("")
        
        # The deeper implications
        if controversial_topics:
            body_parts.append("## The Uncomfortable Truths")
            body_parts.append("")
            body_parts.append(f"This conversation didn't shy away from the difficult topics. We explored {', '.join(controversial_topics[:3])}, and what emerged was a nuanced understanding that challenges simple narratives.")
            body_parts.append("")
        
        # Practical implications
        if practical_applications:
            body_parts.append("## What This Means for Us")
            body_parts.append("")
            for app in practical_applications[:2]:
                body_parts.append(f"- {app}")
            body_parts.append("")
        
        # The questions that remain
        body_parts.append("## The Questions That Linger")
        body_parts.append("")
        body_parts.append("But perhaps the most valuable outcome of this conversation wasn't the answers we found, but the questions it raised:")
        body_parts.append("")
        
        if key_questions:
            for question in key_questions[:2]:
                body_parts.append(f"- {question}")
        else:
            body_parts.append("- What does this mean for how we approach similar challenges?")
            body_parts.append("- How do we balance competing priorities and values?")
        
        body_parts.append("")
        
        # Closing thought
        body_parts.append("## A Final Thought")
        body_parts.append("")
        body_parts.append("This conversation reminded me that the most important discussions aren't about finding the 'right' answer, but about asking the right questions. In a world that often demands certainty, there's something powerful about embracing complexity and nuance.")
        body_parts.append("")
        body_parts.append("What questions does this raise for you? What would you add to this conversation?")
        
        return '\n'.join(body_parts)
    
    def _extract_compelling_quote(self, messages: List[Any]) -> str:
        """Extract a compelling quote from the conversation."""
        for message in messages:
            if len(message.text) > 50 and len(message.text) < 200:
                # Look for sentences that would make good quotes
                sentences = message.text.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 30 and len(sentence) < 150:
                        # Check if it's a good quote
                        if any(indicator in sentence.lower() for indicator in ['think', 'believe', 'realize', 'understand', 'discover', 'learn', 'important', 'crucial', 'key', 'the thing is', 'what matters', 'the truth is']):
                            return sentence
        
        # Fallback to any substantial message
        for message in messages:
            if len(message.text) > 50 and len(message.text) < 200:
                return message.text
        
        return "This conversation provided valuable insights and practical guidance."
    
    def _extract_user_concern(self, user_message: str) -> str:
        """Extract the core concern or question from the user's message."""
        # Look for question patterns
        sentences = user_message.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if '?' in sentence and len(sentence) > 20:
                return sentence
        
        # Look for concern patterns
        concern_patterns = [
            r'I\'m confused about',
            r'I need to ask about',
            r'I think that',
            r'I believe that',
            r'I\'m not sure',
            r'I don\'t understand',
            r'What if',
            r'How do we',
            r'Why is it that'
        ]
        
        for pattern in concern_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                # Extract the sentence containing this pattern
                start = match.start()
                end = user_message.find('.', start)
                if end == -1:
                    end = len(user_message)
                return user_message[start:end].strip()
        
        # Fallback to first sentence
        first_sentence = sentences[0].strip()
        if len(first_sentence) > 20:
            return first_sentence
        
        return "a complex issue that deserves careful consideration"
    
    def create_narrative_tags(self, analysis: Dict[str, Any]) -> List[str]:
        """Create relevant tags for the narrative post."""
        tags = []
        
        # Add primary topic
        primary_topic = analysis['primary_topic']
        tags.append(primary_topic)
        
        # Add secondary topics
        for topic in analysis['secondary_topics'][:2]:
            tags.append(topic)
        
        # Add narrative-specific tags
        tags.append('conversation')
        tags.append('insights')
        
        # Add controversial topic tags
        if analysis['controversial_topics']:
            tags.append('thought-provoking')
        
        # Add depth-based tags
        depth = analysis['conversation_depth']
        if depth == 'deep':
            tags.append('deep-dive')
        elif depth == 'moderate':
            tags.append('analysis')
        
        return tags[:6]
    
    def create_narrative_further_reading(self, analysis: Dict[str, Any]) -> List[FurtherReading]:
        """Create further reading suggestions."""
        primary_topic = analysis['primary_topic']
        
        further_reading_map = {
            'education': [
                FurtherReading(title="The Future of Education", url="https://example.com/education-future"),
                FurtherReading(title="Teaching in the Digital Age", url="https://example.com/digital-teaching")
            ],
            'technology': [
                FurtherReading(title="AI and Society", url="https://example.com/ai-society"),
                FurtherReading(title="The Impact of Technology", url="https://example.com/tech-impact")
            ],
            'society': [
                FurtherReading(title="Social Issues Today", url="https://example.com/social-issues"),
                FurtherReading(title="Community and Society", url="https://example.com/community-society")
            ]
        }
        
        return further_reading_map.get(primary_topic, [])
    
    def summarize(self, conversation: NormalizedConversation) -> SubstackDraft:
        """Generate narrative-style Substack draft from conversation."""
        # Analyze the conversation
        analysis = self.analyzer.analyze_conversation(conversation)
        
        # Generate components
        title = self.create_narrative_title(analysis, conversation.title_hint)
        dek = self.create_narrative_dek(analysis, conversation)
        tldr = self.create_narrative_tldr(analysis, conversation)
        tags = self.create_narrative_tags(analysis)
        body_markdown = self.create_narrative_body(conversation, analysis)
        further_reading = self.create_narrative_further_reading(analysis)
        
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


def summarize_conversation_narrative(conversation: NormalizedConversation) -> SubstackDraft:
    """Narrative conversation summarization."""
    summarizer = NarrativeSummarizer()
    return summarizer.summarize(conversation)
