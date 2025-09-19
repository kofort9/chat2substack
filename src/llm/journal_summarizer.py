"""Journal entry style summarization for project discussions and development stories."""

import re
from typing import Dict, List, Any, Optional
from ..util.schema import NormalizedConversation, SubstackDraft, FurtherReading
from .enhanced_summarizer import ConversationAnalyzer


class JournalSummarizer:
    """Creates journal entry style posts that tell the story of project development."""
    
    def __init__(self):
        self.analyzer = ConversationAnalyzer()
        self.project_indicators = [
            'project', 'build', 'built', 'created', 'developed', 'implemented',
            'working on', 'building', 'made', 'designed', 'coded', 'programmed',
            'prototype', 'demo', 'version', 'feature', 'functionality', 'system',
            'app', 'tool', 'script', 'library', 'framework', 'platform'
        ]
        self.technical_indicators = [
            'code', 'function', 'method', 'class', 'variable', 'algorithm',
            'api', 'database', 'server', 'client', 'frontend', 'backend',
            'deployment', 'testing', 'debugging', 'optimization', 'performance'
        ]
    
    def detect_project_type(self, conversation: NormalizedConversation) -> str:
        """Detect what type of project is being discussed."""
        all_text = " ".join([msg.text for msg in conversation.messages])
        text_lower = all_text.lower()
        
        # Look for specific project types
        if any(word in text_lower for word in ['ai', 'machine learning', 'ml', 'neural', 'model', 'training']):
            return 'ai_project'
        elif any(word in text_lower for word in ['web', 'website', 'app', 'frontend', 'backend', 'api']):
            return 'web_project'
        elif any(word in text_lower for word in ['mobile', 'ios', 'android', 'app store']):
            return 'mobile_project'
        elif any(word in text_lower for word in ['tool', 'utility', 'script', 'automation']):
            return 'tool_project'
        elif any(word in text_lower for word in ['research', 'study', 'experiment', 'analysis']):
            return 'research_project'
        else:
            return 'general_project'
    
    def extract_project_story(self, conversation: NormalizedConversation) -> Dict[str, Any]:
        """Extract the story elements of the project development."""
        user_messages = [msg.text for msg in conversation.messages if msg.role == "user"]
        assistant_messages = [msg.text for msg in conversation.messages if msg.role == "assistant"]
        
        story = {
            'problem': self._extract_problem_statement(user_messages),
            'approach': self._extract_approach(assistant_messages),
            'implementation': self._extract_implementation_details(assistant_messages),
            'results': self._extract_results(assistant_messages),
            'challenges': self._extract_challenges(assistant_messages),
            'next_steps': self._extract_next_steps(assistant_messages),
            'technical_details': self._extract_technical_details(assistant_messages)
        }
        
        return story
    
    def _extract_problem_statement(self, user_messages: List[str]) -> str:
        """Extract the problem or challenge being addressed."""
        for message in user_messages:
            # Look for problem indicators
            if any(indicator in message.lower() for indicator in ['problem', 'issue', 'challenge', 'need', 'want', 'trying to', 'looking for']):
                # Extract the sentence containing the problem
                sentences = message.split('.')
                for sentence in sentences:
                    if any(indicator in sentence.lower() for indicator in ['problem', 'issue', 'challenge', 'need', 'want', 'trying to', 'looking for']):
                        return sentence.strip()
        
        # Fallback to first substantial message
        if user_messages:
            first_message = user_messages[0]
            sentences = first_message.split('.')
            if sentences:
                return sentences[0].strip()
        
        return "A technical challenge that needed solving"
    
    def _extract_approach(self, assistant_messages: List[str]) -> str:
        """Extract the approach or methodology used."""
        for message in assistant_messages:
            if len(message) > 100:  # Substantial message
                # Look for approach indicators
                if any(indicator in message.lower() for indicator in ['approach', 'method', 'strategy', 'way to', 'solution', 'technique']):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in ['approach', 'method', 'strategy', 'way to', 'solution', 'technique']):
                            return sentence.strip()
        
        return "A systematic approach to solving the problem"
    
    def _extract_implementation_details(self, assistant_messages: List[str]) -> List[str]:
        """Extract specific implementation details."""
        details = []
        for message in assistant_messages:
            if len(message) > 50:
                # Look for code snippets, commands, or technical details
                if any(indicator in message for indicator in ['`', '```', 'pip', 'npm', 'git', 'curl', 'python', 'javascript', 'sql']):
                    # Extract code-like content
                    code_pattern = r'`([^`]+)`'
                    matches = re.findall(code_pattern, message)
                    for match in matches:
                        if len(match) > 5 and len(match) < 100:
                            details.append(match)
                
                # Look for numbered lists or steps
                if re.match(r'^\d+\.', message.strip()):
                    details.append(message.strip())
        
        return details[:5]  # Limit to 5 details
    
    def _extract_results(self, assistant_messages: List[str]) -> str:
        """Extract the results or outcomes."""
        for message in assistant_messages:
            if any(indicator in message.lower() for indicator in ['result', 'outcome', 'success', 'working', 'completed', 'finished', 'done']):
                sentences = message.split('.')
                for sentence in sentences:
                    if any(indicator in sentence.lower() for indicator in ['result', 'outcome', 'success', 'working', 'completed', 'finished', 'done']):
                        return sentence.strip()
        
        return "The project was successfully implemented"
    
    def _extract_challenges(self, assistant_messages: List[str]) -> List[str]:
        """Extract challenges or obstacles encountered."""
        challenges = []
        for message in assistant_messages:
            if any(indicator in message.lower() for indicator in ['challenge', 'problem', 'issue', 'difficult', 'trouble', 'error', 'bug']):
                sentences = message.split('.')
                for sentence in sentences:
                    if any(indicator in sentence.lower() for indicator in ['challenge', 'problem', 'issue', 'difficult', 'trouble', 'error', 'bug']):
                        if len(sentence.strip()) > 20:
                            challenges.append(sentence.strip())
        
        return challenges[:3]  # Limit to 3 challenges
    
    def _extract_next_steps(self, assistant_messages: List[str]) -> List[str]:
        """Extract next steps or future plans."""
        next_steps = []
        for message in assistant_messages:
            if any(indicator in message.lower() for indicator in ['next', 'future', 'plan', 'improve', 'enhance', 'add', 'implement']):
                sentences = message.split('.')
                for sentence in sentences:
                    if any(indicator in sentence.lower() for indicator in ['next', 'future', 'plan', 'improve', 'enhance', 'add', 'implement']):
                        if len(sentence.strip()) > 20:
                            next_steps.append(sentence.strip())
        
        return next_steps[:3]  # Limit to 3 next steps
    
    def _extract_technical_details(self, assistant_messages: List[str]) -> List[str]:
        """Extract technical details and specifications."""
        details = []
        for message in assistant_messages:
            if len(message) > 50:
                # Look for technical specifications
                if any(indicator in message.lower() for indicator in ['version', 'library', 'framework', 'language', 'database', 'server', 'api']):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in ['version', 'library', 'framework', 'language', 'database', 'server', 'api']):
                            if len(sentence.strip()) > 20:
                                details.append(sentence.strip())
        
        return details[:3]  # Limit to 3 details
    
    def create_journal_title(self, conversation: NormalizedConversation, project_story: Dict[str, Any]) -> str:
        """Create a journal-style title."""
        # Use the conversation title if it's descriptive
        if conversation.title_hint and conversation.title_hint != "Untitled Conversation":
            title = conversation.title_hint.replace('ChatGPT - ', '').replace('ChatGPT:', '').strip()
            if len(title) > 10:
                return title
        
        # Create title based on project type and problem
        problem = project_story['problem']
        if 'sentry' in problem.lower():
            return "Building a Sentry Integration: A Development Journal"
        elif 'ai' in problem.lower() or 'machine learning' in problem.lower():
            return "Developing an AI Solution: A Technical Journey"
        elif 'web' in problem.lower() or 'app' in problem.lower():
            return "Creating a Web Application: Development Notes"
        else:
            return "Project Development: A Technical Journal"
    
    def create_journal_dek(self, project_story: Dict[str, Any]) -> str:
        """Create a journal-style dek."""
        problem = project_story['problem']
        if len(problem) > 100:
            problem = problem[:100] + "..."
        
        return f"A journal entry documenting the development process: {problem}"
    
    def create_journal_tldr(self, project_story: Dict[str, Any]) -> List[str]:
        """Create journal-style TL;DR points."""
        tldr = []
        
        # Problem statement
        if project_story['problem']:
            tldr.append(f"Problem: {project_story['problem']}")
        
        # Key implementation details
        if project_story['implementation']:
            tldr.append(f"Solution: {project_story['implementation'][0]}")
        
        # Results
        if project_story['results']:
            tldr.append(f"Outcome: {project_story['results']}")
        
        # Ensure we have at least 3 points
        while len(tldr) < 3:
            tldr.append("A technical project with interesting challenges and solutions")
        
        return tldr[:5]
    
    def create_journal_body(self, conversation: NormalizedConversation, project_story: Dict[str, Any]) -> str:
        """Create a journal entry style body."""
        body_parts = []
        
        # Journal entry header
        body_parts.append("## The Problem")
        body_parts.append("")
        body_parts.append(f"Today I found myself facing an interesting challenge: {project_story['problem']}")
        body_parts.append("")
        
        # The approach
        body_parts.append("## The Approach")
        body_parts.append("")
        body_parts.append(f"After thinking through the problem, I decided to {project_story['approach'].lower()}")
        body_parts.append("")
        
        # Implementation details
        if project_story['implementation']:
            body_parts.append("## Implementation Details")
            body_parts.append("")
            body_parts.append("Here's what I actually built:")
            body_parts.append("")
            for i, detail in enumerate(project_story['implementation'], 1):
                body_parts.append(f"**Step {i}:** {detail}")
                body_parts.append("")
        
        # Technical details
        if project_story['technical_details']:
            body_parts.append("## Technical Stack")
            body_parts.append("")
            for detail in project_story['technical_details']:
                body_parts.append(f"- {detail}")
            body_parts.append("")
        
        # Challenges encountered
        if project_story['challenges']:
            body_parts.append("## Challenges Along the Way")
            body_parts.append("")
            body_parts.append("Of course, no project goes smoothly. Here are the main challenges I encountered:")
            body_parts.append("")
            for challenge in project_story['challenges']:
                body_parts.append(f"- {challenge}")
            body_parts.append("")
        
        # Results
        body_parts.append("## The Results")
        body_parts.append("")
        body_parts.append(f"The end result? {project_story['results']}")
        body_parts.append("")
        
        # Next steps
        if project_story['next_steps']:
            body_parts.append("## What's Next")
            body_parts.append("")
            body_parts.append("This project opened up some interesting possibilities:")
            body_parts.append("")
            for step in project_story['next_steps']:
                body_parts.append(f"- {step}")
            body_parts.append("")
        
        # Reflection
        body_parts.append("## Reflection")
        body_parts.append("")
        body_parts.append("Looking back on this project, I'm struck by how much I learned in the process. The technical challenges were interesting, but the real value was in the problem-solving journey itself.")
        body_parts.append("")
        body_parts.append("What projects have you been working on lately? I'd love to hear about your own development stories and the challenges you've faced.")
        
        return '\n'.join(body_parts)
    
    def create_journal_tags(self, conversation: NormalizedConversation, project_story: Dict[str, Any]) -> List[str]:
        """Create relevant tags for the journal entry."""
        tags = []
        
        # Add project type
        project_type = self.detect_project_type(conversation)
        if project_type != 'general_project':
            tags.append(project_type.replace('_', '-'))
        
        # Add technical tags
        tags.extend(['development', 'project', 'journal'])
        
        # Add specific technology tags if found
        all_text = " ".join([msg.text for msg in conversation.messages])
        if 'python' in all_text.lower():
            tags.append('python')
        if 'javascript' in all_text.lower():
            tags.append('javascript')
        if 'ai' in all_text.lower() or 'machine learning' in all_text.lower():
            tags.append('ai')
        
        return tags[:6]
    
    def create_journal_further_reading(self, conversation: NormalizedConversation) -> List[FurtherReading]:
        """Create further reading suggestions."""
        return [
            FurtherReading(title="Development Best Practices", url="https://example.com/dev-practices"),
            FurtherReading(title="Project Management for Developers", url="https://example.com/project-management")
        ]
    
    def summarize(self, conversation: NormalizedConversation) -> SubstackDraft:
        """Generate journal entry style Substack draft from conversation."""
        # Analyze the conversation
        analysis = self.analyzer.analyze_conversation(conversation)
        
        # Extract project story
        project_story = self.extract_project_story(conversation)
        
        # Generate components
        title = self.create_journal_title(conversation, project_story)
        dek = self.create_journal_dek(project_story)
        tldr = self.create_journal_tldr(project_story)
        tags = self.create_journal_tags(conversation, project_story)
        body_markdown = self.create_journal_body(conversation, project_story)
        further_reading = self.create_journal_further_reading(conversation)
        
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


def summarize_conversation_journal(conversation: NormalizedConversation) -> SubstackDraft:
    """Journal entry conversation summarization."""
    summarizer = JournalSummarizer()
    return summarizer.summarize(conversation)
