"""Specialized summarizers for different post types with full conversation context."""

import re
from typing import Dict, List, Any, Optional
from ..util.schema import NormalizedConversation, SubstackDraft, FurtherReading
from .enhanced_summarizer import ConversationAnalyzer


class TechnicalJournalSummarizer:
    """Specialized summarizer for technical journal entries about project development."""
    
    def __init__(self):
        self.analyzer = ConversationAnalyzer()
    
    def extract_project_context(self, conversation: NormalizedConversation) -> Dict[str, Any]:
        """Extract comprehensive project context from the full conversation."""
        user_messages = [msg.text for msg in conversation.messages if msg.role == "user"]
        assistant_messages = [msg.text for msg in conversation.messages if msg.role == "assistant"]
        
        # Combine all text for analysis
        all_text = " ".join([msg.text for msg in conversation.messages])
        
        return {
            'project_name': self._extract_project_name(all_text),
            'problem_statement': self._extract_problem_statement(user_messages),
            'solution_approach': self._extract_solution_approach(assistant_messages),
            'implementation_steps': self._extract_implementation_steps(assistant_messages),
            'technical_stack': self._extract_technical_stack(all_text),
            'challenges': self._extract_challenges(assistant_messages),
            'results': self._extract_results(assistant_messages),
            'lessons_learned': self._extract_lessons_learned(assistant_messages),
            'code_snippets': self._extract_code_snippets(all_text),
            'tools_used': self._extract_tools_used(all_text),
            'architecture_decisions': self._extract_architecture_decisions(assistant_messages)
        }
    
    def _extract_project_name(self, text: str) -> str:
        """Extract the project name from the conversation."""
        # Look for project names
        project_patterns = [
            r'sentry',
            r'testsentry',
            r'docsentry',
            r'litellm',
            r'ollama'
        ]
        
        for pattern in project_patterns:
            if pattern in text.lower():
                return pattern.title()
        
        return "Technical Project"
    
    def _extract_problem_statement(self, user_messages: List[str]) -> str:
        """Extract the core problem being solved."""
        # Look for the initial problem statement
        for message in user_messages[:5]:  # Check first few messages
            if len(message) > 50:
                # Look for problem indicators
                problem_indicators = [
                    'need to', 'want to', 'trying to', 'looking for', 'problem', 'issue', 
                    'challenge', 'considering', 'thinking about', 'working on'
                ]
                if any(indicator in message.lower() for indicator in problem_indicators):
                    return self._clean_text(message)
        
        # Fallback to first substantial message
        if user_messages:
            return self._clean_text(user_messages[0][:300])
        
        return "A technical challenge that required a solution"
    
    def _extract_solution_approach(self, assistant_messages: List[str]) -> str:
        """Extract the solution approach."""
        for message in assistant_messages:
            if len(message) > 100:
                # Look for solution indicators
                solution_indicators = [
                    'solution', 'approach', 'method', 'strategy', 'way to', 'technique',
                    'recommend', 'suggest', 'propose', 'implement', 'setup', 'configure'
                ]
                if any(indicator in message.lower() for indicator in solution_indicators):
                    return self._clean_text(message)
        
        return "A systematic approach to solving the problem"
    
    def _extract_implementation_steps(self, assistant_messages: List[str]) -> List[str]:
        """Extract implementation steps from the conversation."""
        steps = []
        
        for message in assistant_messages:
            if len(message) > 50:
                # Look for numbered steps
                if re.match(r'^\d+\.', message.strip()):
                    steps.append(self._clean_text(message.strip()))
                
                # Look for command sequences
                if '```' in message or 'bash' in message or 'pip' in message:
                    # Extract code blocks
                    code_blocks = re.findall(r'```(?:bash)?\n(.*?)\n```', message, re.DOTALL)
                    for block in code_blocks:
                        if len(block.strip()) > 10:
                            steps.append(f"Command: {block.strip()}")
                
                # Look for specific commands
                commands = re.findall(r'(pip|npm|git|curl|ollama|litellm)\s+[^\n]+', message)
                for cmd in commands:
                    if len(cmd) > 10:
                        steps.append(f"Command: {cmd}")
        
        return steps[:10]  # Limit to 10 steps
    
    def _extract_technical_stack(self, text: str) -> List[str]:
        """Extract the technical stack used."""
        stack = []
        
        # Look for technologies mentioned
        technologies = [
            'python', 'ollama', 'litellm', 'github', 'docker', 'bash', 'yaml',
            'llama', 'deepseek', 'qwen', 'mistral', 'codestral', 'pytest',
            'git', 'github actions', 'macos', 'm1', 'rtx', 'vram'
        ]
        
        for tech in technologies:
            if tech in text.lower():
                stack.append(tech.title())
        
        return list(set(stack))[:8]  # Remove duplicates and limit
    
    def _extract_challenges(self, assistant_messages: List[str]) -> List[str]:
        """Extract challenges encountered."""
        challenges = []
        
        for message in assistant_messages:
            challenge_indicators = [
                'challenge', 'problem', 'issue', 'difficult', 'trouble', 'error', 
                'bug', 'obstacle', 'timeout', 'memory', 'performance', 'dns'
            ]
            if any(indicator in message.lower() for indicator in challenge_indicators):
                sentences = message.split('.')
                for sentence in sentences:
                    if any(indicator in sentence.lower() for indicator in challenge_indicators):
                        cleaned = self._clean_text(sentence)
                        if len(cleaned) > 20:
                            challenges.append(cleaned)
        
        return challenges[:5]
    
    def _extract_results(self, assistant_messages: List[str]) -> str:
        """Extract the results achieved."""
        for message in assistant_messages:
            result_indicators = [
                'success', 'working', 'completed', 'finished', 'achieved', 'done',
                'resolved', 'fixed', 'implemented', 'deployed', 'running'
            ]
            if any(indicator in message.lower() for indicator in result_indicators):
                sentences = message.split('.')
                for sentence in sentences:
                    if any(indicator in sentence.lower() for indicator in result_indicators):
                        return self._clean_text(sentence)
        
        return "The project was successfully implemented and is working as expected"
    
    def _extract_lessons_learned(self, assistant_messages: List[str]) -> List[str]:
        """Extract lessons learned."""
        lessons = []
        
        for message in assistant_messages:
            lesson_indicators = [
                'learned', 'realized', 'discovered', 'found out', 'understood',
                'important', 'key insight', 'takeaway', 'lesson'
            ]
            if any(indicator in message.lower() for indicator in lesson_indicators):
                sentences = message.split('.')
                for sentence in sentences:
                    if any(indicator in sentence.lower() for indicator in lesson_indicators):
                        cleaned = self._clean_text(sentence)
                        if len(cleaned) > 20:
                            lessons.append(cleaned)
        
        return lessons[:5]
    
    def _extract_code_snippets(self, text: str) -> List[str]:
        """Extract code snippets from the conversation."""
        snippets = []
        
        # Extract code blocks
        code_blocks = re.findall(r'```(?:python|bash|yaml|json)?\n(.*?)\n```', text, re.DOTALL)
        for block in code_blocks:
            if len(block.strip()) > 10:
                snippets.append(block.strip())
        
        # Extract inline code
        inline_code = re.findall(r'`([^`]+)`', text)
        for code in inline_code:
            if len(code) > 5 and len(code) < 100:
                snippets.append(code)
        
        return snippets[:5]
    
    def _extract_tools_used(self, text: str) -> List[str]:
        """Extract tools and utilities used."""
        tools = []
        
        tool_patterns = [
            r'ollama', r'litellm', r'github', r'cursor', r'pytest', r'git',
            r'docker', r'homebrew', r'pipx', r'curl', r'jq', r'make'
        ]
        
        for pattern in tool_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                tools.append(pattern.title())
        
        return list(set(tools))
    
    def _extract_architecture_decisions(self, assistant_messages: List[str]) -> List[str]:
        """Extract architecture decisions made."""
        decisions = []
        
        for message in assistant_messages:
            if len(message) > 100:
                # Look for decision indicators
                decision_indicators = [
                    'decided to', 'chose to', 'opted for', 'went with', 'selected',
                    'architecture', 'design', 'structure', 'approach'
                ]
                if any(indicator in message.lower() for indicator in decision_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in decision_indicators):
                            cleaned = self._clean_text(sentence)
                            if len(cleaned) > 30:
                                decisions.append(cleaned)
        
        return decisions[:5]
    
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
        """Create a professional title."""
        project_name = context['project_name']
        
        if project_name == "Sentry":
            return "Building Sentry: A Local LLM-Powered Test and Documentation Automation System"
        elif project_name == "Litellm":
            return "Implementing LiteLLM: A Local AI Model Orchestration Solution"
        elif project_name == "Ollama":
            return "Setting Up Ollama: Local AI Model Management and Integration"
        else:
            return f"Building {project_name}: A Technical Development Journey"
    
    def create_dek(self, context: Dict[str, Any]) -> str:
        """Create a professional dek."""
        problem = context['problem_statement']
        if len(problem) > 200:
            problem = problem[:200] + "..."
        
        return f"A comprehensive look at developing a local AI-powered automation system, including the challenges faced, solutions implemented, and lessons learned along the way."
    
    def create_tldr(self, context: Dict[str, Any]) -> List[str]:
        """Create professional TL;DR points."""
        tldr = []
        
        # Problem
        if context['problem_statement']:
            tldr.append(f"**Problem:** {context['problem_statement'][:100]}...")
        
        # Solution
        if context['solution_approach']:
            tldr.append(f"**Solution:** {context['solution_approach'][:100]}...")
        
        # Tech stack
        if context['technical_stack']:
            tldr.append(f"**Tech Stack:** {', '.join(context['technical_stack'][:3])}")
        
        # Key result
        if context['results']:
            tldr.append(f"**Outcome:** {context['results'][:100]}...")
        
        return tldr[:5]
    
    def create_body(self, conversation: NormalizedConversation, context: Dict[str, Any]) -> str:
        """Create a comprehensive technical journal body."""
        body_parts = []
        
        # Introduction
        body_parts.append("## The Challenge")
        body_parts.append("")
        body_parts.append(f"Recently, I embarked on building {context['project_name']}, a project that emerged from a specific need: {context['problem_statement']}")
        body_parts.append("")
        body_parts.append("This wasn't just a simple script or tool—it was a comprehensive system that required careful planning, multiple technology integrations, and iterative problem-solving.")
        body_parts.append("")
        
        # Solution approach
        body_parts.append("## The Approach")
        body_parts.append("")
        body_parts.append(f"After analyzing the requirements, I decided to {context['solution_approach'].lower()}")
        body_parts.append("")
        body_parts.append("This approach was chosen because it provided the best balance of performance, maintainability, and scalability for the specific use case.")
        body_parts.append("")
        
        # Technical stack
        if context['technical_stack']:
            body_parts.append("## Technical Stack")
            body_parts.append("")
            body_parts.append("The project utilized several key technologies:")
            body_parts.append("")
            for tech in context['technical_stack']:
                body_parts.append(f"- **{tech}**: [Brief description of how it was used]")
            body_parts.append("")
        
        # Implementation details
        if context['implementation_steps']:
            body_parts.append("## Implementation Process")
            body_parts.append("")
            body_parts.append("The implementation involved several key steps:")
            body_parts.append("")
            for i, step in enumerate(context['implementation_steps'][:8], 1):
                body_parts.append(f"**Step {i}:** {step}")
                body_parts.append("")
        
        # Architecture decisions
        if context['architecture_decisions']:
            body_parts.append("## Key Architecture Decisions")
            body_parts.append("")
            body_parts.append("Several important architectural decisions were made during development:")
            body_parts.append("")
            for decision in context['architecture_decisions']:
                body_parts.append(f"- {decision}")
            body_parts.append("")
        
        # Challenges
        if context['challenges']:
            body_parts.append("## Challenges and Solutions")
            body_parts.append("")
            body_parts.append("As with any complex technical project, several challenges emerged:")
            body_parts.append("")
            for challenge in context['challenges']:
                body_parts.append(f"- {challenge}")
            body_parts.append("")
        
        # Results
        body_parts.append("## Results and Impact")
        body_parts.append("")
        body_parts.append(f"The final outcome exceeded expectations: {context['results']}")
        body_parts.append("")
        body_parts.append("The solution not only addressed the original problem but also provided additional benefits in terms of performance, maintainability, and extensibility.")
        body_parts.append("")
        
        # Lessons learned
        if context['lessons_learned']:
            body_parts.append("## Key Takeaways")
            body_parts.append("")
            body_parts.append("This project provided several valuable insights:")
            body_parts.append("")
            for lesson in context['lessons_learned']:
                body_parts.append(f"- {lesson}")
            body_parts.append("")
        
        # Code examples
        if context['code_snippets']:
            body_parts.append("## Code Examples")
            body_parts.append("")
            body_parts.append("Here are some key code snippets from the implementation:")
            body_parts.append("")
            for i, snippet in enumerate(context['code_snippets'][:3], 1):
                body_parts.append(f"**Example {i}:**")
                body_parts.append("```")
                body_parts.append(snippet)
                body_parts.append("```")
                body_parts.append("")
        
        # Conclusion
        body_parts.append("## Conclusion")
        body_parts.append("")
        body_parts.append("This project demonstrates the importance of systematic problem-solving, careful technology selection, and iterative development. The challenges encountered along the way provided valuable learning opportunities and ultimately led to a more robust solution.")
        body_parts.append("")
        body_parts.append("For those facing similar technical challenges, I'd recommend starting with a clear understanding of the requirements, choosing the right tools for the job, and being prepared to iterate and refine the solution as you learn more about the problem space.")
        body_parts.append("")
        body_parts.append("The journey from initial concept to working system was both challenging and rewarding, and the lessons learned will undoubtedly inform future projects.")
        
        return '\n'.join(body_parts)
    
    def create_tags(self, context: Dict[str, Any]) -> List[str]:
        """Create relevant tags."""
        tags = ['technical', 'development', 'project', 'automation', 'ai']
        
        # Add technology-specific tags
        if context['technical_stack']:
            tags.extend([tech.lower() for tech in context['technical_stack'][:3]])
        
        # Add project-specific tags
        if context['project_name']:
            tags.append(context['project_name'].lower())
        
        return tags[:6]
    
    def summarize(self, conversation: NormalizedConversation) -> SubstackDraft:
        """Generate comprehensive technical journal entry."""
        # Extract comprehensive project context
        context = self.extract_project_context(conversation)
        
        # Generate components
        title = self.create_title(conversation, context)
        dek = self.create_dek(context)
        tldr = self.create_tldr(context)
        tags = self.create_tags(context)
        body_markdown = self.create_body(conversation, context)
        further_reading = [
            FurtherReading(title="Local AI Development Best Practices", url="https://example.com/local-ai-dev"),
            FurtherReading(title="Technical Writing for Developers", url="https://example.com/tech-writing-dev")
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


def summarize_conversation_technical_journal(conversation: NormalizedConversation) -> SubstackDraft:
    """Generate technical journal entry with full conversation context."""
    summarizer = TechnicalJournalSummarizer()
    return summarizer.summarize(conversation)
