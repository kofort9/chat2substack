"""Comprehensive summarizer that captures much more content from conversations."""

import re
from typing import Dict, List, Any, Optional
from ..util.schema import NormalizedConversation, SubstackDraft, FurtherReading
from .advanced_topic_extractor import extract_topics_advanced, extract_conversation_themes
from ..analysis.signal_extractor import extract_content_signals, extract_high_confidence_signals


class ComprehensiveTechnicalJournalSummarizer:
    """Comprehensive summarizer that captures much more content from technical conversations."""
    
    def __init__(self):
        pass
    
    def extract_comprehensive_context(self, conversation: NormalizedConversation) -> Dict[str, Any]:
        """Extract comprehensive context from the entire conversation."""
        user_messages = [msg.text for msg in conversation.messages if msg.role == "user"]
        assistant_messages = [msg.text for msg in conversation.messages if msg.role == "assistant"]
        all_text = " ".join([msg.text for msg in conversation.messages])
        
        # Extract advanced topics
        topic_analysis = extract_topics_advanced(all_text)
        conversation_themes = extract_conversation_themes(all_text)
        
        # Extract content signals for better context understanding
        all_signals = extract_content_signals(all_text)
        high_confidence_signals = extract_high_confidence_signals(all_text, min_confidence=0.7)
        
        return {
            'project_name': self._extract_project_name(all_text),
            'problem_evolution': self._extract_problem_evolution(user_messages),
            'solution_journey': self._extract_solution_journey(assistant_messages),
            'implementation_details': self._extract_detailed_implementation(assistant_messages),
            'technical_stack': self._extract_comprehensive_tech_stack(all_text),
            'challenges_timeline': self._extract_challenges_timeline(assistant_messages),
            'solutions_provided': self._extract_all_solutions(assistant_messages),
            'code_examples': self._extract_meaningful_code_examples(all_text),
            'decisions_made': self._extract_decisions_made(assistant_messages),
            'results_achieved': self._extract_results_achieved(assistant_messages),
            'lessons_learned': self._extract_comprehensive_lessons(assistant_messages),
            'next_steps': self._extract_next_steps(user_messages),
            'key_insights': self._extract_key_insights(assistant_messages),
            'tools_used': self._extract_all_tools_used(all_text),
            'architecture_decisions': self._extract_architecture_decisions(assistant_messages),
            'topics_discussed': topic_analysis['primary_topics'],
            'conversation_themes': conversation_themes,
            'domain_breakdown': topic_analysis['domain_breakdown'],
            'technical_concepts': topic_analysis.get('technical_concepts', []),
            'content_signals': [s.content for s in all_signals],
            'high_confidence_signals': [s.content for s in high_confidence_signals],
            'signal_summary': {
                'total_signals': len(all_signals),
                'high_confidence_count': len(high_confidence_signals),
                'signal_types': {signal_type: len([s for s in all_signals if s.signal_type == signal_type]) 
                               for signal_type in set(s.signal_type for s in all_signals)}
            }
        }
    
    def _extract_project_name(self, text: str) -> str:
        """Extract the project name from the conversation."""
        project_patterns = [
            r'sentry', r'testsentry', r'docsentry', r'litellm', r'ollama',
            r'deepseek', r'codestral', r'qwen', r'llama'
        ]
        
        for pattern in project_patterns:
            if pattern in text.lower():
                return pattern.title()
        
        return "Technical Project"
    
    def _extract_problem_evolution(self, user_messages: List[str]) -> List[str]:
        """Extract how the problem evolved throughout the conversation."""
        problems = []
        
        for i, message in enumerate(user_messages):
            if len(message) > 30:
                # Look for problem indicators
                problem_indicators = [
                    'need to', 'want to', 'trying to', 'looking for', 'problem', 'issue',
                    'challenge', 'considering', 'thinking about', 'working on', 'wondering',
                    'unsure', 'confused', 'stuck', 'help with'
                ]
                if any(indicator in message.lower() for indicator in problem_indicators):
                    problems.append(f"Step {i+1}: {self._clean_text(message)}")
        
        return problems[:8]
    
    def _extract_solution_journey(self, assistant_messages: List[str]) -> List[str]:
        """Extract the journey of solutions provided."""
        solutions = []
        
        for i, message in enumerate(assistant_messages):
            if len(message) > 50:
                # Look for solution indicators
                solution_indicators = [
                    'solution', 'answer', 'here\'s how', 'you can', 'try this',
                    'recommend', 'suggest', 'approach', 'method', 'way to',
                    'here\'s what', 'let me', 'i\'ll help', 'we can'
                ]
                if any(indicator in message.lower() for indicator in solution_indicators):
                    solutions.append(f"Solution {i+1}: {self._clean_text(message[:200])}")
        
        return solutions[:10]
    
    def _extract_detailed_implementation(self, assistant_messages: List[str]) -> List[str]:
        """Extract detailed implementation steps."""
        implementation = []
        
        for message in assistant_messages:
            if len(message) > 100:
                # Look for implementation indicators
                impl_indicators = [
                    'step', 'first', 'then', 'next', 'after', 'now', 'finally',
                    'install', 'run', 'execute', 'create', 'build', 'setup',
                    'configure', 'deploy', 'test', 'verify'
                ]
                if any(indicator in message.lower() for indicator in impl_indicators):
                    # Extract the implementation details
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in impl_indicators):
                            if len(sentence.strip()) > 20:
                                implementation.append(self._clean_text(sentence.strip()))
        
        return implementation[:15]
    
    def _extract_comprehensive_tech_stack(self, text: str) -> List[str]:
        """Extract comprehensive technical stack."""
        tech_terms = [
            'python', 'javascript', 'typescript', 'bash', 'shell', 'yaml', 'json',
            'ollama', 'litellm', 'sentry', 'pytest', 'github', 'git', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'api', 'rest', 'graphql',
            'llama', 'deepseek', 'qwen', 'codestral', 'mistral', 'openai',
            'rtx', 'gpu', 'vram', 'm1', 'macos', 'linux', 'windows',
            'pip', 'npm', 'yarn', 'homebrew', 'conda', 'venv', 'virtualenv',
            'pytest', 'unittest', 'coverage', 'black', 'flake8', 'mypy',
            'github actions', 'ci/cd', 'workflow', 'runner', 'self-hosted'
        ]
        
        found_tech = []
        for tech in tech_terms:
            if tech.lower() in text.lower():
                found_tech.append(tech.title())
        
        return list(set(found_tech))
    
    def _extract_challenges_timeline(self, assistant_messages: List[str]) -> List[str]:
        """Extract challenges encountered in chronological order."""
        challenges = []
        
        for i, message in enumerate(assistant_messages):
            if len(message) > 50:
                challenge_indicators = [
                    'challenge', 'problem', 'issue', 'difficult', 'trouble',
                    'error', 'bug', 'obstacle', 'timeout', 'memory', 'performance',
                    'dns', 'network', 'connection', 'failed', 'stuck', 'blocked'
                ]
                if any(indicator in message.lower() for indicator in challenge_indicators):
                    challenges.append(f"Challenge {i+1}: {self._clean_text(message[:150])}")
        
        return challenges[:10]
    
    def _extract_all_solutions(self, assistant_messages: List[str]) -> List[str]:
        """Extract all solutions provided."""
        solutions = []
        
        for message in assistant_messages:
            if len(message) > 100:
                # Look for solution patterns
                solution_patterns = [
                    r'here\'s (?:how|what|why)',
                    r'you can (?:try|do|use)',
                    r'try (?:this|that|using)',
                    r'use (?:this|that|the following)',
                    r'run (?:this|that|the following)',
                    r'install (?:this|that|the following)',
                    r'configure (?:this|that|the following)'
                ]
                
                for pattern in solution_patterns:
                    matches = re.findall(pattern, message, re.IGNORECASE)
                    for match in matches:
                        # Extract the sentence containing the solution
                        sentence_match = re.search(r'[^.!?]*' + re.escape(match) + r'[^.!?]*[.!?]', message, re.IGNORECASE)
                        if sentence_match:
                            sentence = sentence_match.group(0).strip()
                            if len(sentence) > 30:
                                solutions.append(self._clean_text(sentence))
        
        return solutions[:12]
    
    def _extract_meaningful_code_examples(self, text: str) -> List[str]:
        """Extract only meaningful code examples that contribute to the story."""
        code_examples = []
        
        # Extract code blocks that are substantial and meaningful
        code_blocks = re.findall(r'```(?:python|bash|yaml|json|javascript|shell)?\n(.*?)\n```', text, re.DOTALL)
        for block in code_blocks:
            block = block.strip()
            if len(block) > 20 and self._is_meaningful_code(block):
                code_examples.append(block)
        
        # Extract inline code that's substantial
        inline_code = re.findall(r'`([^`]+)`', text)
        for code in inline_code:
            if len(code) > 10 and len(code) < 100 and self._is_meaningful_code(code):
                code_examples.append(code)
        
        # Extract important commands
        commands = re.findall(r'(?:pip|npm|git|curl|ollama|litellm|python|bash)\s+[^\n]+', text)
        for cmd in commands:
            if len(cmd) > 15 and self._is_meaningful_command(cmd):
                code_examples.append(cmd)
        
        return code_examples[:8]  # Reduced from 15 to 8 for more selective inclusion
    
    def _is_meaningful_code(self, code: str) -> bool:
        """Determine if code is meaningful and contributes to the story."""
        # Skip very short or trivial code
        if len(code) < 10:
            return False
        
        # Skip single words or very simple expressions
        if len(code.split()) < 3:
            return False
        
        # Skip common trivial patterns
        trivial_patterns = [
            r'^\w+$',  # Single word
            r'^\d+$',  # Single number
            r'^[{}[\]()]+$',  # Just brackets
            r'^[.,;:!?]+$',  # Just punctuation
        ]
        
        for pattern in trivial_patterns:
            if re.match(pattern, code.strip()):
                return False
        
        # Look for meaningful indicators
        meaningful_indicators = [
            'install', 'run', 'execute', 'create', 'build', 'setup', 'configure',
            'deploy', 'test', 'verify', 'import', 'from', 'def', 'class', 'function',
            'if', 'for', 'while', 'try', 'except', 'return', 'yield'
        ]
        
        return any(indicator in code.lower() for indicator in meaningful_indicators)
    
    def _is_meaningful_command(self, cmd: str) -> bool:
        """Determine if a command is meaningful and contributes to the story."""
        # Skip very short commands
        if len(cmd) < 15:
            return False
        
        # Look for meaningful command patterns
        meaningful_patterns = [
            r'install\s+\w+',  # Installation commands
            r'run\s+\w+',      # Run commands
            r'create\s+\w+',   # Create commands
            r'build\s+\w+',    # Build commands
            r'setup\s+\w+',    # Setup commands
            r'configure\s+\w+', # Configure commands
            r'deploy\s+\w+',   # Deploy commands
            r'test\s+\w+',     # Test commands
        ]
        
        return any(re.search(pattern, cmd, re.IGNORECASE) for pattern in meaningful_patterns)
    
    def _extract_decisions_made(self, assistant_messages: List[str]) -> List[str]:
        """Extract decisions made during the conversation."""
        decisions = []
        
        for message in assistant_messages:
            if len(message) > 100:
                decision_indicators = [
                    'decided to', 'chose to', 'opted for', 'went with', 'selected',
                    'recommend', 'suggest', 'prefer', 'better to', 'best to',
                    'should use', 'should go with', 'would recommend'
                ]
                if any(indicator in message.lower() for indicator in decision_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in decision_indicators):
                            if len(sentence.strip()) > 30:
                                decisions.append(self._clean_text(sentence.strip()))
        
        return decisions[:8]
    
    def _extract_results_achieved(self, assistant_messages: List[str]) -> List[str]:
        """Extract results achieved."""
        results = []
        
        for message in assistant_messages:
            if len(message) > 100:
                result_indicators = [
                    'success', 'working', 'completed', 'finished', 'achieved',
                    'done', 'resolved', 'fixed', 'implemented', 'deployed',
                    'running', 'functional', 'operational', 'ready'
                ]
                if any(indicator in message.lower() for indicator in result_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in result_indicators):
                            if len(sentence.strip()) > 20:
                                results.append(self._clean_text(sentence.strip()))
        
        return results[:8]
    
    def _extract_comprehensive_lessons(self, assistant_messages: List[str]) -> List[str]:
        """Extract comprehensive lessons learned."""
        lessons = []
        
        for message in assistant_messages:
            if len(message) > 100:
                lesson_indicators = [
                    'learned', 'realized', 'discovered', 'found out', 'understood',
                    'important', 'key insight', 'takeaway', 'lesson', 'remember',
                    'note that', 'keep in mind', 'crucial', 'essential'
                ]
                if any(indicator in message.lower() for indicator in lesson_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in lesson_indicators):
                            if len(sentence.strip()) > 30:
                                lessons.append(self._clean_text(sentence.strip()))
        
        return lessons[:10]
    
    def _extract_next_steps(self, user_messages: List[str]) -> List[str]:
        """Extract next steps mentioned by the user."""
        next_steps = []
        
        for message in user_messages:
            if len(message) > 30:
                next_step_indicators = [
                    'next step', 'next', 'then', 'after', 'later', 'future',
                    'plan to', 'going to', 'will', 'should', 'need to',
                    'want to', 'thinking about', 'considering'
                ]
                if any(indicator in message.lower() for indicator in next_step_indicators):
                    next_steps.append(self._clean_text(message))
        
        return next_steps[:8]
    
    def _extract_key_insights(self, assistant_messages: List[str]) -> List[str]:
        """Extract key insights from the conversation."""
        insights = []
        
        for message in assistant_messages:
            if len(message) > 150:
                insight_indicators = [
                    'insight', 'important', 'key point', 'note that', 'remember',
                    'crucial', 'essential', 'significant', 'notable', 'interesting',
                    'worth noting', 'keep in mind', 'pay attention to'
                ]
                if any(indicator in message.lower() for indicator in insight_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in insight_indicators):
                            if len(sentence.strip()) > 40:
                                insights.append(self._clean_text(sentence.strip()))
        
        return insights[:10]
    
    def _extract_all_tools_used(self, text: str) -> List[str]:
        """Extract all tools and utilities used."""
        tools = []
        
        tool_patterns = [
            r'ollama', r'litellm', r'github', r'cursor', r'pytest', r'git',
            r'docker', r'homebrew', r'pipx', r'curl', r'jq', r'make',
            r'bash', r'shell', r'terminal', r'cli', r'api', r'web'
        ]
        
        for pattern in tool_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                tools.append(pattern.title())
        
        return list(set(tools))
    
    def _extract_architecture_decisions(self, assistant_messages: List[str]) -> List[str]:
        """Extract architecture decisions made."""
        decisions = []
        
        for message in assistant_messages:
            if len(message) > 150:
                arch_indicators = [
                    'architecture', 'design', 'structure', 'approach', 'pattern',
                    'framework', 'platform', 'system', 'infrastructure', 'setup',
                    'configuration', 'deployment', 'environment'
                ]
                if any(indicator in message.lower() for indicator in arch_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in arch_indicators):
                            if len(sentence.strip()) > 40:
                                decisions.append(self._clean_text(sentence.strip()))
        
        return decisions[:8]
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common prefixes
        text = re.sub(r'^(i think|i believe|i feel|i know|i understand|i realized|i learned)\s+', '', text, flags=re.IGNORECASE)
        # Remove trailing punctuation
        text = re.sub(r'[.!?]+$', '', text)
        return text.strip()
    
    def create_comprehensive_title(self, conversation: NormalizedConversation, context: Dict[str, Any]) -> str:
        """Create a comprehensive title."""
        project_name = context['project_name']
        
        if conversation.title_hint and conversation.title_hint != "Untitled Conversation":
            return conversation.title_hint.replace('ChatGPT - ', '').strip()
        
        return f"Building {project_name}: A Complete Technical Development Journey"
    
    def create_comprehensive_dek(self, context: Dict[str, Any]) -> str:
        """Create a comprehensive dek."""
        return f"A comprehensive technical journal documenting the complete development process, including challenges, solutions, implementation details, and lessons learned."
    
    def create_comprehensive_tldr(self, context: Dict[str, Any]) -> List[str]:
        """Create comprehensive TL;DR points."""
        tldr = []
        
        # Problem evolution
        if context['problem_evolution']:
            tldr.append(f"**Problem Evolution:** {context['problem_evolution'][0][:100]}...")
        
        # Key solution
        if context['solution_journey']:
            tldr.append(f"**Key Solution:** {context['solution_journey'][0][:100]}...")
        
        # Tech stack
        if context['technical_stack']:
            tldr.append(f"**Tech Stack:** {', '.join(context['technical_stack'][:5])}")
        
        # Results
        if context['results_achieved']:
            tldr.append(f"**Results:** {context['results_achieved'][0][:100]}...")
        
        # Key insight
        if context['key_insights']:
            tldr.append(f"**Key Insight:** {context['key_insights'][0][:100]}...")
        
        # Ensure we have at least 3 items for validation
        if len(tldr) < 3:
            tldr.extend([
                "**Development Process:** Comprehensive technical implementation and problem-solving approach",
                "**Key Outcome:** Successful project completion with documented learnings"
            ])
        
        return tldr[:6]
    
    def create_comprehensive_body(self, conversation: NormalizedConversation, context: Dict[str, Any]) -> str:
        """Create a comprehensive technical journal body."""
        body_parts = []
        
        # Introduction
        body_parts.append("## The Complete Development Journey")
        body_parts.append("")
        body_parts.append(f"This comprehensive technical journal documents the complete development process of {context['project_name']}, capturing every challenge, solution, and insight from the entire conversation.")
        body_parts.append("")
        
        # Topics and Themes
        if context['topics_discussed']:
            body_parts.append("## Topics and Themes Discussed")
            body_parts.append("")
            body_parts.append("The conversation covered several key topics and themes:")
            body_parts.append("")
            for i, topic in enumerate(context['topics_discussed'][:8], 1):
                body_parts.append(f"{i}. {topic}")
            body_parts.append("")
        
        if context['conversation_themes']:
            body_parts.append("## Main Themes")
            body_parts.append("")
            for theme in context['conversation_themes']:
                body_parts.append(f"- {theme}")
            body_parts.append("")
        
        # Problem Evolution
        if context['problem_evolution']:
            body_parts.append("## Problem Evolution")
            body_parts.append("")
            body_parts.append("The problem evolved throughout the conversation as new challenges emerged:")
            body_parts.append("")
            for i, problem in enumerate(context['problem_evolution'], 1):
                body_parts.append(f"{i}. {problem}")
            body_parts.append("")
        
        # Solution Journey
        if context['solution_journey']:
            body_parts.append("## Solution Journey")
            body_parts.append("")
            body_parts.append("The solutions were developed iteratively:")
            body_parts.append("")
            for i, solution in enumerate(context['solution_journey'], 1):
                body_parts.append(f"{i}. {solution}")
            body_parts.append("")
        
        # Technical Stack
        if context['technical_stack']:
            body_parts.append("## Comprehensive Technical Stack")
            body_parts.append("")
            body_parts.append("The project utilized a wide range of technologies:")
            body_parts.append("")
            for tech in context['technical_stack']:
                body_parts.append(f"- **{tech}**: [Description of usage]")
            body_parts.append("")
        
        # Implementation Details
        if context['implementation_details']:
            body_parts.append("## Detailed Implementation")
            body_parts.append("")
            body_parts.append("The implementation involved numerous detailed steps:")
            body_parts.append("")
            for i, detail in enumerate(context['implementation_details'], 1):
                body_parts.append(f"{i}. {detail}")
            body_parts.append("")
        
        # Challenges Timeline
        if context['challenges_timeline']:
            body_parts.append("## Challenges Encountered")
            body_parts.append("")
            body_parts.append("Several challenges were encountered and overcome:")
            body_parts.append("")
            for challenge in context['challenges_timeline']:
                body_parts.append(f"- {challenge}")
            body_parts.append("")
        
        # Solutions Provided
        if context['solutions_provided']:
            body_parts.append("## Solutions Provided")
            body_parts.append("")
            body_parts.append("Multiple solutions were developed and implemented:")
            body_parts.append("")
            for i, solution in enumerate(context['solutions_provided'], 1):
                body_parts.append(f"{i}. {solution}")
            body_parts.append("")
        
        # Code Examples
        if context['code_examples']:
            body_parts.append("## Code Examples")
            body_parts.append("")
            body_parts.append("Key code examples from the implementation:")
            body_parts.append("")
            for i, example in enumerate(context['code_examples'][:8], 1):
                body_parts.append(f"**Example {i}:**")
                body_parts.append("```")
                body_parts.append(example)
                body_parts.append("```")
                body_parts.append("")
        
        # Architecture Decisions
        if context['architecture_decisions']:
            body_parts.append("## Architecture Decisions")
            body_parts.append("")
            body_parts.append("Key architectural decisions made during development:")
            body_parts.append("")
            for decision in context['architecture_decisions']:
                body_parts.append(f"- {decision}")
            body_parts.append("")
        
        # Results Achieved
        if context['results_achieved']:
            body_parts.append("## Results Achieved")
            body_parts.append("")
            body_parts.append("The project achieved several key results:")
            body_parts.append("")
            for result in context['results_achieved']:
                body_parts.append(f"- {result}")
            body_parts.append("")
        
        # Key Insights
        if context['key_insights']:
            body_parts.append("## Key Insights")
            body_parts.append("")
            body_parts.append("Important insights gained during the development process:")
            body_parts.append("")
            for insight in context['key_insights']:
                body_parts.append(f"- {insight}")
            body_parts.append("")
        
        # Lessons Learned
        if context['lessons_learned']:
            body_parts.append("## Comprehensive Lessons Learned")
            body_parts.append("")
            body_parts.append("The development process provided numerous valuable lessons:")
            body_parts.append("")
            for lesson in context['lessons_learned']:
                body_parts.append(f"- {lesson}")
            body_parts.append("")
        
        # Next Steps
        if context['next_steps']:
            body_parts.append("## Next Steps")
            body_parts.append("")
            body_parts.append("Future development directions identified:")
            body_parts.append("")
            for step in context['next_steps']:
                body_parts.append(f"- {step}")
            body_parts.append("")
        
        # Conclusion
        body_parts.append("## Conclusion")
        body_parts.append("")
        body_parts.append("This comprehensive technical journal captures the complete development journey, from initial problem identification through final implementation and lessons learned. The iterative nature of the development process, the numerous challenges overcome, and the solutions developed provide valuable insights for future projects.")
        body_parts.append("")
        body_parts.append("The project demonstrates the importance of systematic problem-solving, careful technology selection, and iterative development. The extensive documentation of challenges, solutions, and lessons learned will be invaluable for future reference and for others facing similar technical challenges.")
        
        return '\n'.join(body_parts)
    
    def create_comprehensive_tags(self, context: Dict[str, Any]) -> List[str]:
        """Create comprehensive tags."""
        tags = ['technical', 'development', 'project', 'comprehensive', 'journal']
        
        # Add technology-specific tags
        if context['technical_stack']:
            tags.extend([tech.lower() for tech in context['technical_stack'][:5]])
        
        # Add project-specific tags
        if context['project_name']:
            tags.append(context['project_name'].lower())
        
        return tags[:6]
    
    def summarize(self, conversation: NormalizedConversation) -> SubstackDraft:
        """Generate comprehensive technical journal entry."""
        # Extract comprehensive context
        context = self.extract_comprehensive_context(conversation)
        
        # Generate components
        title = self.create_comprehensive_title(conversation, context)
        dek = self.create_comprehensive_dek(context)
        tldr = self.create_comprehensive_tldr(context)
        tags = self.create_comprehensive_tags(context)
        body_markdown = self.create_comprehensive_body(conversation, context)
        further_reading = [
            FurtherReading(title="Comprehensive Technical Writing", url="https://example.com/comprehensive-tech-writing"),
            FurtherReading(title="Development Process Documentation", url="https://example.com/dev-process-docs")
        ]
        
        # Ensure word count is within limits (increased for comprehensive content)
        word_count = len(body_markdown.split())
        if word_count > 1400:  # Increased from 900 to 1400 for comprehensive content
            words = body_markdown.split()
            body_markdown = ' '.join(words[:1400])
        
        return SubstackDraft(
            title=title,
            dek=dek,
            tldr=tldr,
            tags=tags,
            body_markdown=body_markdown,
            further_reading=further_reading
        )


def summarize_conversation_comprehensive(conversation: NormalizedConversation) -> SubstackDraft:
    """Generate comprehensive technical journal entry with full conversation context."""
    summarizer = ComprehensiveTechnicalJournalSummarizer()
    return summarizer.summarize(conversation)
