"""Conversation analysis and storage system for comparing full context vs summarized output."""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from ..util.schema import NormalizedConversation, SubstackDraft
from ..llm.advanced_topic_extractor import extract_topics_advanced, extract_conversation_themes


class ConversationAnalyzer:
    """Analyzes full conversations and compares them with summarized outputs."""
    
    def __init__(self, output_dir: Path = Path("dist")):
        self.output_dir = output_dir
    
    def store_full_conversation(self, conversation: NormalizedConversation, post_slug: str) -> Path:
        """Store the full conversation in the post folder for records."""
        # Create post-specific directory
        post_dir = self.output_dir / post_slug
        post_dir.mkdir(parents=True, exist_ok=True)
        
        # Store full conversation data
        conversation_data = {
            "metadata": {
                "title_hint": conversation.title_hint,
                "source_type": conversation.source.type,
                "source_path": conversation.source.path,
                "message_count": len(conversation.messages),
                "extracted_at": datetime.now().isoformat()
            },
            "messages": [
                {
                    "role": msg.role,
                    "text": msg.text,
                    "length": len(msg.text),
                    "word_count": len(msg.text.split())
                }
                for msg in conversation.messages
            ],
            "full_text": " ".join([msg.text for msg in conversation.messages]),
            "total_word_count": sum(len(msg.text.split()) for msg in conversation.messages),
            "total_char_count": sum(len(msg.text) for msg in conversation.messages)
        }
        
        # Save to JSON
        conversation_file = post_dir / "full_conversation.json"
        with open(conversation_file, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        
        # Also save as readable markdown
        markdown_file = post_dir / "full_conversation.md"
        self._save_conversation_as_markdown(conversation, markdown_file)
        
        return conversation_file
    
    def _save_conversation_as_markdown(self, conversation: NormalizedConversation, output_file: Path):
        """Save conversation as readable markdown."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Full Conversation: {conversation.title_hint}\n\n")
            f.write(f"**Source:** {conversation.source.type} - {conversation.source.path}\n")
            f.write(f"**Message Count:** {len(conversation.messages)}\n")
            f.write(f"**Total Words:** {sum(len(msg.text.split()) for msg in conversation.messages)}\n\n")
            f.write("---\n\n")
            
            for i, msg in enumerate(conversation.messages, 1):
                f.write(f"## Message {i} - {msg.role.title()}\n\n")
                f.write(f"**Length:** {len(msg.text)} chars, {len(msg.text.split())} words\n\n")
                f.write(f"{msg.text}\n\n")
                f.write("---\n\n")
    
    def analyze_conversation_content(self, conversation: NormalizedConversation) -> Dict[str, Any]:
        """Analyze the content of the full conversation."""
        all_text = " ".join([msg.text for msg in conversation.messages])
        user_messages = [msg.text for msg in conversation.messages if msg.role == "user"]
        assistant_messages = [msg.text for msg in conversation.messages if msg.role == "assistant"]
        
        # Use advanced topic extraction
        topic_analysis = extract_topics_advanced(all_text)
        conversation_themes = extract_conversation_themes(all_text)
        
        return {
            "total_messages": len(conversation.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_words": len(all_text.split()),
            "total_characters": len(all_text),
            "average_message_length": sum(len(msg.text.split()) for msg in conversation.messages) / len(conversation.messages),
            "longest_message": max(len(msg.text.split()) for msg in conversation.messages),
            "shortest_message": min(len(msg.text.split()) for msg in conversation.messages),
            "topics_discussed": topic_analysis['primary_topics'],
            "conversation_themes": conversation_themes,
            "domain_breakdown": topic_analysis['domain_breakdown'],
            "technical_terms": self._extract_technical_terms(all_text),
            "code_snippets": self._extract_code_snippets(all_text),
            "questions_asked": self._extract_questions(user_messages),
            "solutions_provided": self._extract_solutions(assistant_messages),
            "key_insights": self._extract_key_insights(assistant_messages)
        }
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics discussed."""
        topics = []
        
        # Look for topic indicators
        topic_patterns = [
            r'(?:discussing|talking about|focusing on|working on) ([^.!?]+)',
            r'(?:topic|subject|issue|problem) (?:is|of|about) ([^.!?]+)',
            r'(?:let\'s|we\'ll) (?:discuss|talk about|focus on) ([^.!?]+)'
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 5:
                    topics.append(match.strip())
        
        return list(set(topics))[:10]
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms mentioned."""
        technical_terms = [
            'python', 'javascript', 'api', 'database', 'server', 'client',
            'framework', 'library', 'package', 'module', 'function',
            'class', 'method', 'variable', 'algorithm', 'data structure',
            'git', 'github', 'docker', 'kubernetes', 'aws', 'azure',
            'ollama', 'litellm', 'sentry', 'pytest', 'yaml', 'json',
            'bash', 'shell', 'command', 'terminal', 'cli', 'gui'
        ]
        
        found_terms = []
        for term in technical_terms:
            if term.lower() in text.lower():
                found_terms.append(term)
        
        return found_terms
    
    def _extract_code_snippets(self, text: str) -> List[str]:
        """Extract code snippets from the conversation."""
        snippets = []
        
        # Extract code blocks
        code_blocks = re.findall(r'```(?:python|bash|yaml|json|javascript)?\n(.*?)\n```', text, re.DOTALL)
        for block in code_blocks:
            if len(block.strip()) > 10:
                snippets.append(block.strip())
        
        # Extract inline code
        inline_code = re.findall(r'`([^`]+)`', text)
        for code in inline_code:
            if len(code) > 5 and len(code) < 100:
                snippets.append(code)
        
        return snippets[:10]
    
    def _extract_questions(self, user_messages: List[str]) -> List[str]:
        """Extract questions asked by the user."""
        questions = []
        
        for message in user_messages:
            if '?' in message:
                # Split by sentences and find questions
                sentences = re.split(r'[.!?]+', message)
                for sentence in sentences:
                    if '?' in sentence and len(sentence.strip()) > 10:
                        questions.append(sentence.strip())
        
        return questions[:10]
    
    def _extract_solutions(self, assistant_messages: List[str]) -> List[str]:
        """Extract solutions provided by the assistant."""
        solutions = []
        
        for message in assistant_messages:
            if len(message) > 100:
                # Look for solution indicators
                solution_indicators = [
                    'solution', 'answer', 'here\'s how', 'you can', 'try this',
                    'recommend', 'suggest', 'approach', 'method', 'way to'
                ]
                if any(indicator in message.lower() for indicator in solution_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in solution_indicators):
                            if len(sentence.strip()) > 20:
                                solutions.append(sentence.strip())
        
        return solutions[:10]
    
    def _extract_key_insights(self, assistant_messages: List[str]) -> List[str]:
        """Extract key insights from assistant messages."""
        insights = []
        
        for message in assistant_messages:
            if len(message) > 100:
                # Look for insight indicators
                insight_indicators = [
                    'insight', 'important', 'key point', 'note that', 'remember',
                    'crucial', 'essential', 'significant', 'notable', 'interesting'
                ]
                if any(indicator in message.lower() for indicator in insight_indicators):
                    sentences = message.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in insight_indicators):
                            if len(sentence.strip()) > 20:
                                insights.append(sentence.strip())
        
        return insights[:10]
    
    def compare_with_summary(self, conversation: NormalizedConversation, draft: SubstackDraft, post_slug: str) -> Dict[str, Any]:
        """Compare the full conversation with the summarized output."""
        # Analyze full conversation
        full_analysis = self.analyze_conversation_content(conversation)
        
        # Analyze summarized output
        summary_text = f"{draft.title} {draft.dek} {' '.join(draft.tldr)} {draft.body_markdown}"
        
        # Use advanced topic extraction for both conversation and summary
        from src.llm.advanced_topic_extractor import extract_topics_advanced
        summary_topic_analysis = extract_topics_advanced(summary_text)
        
        summary_analysis = {
            "word_count": len(summary_text.split()),
            "char_count": len(summary_text),
            "topics_covered": summary_topic_analysis['primary_topics'],
            "technical_terms_used": self._extract_technical_terms(summary_text),
            "code_snippets_included": self._extract_code_snippets(summary_text)
        }
        
        # Calculate coverage metrics
        coverage_metrics = {
            "word_coverage": (summary_analysis["word_count"] / full_analysis["total_words"]) * 100,
            "topic_coverage": self._calculate_topic_coverage(full_analysis["topics_discussed"], summary_analysis["topics_covered"]),
            "technical_term_coverage": self._calculate_term_coverage(full_analysis["technical_terms"], summary_analysis["technical_terms_used"]),
            "code_snippet_coverage": self._calculate_snippet_coverage(full_analysis["code_snippets"], summary_analysis["code_snippets_included"]),
            "questions_addressed": self._calculate_question_coverage(full_analysis["questions_asked"], summary_text),
            "solutions_included": self._calculate_solution_coverage(full_analysis["solutions_provided"], summary_text)
        }
        
        # Identify what's missing
        missing_content = {
            "topics_not_covered": list(set(full_analysis["topics_discussed"]) - set(summary_analysis["topics_covered"])),
            "technical_terms_missing": list(set(full_analysis["technical_terms"]) - set(summary_analysis["technical_terms_used"])),
            "code_snippets_missing": list(set(full_analysis["code_snippets"]) - set(summary_analysis["code_snippets_included"])),
            "questions_not_addressed": [q for q in full_analysis["questions_asked"] if not any(q.lower() in summary_text.lower() for q in [q])],
            "solutions_not_included": [s for s in full_analysis["solutions_provided"] if not any(s.lower() in summary_text.lower() for s in [s])]
        }
        
        # Create comparison report
        comparison_report = {
            "full_conversation": full_analysis,
            "summary_output": summary_analysis,
            "coverage_metrics": coverage_metrics,
            "missing_content": missing_content,
            "recommendations": self._generate_recommendations(coverage_metrics, missing_content)
        }
        
        # Save comparison report
        post_dir = self.output_dir / post_slug
        post_dir.mkdir(parents=True, exist_ok=True)
        
        comparison_file = post_dir / "conversation_vs_summary_analysis.json"
        with open(comparison_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_report, f, indent=2, ensure_ascii=False)
        
        # Also save as readable markdown
        self._save_comparison_as_markdown(comparison_report, post_dir / "conversation_vs_summary_analysis.md")
        
        return comparison_report
    
    def _calculate_topic_coverage(self, full_topics: List[str], summary_topics: List[str]) -> float:
        """Calculate what percentage of topics were covered using improved fuzzy matching."""
        if not full_topics:
            return 100.0
        
        # Use improved fuzzy matching with multiple strategies
        covered_count = 0
        for full_topic in full_topics:
            full_words = set(full_topic.lower().split())
            best_match = False
            
            for summary_topic in summary_topics:
                summary_words = set(summary_topic.lower().split())
                
                # Strategy 1: Direct word overlap
                overlap = len(full_words & summary_words)
                total_words = len(full_words | summary_words)
                if total_words > 0:
                    similarity = overlap / total_words
                    if similarity > 0.2:  # Lowered threshold to 20%
                        best_match = True
                        break
                
                # Strategy 2: Key word matching (important technical terms)
                key_words = {'sentry', 'cursor', 'prompt', 'readme', 'test', 'code', 'deepseek', 'ollama', 'llm', 'api', 'json', 'yaml', 'docker', 'github'}
                full_key_words = full_words & key_words
                summary_key_words = summary_words & key_words
                if full_key_words and summary_key_words:
                    key_overlap = len(full_key_words & summary_key_words)
                    if key_overlap >= len(full_key_words) * 0.5:  # 50% of key words match
                        best_match = True
                        break
                
                # Strategy 3: Phrase matching (substring overlap)
                full_phrases = self._extract_phrases(full_topic.lower())
                summary_phrases = self._extract_phrases(summary_topic.lower())
                phrase_overlap = len(set(full_phrases) & set(summary_phrases))
                if phrase_overlap > 0:
                    best_match = True
                    break
            
            if best_match:
                covered_count += 1
        
        return (covered_count / len(full_topics)) * 100
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract meaningful phrases from text for better matching."""
        import re
        
        # Extract 2-3 word phrases
        words = re.findall(r'\b\w+\b', text)
        phrases = []
        
        # 2-word phrases
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 5:  # Only meaningful phrases
                phrases.append(phrase)
        
        # 3-word phrases
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(phrase) > 8:  # Only meaningful phrases
                phrases.append(phrase)
        
        return phrases
    
    def _calculate_term_coverage(self, full_terms: List[str], summary_terms: List[str]) -> float:
        """Calculate what percentage of technical terms were covered."""
        if not full_terms:
            return 100.0
        covered = len(set(full_terms) & set(summary_terms))
        return (covered / len(full_terms)) * 100
    
    def _calculate_snippet_coverage(self, full_snippets: List[str], summary_snippets: List[str]) -> float:
        """Calculate what percentage of code snippets were covered."""
        if not full_snippets:
            return 100.0
        covered = len(set(full_snippets) & set(summary_snippets))
        return (covered / len(full_snippets)) * 100
    
    def _calculate_question_coverage(self, full_questions: List[str], summary_text: str) -> float:
        """Calculate what percentage of questions were addressed."""
        if not full_questions:
            return 100.0
        addressed = sum(1 for q in full_questions if any(q.lower() in summary_text.lower() for q in [q]))
        return (addressed / len(full_questions)) * 100
    
    def _calculate_solution_coverage(self, full_solutions: List[str], summary_text: str) -> float:
        """Calculate what percentage of solutions were included."""
        if not full_solutions:
            return 100.0
        included = sum(1 for s in full_solutions if any(s.lower() in summary_text.lower() for s in [s]))
        return (included / len(full_solutions)) * 100
    
    def _generate_recommendations(self, coverage_metrics: Dict[str, float], missing_content: Dict[str, List[str]]) -> List[str]:
        """Generate recommendations for improving summarization."""
        recommendations = []
        
        if coverage_metrics["word_coverage"] < 10:
            recommendations.append("Consider increasing the word count target to capture more content")
        
        if coverage_metrics["topic_coverage"] < 50:
            recommendations.append("Improve topic extraction to cover more discussed subjects")
        
        if coverage_metrics["technical_term_coverage"] < 30:
            recommendations.append("Include more technical terms in the summary")
        
        if coverage_metrics["code_snippet_coverage"] < 20:
            recommendations.append("Include more code snippets and examples")
        
        if coverage_metrics["questions_addressed"] < 40:
            recommendations.append("Address more of the questions asked in the conversation")
        
        if coverage_metrics["solutions_included"] < 30:
            recommendations.append("Include more of the solutions provided")
        
        if missing_content["topics_not_covered"]:
            recommendations.append(f"Consider covering these topics: {', '.join(missing_content['topics_not_covered'][:3])}")
        
        if missing_content["technical_terms_missing"]:
            recommendations.append(f"Consider including these technical terms: {', '.join(missing_content['technical_terms_missing'][:5])}")
        
        return recommendations
    
    def _save_comparison_as_markdown(self, comparison_report: Dict[str, Any], output_file: Path):
        """Save comparison report as readable markdown."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Conversation vs Summary Analysis\n\n")
            
            # Overview
            f.write("## Overview\n\n")
            f.write(f"**Full Conversation:** {comparison_report['full_conversation']['total_words']} words, {comparison_report['full_conversation']['total_messages']} messages\n")
            f.write(f"**Summary Output:** {comparison_report['summary_output']['word_count']} words\n")
            f.write(f"**Word Coverage:** {comparison_report['coverage_metrics']['word_coverage']:.1f}%\n\n")
            
            # Coverage Metrics
            f.write("## Coverage Metrics\n\n")
            metrics = comparison_report['coverage_metrics']
            f.write(f"- **Topic Coverage:** {metrics['topic_coverage']:.1f}%\n")
            f.write(f"- **Technical Term Coverage:** {metrics['technical_term_coverage']:.1f}%\n")
            f.write(f"- **Code Snippet Coverage:** {metrics['code_snippet_coverage']:.1f}%\n")
            f.write(f"- **Questions Addressed:** {metrics['questions_addressed']:.1f}%\n")
            f.write(f"- **Solutions Included:** {metrics['solutions_included']:.1f}%\n\n")
            
            # Missing Content
            f.write("## Missing Content\n\n")
            missing = comparison_report['missing_content']
            
            if missing['topics_not_covered']:
                f.write("### Topics Not Covered\n")
                for topic in missing['topics_not_covered'][:5]:
                    f.write(f"- {topic}\n")
                f.write("\n")
            
            if missing['technical_terms_missing']:
                f.write("### Technical Terms Missing\n")
                for term in missing['technical_terms_missing'][:10]:
                    f.write(f"- {term}\n")
                f.write("\n")
            
            if missing['code_snippets_missing']:
                f.write("### Code Snippets Missing\n")
                for snippet in missing['code_snippets_missing'][:5]:
                    f.write(f"```\n{snippet}\n```\n")
                f.write("\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            for rec in comparison_report['recommendations']:
                f.write(f"- {rec}\n")
            f.write("\n")


def analyze_conversation_and_compare(conversation: NormalizedConversation, draft: SubstackDraft, post_slug: str, output_dir: Path = Path("dist")) -> Dict[str, Any]:
    """Analyze full conversation and compare with summary."""
    analyzer = ConversationAnalyzer(output_dir)
    
    # Store full conversation
    conversation_file = analyzer.store_full_conversation(conversation, post_slug)
    print(f"Stored full conversation: {conversation_file}")
    
    # Compare with summary
    comparison_report = analyzer.compare_with_summary(conversation, draft, post_slug)
    print(f"Generated comparison analysis for: {post_slug}")
    
    return comparison_report
