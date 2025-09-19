"""Specialized summarizer for research articles."""

import re
from typing import Dict, List, Any, Optional
from ..util.schema import NormalizedConversation, SubstackDraft, FurtherReading


class ResearchArticleSummarizer:
    """Specialized summarizer for research articles and analysis."""
    
    def __init__(self):
        pass
    
    def extract_research_context(self, conversation: NormalizedConversation) -> Dict[str, Any]:
        """Extract comprehensive research context from the conversation."""
        user_messages = [msg.text for msg in conversation.messages if msg.role == "user"]
        assistant_messages = [msg.text for msg in conversation.messages if msg.role == "assistant"]
        
        # Combine all text for analysis
        all_text = " ".join([msg.text for msg in conversation.messages])
        
        return {
            'research_topic': self._extract_research_topic(all_text),
            'research_question': self._extract_research_question(user_messages),
            'methodology': self._extract_methodology(assistant_messages),
            'key_findings': self._extract_key_findings(assistant_messages),
            'data_sources': self._extract_data_sources(all_text),
            'conclusions': self._extract_conclusions(assistant_messages),
            'implications': self._extract_implications(assistant_messages),
            'citations': self._extract_citations(all_text),
            'limitations': self._extract_limitations(assistant_messages)
        }
    
    def _extract_research_topic(self, text: str) -> str:
        """Extract the main research topic."""
        # Look for research topics
        topic_patterns = [
            r'research (on|about|into) ([^.!?]+)',
            r'study (of|on|about) ([^.!?]+)',
            r'analysis (of|on|about) ([^.!?]+)',
            r'investigation (into|of) ([^.!?]+)'
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(2).strip()
        
        # Fallback to first few words
        words = text.split()[:10]
        return " ".join(words)
    
    def _extract_research_question(self, user_messages: List[str]) -> str:
        """Extract the main research question."""
        for message in user_messages[:5]:
            if '?' in message and len(message) > 20:
                return self._clean_text(message)
        
        # Look for question indicators
        for message in user_messages:
            if any(word in message.lower() for word in ['what', 'how', 'why', 'when', 'where', 'which']):
                return self._clean_text(message)
        
        return "What are the key insights and implications of this topic?"
    
    def _extract_methodology(self, assistant_messages: List[str]) -> List[str]:
        """Extract research methodology."""
        methodology = []
        
        for message in assistant_messages:
            if len(message) > 100:
                # Look for methodology indicators
                method_indicators = [
                    'method', 'approach', 'technique', 'strategy', 'process',
                    'analysis', 'evaluation', 'assessment', 'investigation'
                ]
                if any(indicator in message.lower() for indicator in method_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in method_indicators):
                            cleaned = self._clean_text(sentence)
                            if len(cleaned) > 20:
                                methodology.append(cleaned)
        
        return methodology[:5]
    
    def _extract_key_findings(self, assistant_messages: List[str]) -> List[str]:
        """Extract key research findings."""
        findings = []
        
        for message in assistant_messages:
            if len(message) > 50:
                # Look for finding indicators
                finding_indicators = [
                    'finding', 'result', 'discovery', 'insight', 'conclusion',
                    'shows', 'indicates', 'suggests', 'reveals', 'demonstrates'
                ]
                if any(indicator in message.lower() for indicator in finding_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in finding_indicators):
                            cleaned = self._clean_text(sentence)
                            if len(cleaned) > 20:
                                findings.append(cleaned)
        
        return findings[:8]
    
    def _extract_data_sources(self, text: str) -> List[str]:
        """Extract data sources mentioned."""
        sources = []
        
        # Look for source indicators
        source_patterns = [
            r'according to ([^.!?]+)',
            r'([^.!?]+) (shows|indicates|suggests)',
            r'([^.!?]+) (study|research|analysis)',
            r'([^.!?]+) (report|paper|article)'
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) > 5:
                    sources.append(match.strip())
        
        return sources[:5]
    
    def _extract_conclusions(self, assistant_messages: List[str]) -> List[str]:
        """Extract research conclusions."""
        conclusions = []
        
        for message in assistant_messages:
            if len(message) > 100:
                # Look for conclusion indicators
                conclusion_indicators = [
                    'conclusion', 'summary', 'overall', 'in summary', 'to conclude',
                    'the main point', 'key takeaway', 'bottom line'
                ]
                if any(indicator in message.lower() for indicator in conclusion_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in conclusion_indicators):
                            cleaned = self._clean_text(sentence)
                            if len(cleaned) > 20:
                                conclusions.append(cleaned)
        
        return conclusions[:5]
    
    def _extract_implications(self, assistant_messages: List[str]) -> List[str]:
        """Extract implications of the research."""
        implications = []
        
        for message in assistant_messages:
            if len(message) > 100:
                # Look for implication indicators
                implication_indicators = [
                    'implication', 'impact', 'significance', 'importance',
                    'means that', 'suggests that', 'indicates that'
                ]
                if any(indicator in message.lower() for indicator in implication_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in implication_indicators):
                            cleaned = self._clean_text(sentence)
                            if len(cleaned) > 20:
                                implications.append(cleaned)
        
        return implications[:5]
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract citations and references."""
        citations = []
        
        # Look for citation patterns
        citation_patterns = [
            r'\([^)]+\d{4}[^)]*\)',  # (Author, 2024)
            r'\[[^\]]+\d{4}[^\]]*\]',  # [Author, 2024]
            r'[A-Z][a-z]+ \d{4}',  # Author 2024
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) > 5:
                    citations.append(match.strip())
        
        return citations[:5]
    
    def _extract_limitations(self, assistant_messages: List[str]) -> List[str]:
        """Extract research limitations."""
        limitations = []
        
        for message in assistant_messages:
            if len(message) > 100:
                # Look for limitation indicators
                limitation_indicators = [
                    'limitation', 'constraint', 'challenge', 'difficulty',
                    'however', 'but', 'although', 'despite'
                ]
                if any(indicator in message.lower() for indicator in limitation_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in limitation_indicators):
                            cleaned = self._clean_text(sentence)
                            if len(cleaned) > 20:
                                limitations.append(cleaned)
        
        return limitations[:5]
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common prefixes
        text = re.sub(r'^(i think|i believe|i feel|i know|i understand|i realized|i learned)\s+', '', text, flags=re.IGNORECASE)
        # Remove trailing punctuation
        text = re.sub(r'[.!?]+$', '', text)
        return text.strip()
    
    def create_title(self, conversation: NormalizedConversation, context: Dict[str, Any]) -> str:
        """Create a professional research article title."""
        topic = context['research_topic']
        
        if conversation.title_hint and conversation.title_hint != "Untitled Conversation":
            return conversation.title_hint.replace('ChatGPT - ', '').strip()
        
        return f"Research Analysis: {topic}"
    
    def create_dek(self, context: Dict[str, Any]) -> str:
        """Create a professional dek."""
        topic = context['research_topic']
        if len(topic) > 50:
            topic = topic[:50] + "..."
        return f"A comprehensive analysis of {topic}, examining key findings and implications."
    
    def create_tldr(self, context: Dict[str, Any]) -> List[str]:
        """Create professional TL;DR points."""
        tldr = []
        
        # Research question
        if context['research_question']:
            tldr.append(f"**Research Question:** {context['research_question'][:100]}...")
        
        # Key findings
        if context['key_findings']:
            tldr.append(f"**Key Finding:** {context['key_findings'][0][:100]}...")
        
        # Methodology
        if context['methodology']:
            tldr.append(f"**Methodology:** {context['methodology'][0][:100]}...")
        
        # Implications
        if context['implications']:
            tldr.append(f"**Implications:** {context['implications'][0][:100]}...")
        
        return tldr[:5]
    
    def create_body(self, conversation: NormalizedConversation, context: Dict[str, Any]) -> str:
        """Create a comprehensive research article body."""
        body_parts = []
        
        # Introduction
        body_parts.append("## Introduction")
        body_parts.append("")
        body_parts.append(f"This analysis examines {context['research_topic']}, addressing the key question: {context['research_question']}")
        body_parts.append("")
        body_parts.append("The research provides valuable insights into this important topic and its implications for current understanding and future developments.")
        body_parts.append("")
        
        # Methodology
        if context['methodology']:
            body_parts.append("## Methodology")
            body_parts.append("")
            body_parts.append("The analysis employed several key approaches:")
            body_parts.append("")
            for i, method in enumerate(context['methodology'], 1):
                body_parts.append(f"{i}. {method}")
            body_parts.append("")
        
        # Key Findings
        if context['key_findings']:
            body_parts.append("## Key Findings")
            body_parts.append("")
            body_parts.append("The research revealed several important findings:")
            body_parts.append("")
            for i, finding in enumerate(context['key_findings'], 1):
                body_parts.append(f"{i}. {finding}")
            body_parts.append("")
        
        # Data Sources
        if context['data_sources']:
            body_parts.append("## Data Sources")
            body_parts.append("")
            body_parts.append("The analysis drew from multiple sources:")
            body_parts.append("")
            for source in context['data_sources']:
                body_parts.append(f"- {source}")
            body_parts.append("")
        
        # Implications
        if context['implications']:
            body_parts.append("## Implications")
            body_parts.append("")
            body_parts.append("These findings have several important implications:")
            body_parts.append("")
            for implication in context['implications']:
                body_parts.append(f"- {implication}")
            body_parts.append("")
        
        # Limitations
        if context['limitations']:
            body_parts.append("## Limitations")
            body_parts.append("")
            body_parts.append("It's important to note several limitations:")
            body_parts.append("")
            for limitation in context['limitations']:
                body_parts.append(f"- {limitation}")
            body_parts.append("")
        
        # Conclusions
        body_parts.append("## Conclusions")
        body_parts.append("")
        body_parts.append("This analysis provides valuable insights into the topic and its implications. The findings contribute to our understanding and suggest important directions for future research.")
        body_parts.append("")
        
        # Citations
        if context['citations']:
            body_parts.append("## References")
            body_parts.append("")
            for citation in context['citations']:
                body_parts.append(f"- {citation}")
            body_parts.append("")
        
        return '\n'.join(body_parts)
    
    def create_tags(self, context: Dict[str, Any]) -> List[str]:
        """Create relevant tags."""
        tags = ['research', 'analysis', 'insights', 'findings']
        
        # Add topic-specific tags
        if context['research_topic']:
            topic_words = context['research_topic'].lower().split()
            tags.extend(topic_words[:3])
        
        return tags[:6]
    
    def summarize(self, conversation: NormalizedConversation) -> SubstackDraft:
        """Generate comprehensive research article."""
        # Extract comprehensive research context
        context = self.extract_research_context(conversation)
        
        # Generate components
        title = self.create_title(conversation, context)
        dek = self.create_dek(context)
        tldr = self.create_tldr(context)
        tags = self.create_tags(context)
        body_markdown = self.create_body(conversation, context)
        further_reading = [
            FurtherReading(title="Research Methodology Best Practices", url="https://example.com/research-methods"),
            FurtherReading(title="Academic Writing Guidelines", url="https://example.com/academic-writing")
        ]
        
        # Ensure word count is within limits
        word_count = len(body_markdown.split())
        if word_count > 900:
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


def summarize_conversation_research_article(conversation: NormalizedConversation) -> SubstackDraft:
    """Generate research article with full conversation context."""
    summarizer = ResearchArticleSummarizer()
    return summarizer.summarize(conversation)
