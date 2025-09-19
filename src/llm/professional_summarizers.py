"""Professional summarizers for different content types."""

import re
from typing import Dict, List, Any, Optional
from ..util.schema import NormalizedConversation, SubstackDraft, FurtherReading
from .enhanced_summarizer import ConversationAnalyzer
from .category_detector import PostCategory
from .specialized_summarizers import summarize_conversation_technical_journal
from .research_article_summarizer import summarize_conversation_research_article
from .critique_summarizer import CritiqueSummarizer


class ProfessionalTechnicalJournalSummarizer:
    """Creates professional technical journal entries about project development."""
    
    def __init__(self):
        self.analyzer = ConversationAnalyzer()
    
    def extract_project_story(self, conversation: NormalizedConversation) -> Dict[str, Any]:
        """Extract the project development story."""
        user_messages = [msg.text for msg in conversation.messages if msg.role == "user"]
        assistant_messages = [msg.text for msg in conversation.messages if msg.role == "assistant"]
        
        return {
            'problem': self._extract_problem_statement(user_messages),
            'solution_approach': self._extract_solution_approach(assistant_messages),
            'implementation': self._extract_implementation_steps(assistant_messages),
            'technical_details': self._extract_technical_specs(assistant_messages),
            'challenges': self._extract_challenges(assistant_messages),
            'results': self._extract_results(assistant_messages),
            'lessons_learned': self._extract_lessons(assistant_messages)
        }
    
    def _extract_problem_statement(self, user_messages: List[str]) -> str:
        """Extract the core problem being solved."""
        for message in user_messages:
            # Look for problem indicators
            problem_indicators = ['need to', 'want to', 'trying to', 'looking for', 'problem', 'issue', 'challenge']
            if any(indicator in message.lower() for indicator in problem_indicators):
                # Clean up and return the problem statement
                sentences = message.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if any(indicator in sentence.lower() for indicator in problem_indicators):
                        return self._clean_text(sentence)
        
        # Fallback to first message
        if user_messages:
            return self._clean_text(user_messages[0][:200])
        
        return "A technical challenge that required a solution"
    
    def _extract_solution_approach(self, assistant_messages: List[str]) -> str:
        """Extract the solution approach."""
        for message in assistant_messages:
            if len(message) > 100:
                # Look for solution indicators
                solution_indicators = ['solution', 'approach', 'method', 'strategy', 'way to', 'technique']
                if any(indicator in message.lower() for indicator in solution_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in solution_indicators):
                            return self._clean_text(sentence)
        
        return "A systematic approach to solving the problem"
    
    def _extract_implementation_steps(self, assistant_messages: List[str]) -> List[str]:
        """Extract implementation steps."""
        steps = []
        for message in assistant_messages:
            if len(message) > 50:
                # Look for numbered steps
                if re.match(r'^\d+\.', message.strip()):
                    steps.append(self._clean_text(message.strip()))
                # Look for code blocks or commands
                elif '`' in message or 'pip' in message or 'npm' in message:
                    # Extract code-like content
                    code_pattern = r'`([^`]+)`'
                    matches = re.findall(code_pattern, message)
                    for match in matches:
                        if len(match) > 5 and len(match) < 100:
                            steps.append(match)
        
        return steps[:5]
    
    def _extract_technical_specs(self, assistant_messages: List[str]) -> List[str]:
        """Extract technical specifications."""
        specs = []
        for message in assistant_messages:
            if len(message) > 50:
                # Look for technical details
                tech_indicators = ['version', 'library', 'framework', 'language', 'database', 'server', 'api', 'config']
                if any(indicator in message.lower() for indicator in tech_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in tech_indicators):
                            cleaned = self._clean_text(sentence)
                            if len(cleaned) > 20:
                                specs.append(cleaned)
        
        return specs[:3]
    
    def _extract_challenges(self, assistant_messages: List[str]) -> List[str]:
        """Extract challenges encountered."""
        challenges = []
        for message in assistant_messages:
            challenge_indicators = ['challenge', 'problem', 'issue', 'difficult', 'trouble', 'error', 'bug', 'obstacle']
            if any(indicator in message.lower() for indicator in challenge_indicators):
                sentences = message.split('.')
                for sentence in sentences:
                    if any(indicator in sentence.lower() for indicator in challenge_indicators):
                        cleaned = self._clean_text(sentence)
                        if len(cleaned) > 20:
                            challenges.append(cleaned)
        
        return challenges[:3]
    
    def _extract_results(self, assistant_messages: List[str]) -> str:
        """Extract the results achieved."""
        for message in assistant_messages:
            result_indicators = ['result', 'outcome', 'success', 'working', 'completed', 'finished', 'achieved']
            if any(indicator in message.lower() for indicator in result_indicators):
                sentences = message.split('.')
                for sentence in sentences:
                    if any(indicator in sentence.lower() for indicator in result_indicators):
                        return self._clean_text(sentence)
        
        return "The project was successfully implemented and is working as expected"
    
    def _extract_lessons(self, assistant_messages: List[str]) -> List[str]:
        """Extract lessons learned."""
        lessons = []
        for message in assistant_messages:
            lesson_indicators = ['learned', 'realized', 'discovered', 'found out', 'understood']
            if any(indicator in message.lower() for indicator in lesson_indicators):
                sentences = message.split('.')
                for sentence in sentences:
                    if any(indicator in sentence.lower() for indicator in lesson_indicators):
                        cleaned = self._clean_text(sentence)
                        if len(cleaned) > 20:
                            lessons.append(cleaned)
        
        return lessons[:3]
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common prefixes
        text = re.sub(r'^(i think|i believe|i feel|i know|i understand|i realized|i learned)\s+', '', text, flags=re.IGNORECASE)
        # Remove trailing punctuation
        text = re.sub(r'[.!?]+$', '', text)
        return text.strip()
    
    def create_title(self, conversation: NormalizedConversation, project_story: Dict[str, Any]) -> str:
        """Create a professional title."""
        if conversation.title_hint and conversation.title_hint != "Untitled Conversation":
            title = conversation.title_hint.replace('ChatGPT - ', '').replace('ChatGPT:', '').strip()
            if len(title) > 10:
                return title
        
        # Create title based on project content
        problem = project_story['problem']
        if 'sentry' in problem.lower():
            return "Building a Sentry Integration: A Technical Deep Dive"
        elif 'ai' in problem.lower() or 'machine learning' in problem.lower():
            return "Developing an AI-Powered Solution: Technical Implementation"
        elif 'web' in problem.lower() or 'app' in problem.lower():
            return "Creating a Web Application: Development Process and Lessons"
        else:
            return "Technical Project Development: Implementation and Insights"
    
    def create_dek(self, project_story: Dict[str, Any]) -> str:
        """Create a professional dek."""
        problem = project_story['problem']
        if len(problem) > 150:
            problem = problem[:150] + "..."
        
        return f"An in-depth look at solving {problem} through technical implementation, including challenges faced and lessons learned."
    
    def create_tldr(self, project_story: Dict[str, Any]) -> List[str]:
        """Create professional TL;DR points."""
        tldr = []
        
        # Problem
        if project_story['problem']:
            tldr.append(f"**Problem:** {project_story['problem']}")
        
        # Solution
        if project_story['solution_approach']:
            tldr.append(f"**Solution:** {project_story['solution_approach']}")
        
        # Key result
        if project_story['results']:
            tldr.append(f"**Outcome:** {project_story['results']}")
        
        # Technical highlight
        if project_story['technical_details']:
            tldr.append(f"**Tech Stack:** {project_story['technical_details'][0]}")
        
        return tldr[:5]
    
    def create_body(self, conversation: NormalizedConversation, project_story: Dict[str, Any]) -> str:
        """Create a professional technical journal body."""
        body_parts = []
        
        # Introduction
        body_parts.append("## The Challenge")
        body_parts.append("")
        body_parts.append(f"Recently, I encountered a technical challenge: {project_story['problem']}")
        body_parts.append("")
        body_parts.append("This wasn't just a simple bug fix or feature request—it was a problem that required careful analysis and a systematic approach to solve effectively.")
        body_parts.append("")
        
        # Solution approach
        body_parts.append("## The Approach")
        body_parts.append("")
        body_parts.append(f"After analyzing the requirements, I decided to {project_story['solution_approach'].lower()}")
        body_parts.append("")
        body_parts.append("This approach was chosen because it provided the best balance of performance, maintainability, and scalability for the specific use case.")
        body_parts.append("")
        
        # Implementation details
        if project_story['implementation']:
            body_parts.append("## Implementation Details")
            body_parts.append("")
            body_parts.append("The implementation involved several key steps:")
            body_parts.append("")
            for i, step in enumerate(project_story['implementation'], 1):
                body_parts.append(f"**Step {i}:** {step}")
                body_parts.append("")
        
        # Technical specifications
        if project_story['technical_details']:
            body_parts.append("## Technical Specifications")
            body_parts.append("")
            body_parts.append("The technical stack and configuration included:")
            body_parts.append("")
            for spec in project_story['technical_details']:
                body_parts.append(f"- {spec}")
            body_parts.append("")
        
        # Challenges
        if project_story['challenges']:
            body_parts.append("## Challenges and Solutions")
            body_parts.append("")
            body_parts.append("As with any technical project, several challenges emerged during development:")
            body_parts.append("")
            for challenge in project_story['challenges']:
                body_parts.append(f"- {challenge}")
            body_parts.append("")
        
        # Results
        body_parts.append("## Results and Impact")
        body_parts.append("")
        body_parts.append(f"The final outcome exceeded expectations: {project_story['results']}")
        body_parts.append("")
        body_parts.append("The solution not only addressed the original problem but also provided additional benefits in terms of performance and maintainability.")
        body_parts.append("")
        
        # Lessons learned
        if project_story['lessons_learned']:
            body_parts.append("## Key Takeaways")
            body_parts.append("")
            body_parts.append("This project provided several valuable insights:")
            body_parts.append("")
            for lesson in project_story['lessons_learned']:
                body_parts.append(f"- {lesson}")
            body_parts.append("")
        
        # Conclusion
        body_parts.append("## Conclusion")
        body_parts.append("")
        body_parts.append("This project demonstrates the importance of systematic problem-solving and careful technical implementation. The challenges encountered along the way provided valuable learning opportunities and ultimately led to a more robust solution.")
        body_parts.append("")
        body_parts.append("For those facing similar technical challenges, I'd recommend starting with a clear understanding of the requirements, choosing the right tools for the job, and being prepared to iterate and refine the solution as you learn more about the problem space.")
        
        return '\n'.join(body_parts)
    
    def create_tags(self, conversation: NormalizedConversation) -> List[str]:
        """Create relevant tags."""
        tags = ['technical', 'development', 'project', 'implementation']
        
        # Add technology-specific tags
        all_text = " ".join([msg.text for msg in conversation.messages])
        if 'python' in all_text.lower():
            tags.append('python')
        if 'javascript' in all_text.lower():
            tags.append('javascript')
        if 'ai' in all_text.lower() or 'machine learning' in all_text.lower():
            tags.append('ai')
        if 'web' in all_text.lower():
            tags.append('web-development')
        
        return tags[:6]
    
    def summarize(self, conversation: NormalizedConversation) -> SubstackDraft:
        """Generate professional technical journal entry."""
        # Use the specialized technical journal summarizer
        return summarize_conversation_technical_journal(conversation)


class ProfessionalResearchArticleSummarizer:
    """Creates professional research articles."""
    
    def __init__(self):
        self.analyzer = ConversationAnalyzer()
    
    def summarize(self, conversation: NormalizedConversation) -> SubstackDraft:
        """Generate professional research article."""
        # Use the specialized research article summarizer
        return summarize_conversation_research_article(conversation)


class ProfessionalCritiqueSummarizer:
    """Creates professional critique articles."""
    
    def __init__(self):
        self.analyzer = ConversationAnalyzer()
    
    def summarize(self, conversation: NormalizedConversation) -> SubstackDraft:
        """Generate professional critique article."""
        # Use the specialized critique summarizer
        summarizer = CritiqueSummarizer()
        conversation_dict = {
            'messages': [{'role': msg.role, 'content': msg.text} for msg in conversation.messages],
            'title_hint': getattr(conversation, 'title_hint', 'Untitled Conversation')
        }
        return summarizer.summarize_conversation(conversation_dict)


def get_professional_summarizer(category: PostCategory):
    """Get the appropriate professional summarizer for the category."""
    summarizers = {
        "technical_journal": ProfessionalTechnicalJournalSummarizer(),
        "research_article": ProfessionalResearchArticleSummarizer(),
        "critique": ProfessionalCritiqueSummarizer()
    }
    return summarizers[category]


def summarize_conversation_professional(conversation: NormalizedConversation, category: PostCategory) -> SubstackDraft:
    """Generate professional content based on category."""
    summarizer = get_professional_summarizer(category)
    return summarizer.summarize(conversation)
