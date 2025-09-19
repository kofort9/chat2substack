"""System for testing multiple prompts simultaneously."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from ..util.schema import NormalizedConversation, SubstackDraft
from .narrative_summarizer import summarize_conversation_narrative
from .journal_summarizer import summarize_conversation_journal
from .enhanced_summarizer import summarize_conversation_enhanced


class PromptTester:
    """Test multiple summarization approaches simultaneously."""
    
    def __init__(self):
        self.summarizers = {
            'narrative': summarize_conversation_narrative,
            'journal': summarize_conversation_journal,
            'enhanced': summarize_conversation_enhanced
        }
    
    def test_all_approaches(self, conversation: NormalizedConversation) -> Dict[str, SubstackDraft]:
        """Test all summarization approaches on the same conversation."""
        results = {}
        
        for name, summarizer_func in self.summarizers.items():
            try:
                draft = summarizer_func(conversation)
                results[name] = draft
            except Exception as e:
                print(f"Error with {name} summarizer: {e}")
                results[name] = None
        
        return results
    
    def compare_outputs(self, results: Dict[str, SubstackDraft]) -> Dict[str, Any]:
        """Compare the outputs of different summarizers."""
        comparison = {
            'word_counts': {},
            'titles': {},
            'approaches': {},
            'quality_metrics': {}
        }
        
        for name, draft in results.items():
            if draft:
                comparison['word_counts'][name] = len(draft.body_markdown.split())
                comparison['titles'][name] = draft.title
                comparison['approaches'][name] = {
                    'has_narrative_flow': self._check_narrative_flow(draft.body_markdown),
                    'has_technical_details': self._check_technical_details(draft.body_markdown),
                    'has_personal_voice': self._check_personal_voice(draft.body_markdown),
                    'has_story_structure': self._check_story_structure(draft.body_markdown)
                }
        
        return comparison
    
    def _check_narrative_flow(self, content: str) -> bool:
        """Check if content has narrative flow."""
        narrative_indicators = [
            'today', 'yesterday', 'recently', 'i found', 'i discovered',
            'the story', 'the journey', 'what happened', 'the process'
        ]
        return any(indicator in content.lower() for indicator in narrative_indicators)
    
    def _check_technical_details(self, content: str) -> bool:
        """Check if content has technical details."""
        technical_indicators = [
            '`', '```', 'pip', 'npm', 'git', 'curl', 'python', 'javascript',
            'api', 'database', 'server', 'function', 'method', 'class'
        ]
        return any(indicator in content for indicator in technical_indicators)
    
    def _check_personal_voice(self, content: str) -> bool:
        """Check if content has personal voice."""
        personal_indicators = [
            'i', 'my', 'me', 'we', 'our', 'us', 'i think', 'i believe',
            'i found', 'i discovered', 'i learned', 'i realized'
        ]
        return any(indicator in content.lower() for indicator in personal_indicators)
    
    def _check_story_structure(self, content: str) -> bool:
        """Check if content has story structure."""
        story_indicators = [
            'the problem', 'the challenge', 'the approach', 'the solution',
            'the results', 'the outcome', 'what happened', 'the journey'
        ]
        return any(indicator in content.lower() for indicator in story_indicators)
    
    def generate_comparison_report(self, results: Dict[str, SubstackDraft], comparison: Dict[str, Any]) -> str:
        """Generate a comparison report."""
        report = "# Prompt Testing Comparison Report\n\n"
        
        report += "## Summary\n"
        report += f"Tested {len(results)} different summarization approaches on the same conversation.\n\n"
        
        report += "## Word Counts\n"
        for name, count in comparison['word_counts'].items():
            report += f"- **{name}**: {count} words\n"
        report += "\n"
        
        report += "## Titles\n"
        for name, title in comparison['titles'].items():
            report += f"- **{name}**: {title}\n"
        report += "\n"
        
        report += "## Quality Metrics\n"
        for name, metrics in comparison['approaches'].items():
            report += f"### {name.title()}\n"
            for metric, value in metrics.items():
                status = "✅" if value else "❌"
                report += f"- {metric.replace('_', ' ').title()}: {status}\n"
            report += "\n"
        
        return report
    
    def save_comparison_results(self, results: Dict[str, SubstackDraft], comparison: Dict[str, Any], output_dir: str = "dist/comparison"):
        """Save comparison results to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save individual drafts
        for name, draft in results.items():
            if draft:
                # Save markdown
                markdown_file = output_path / f"{name}_draft.md"
                with open(markdown_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {draft.title}\n\n")
                    f.write(f"*{draft.dek}*\n\n")
                    f.write("**TL;DR**\n")
                    for point in draft.tldr:
                        f.write(f"- {point}\n")
                    f.write("\n")
                    f.write(draft.body_markdown)
                
                # Save HTML
                html_file = output_path / f"{name}_draft.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(f"<h1>{draft.title}</h1>\n")
                    f.write(f"<p><em>{draft.dek}</em></p>\n")
                    f.write("<p><strong>TL;DR</strong></p>\n<ul>\n")
                    for point in draft.tldr:
                        f.write(f"<li>{point}</li>\n")
                    f.write("</ul>\n")
                    f.write(draft.body_markdown.replace('\n', '<br>\n'))
        
        # Save comparison report
        report = self.generate_comparison_report(results, comparison)
        report_file = output_path / "comparison_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save JSON comparison data
        json_file = output_path / "comparison_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)
        
        print(f"Comparison results saved to {output_path}")


def test_prompts(conversation: NormalizedConversation, output_dir: str = "dist/comparison") -> Dict[str, Any]:
    """Test all prompts on a conversation and save results."""
    tester = PromptTester()
    
    # Test all approaches
    results = tester.test_all_approaches(conversation)
    
    # Compare outputs
    comparison = tester.compare_outputs(results)
    
    # Save results
    tester.save_comparison_results(results, comparison, output_dir)
    
    return {
        'results': results,
        'comparison': comparison
    }
