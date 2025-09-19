"""Comprehensive comparison system for all summarizer types."""

import json
from pathlib import Path
from typing import Dict, Any, List
from ..util.schema import NormalizedConversation, SubstackDraft
from .specialized_summarizers import summarize_conversation_technical_journal
from .research_article_summarizer import summarize_conversation_research_article
from .critique_summarizer import summarize_conversation_critique
from .enhanced_summarizer import summarize_conversation_enhanced
from .journal_summarizer import summarize_conversation_journal
from .narrative_summarizer import summarize_conversation_narrative


class ComprehensiveComparison:
    """Compares all summarizer types and generates detailed reports."""
    
    def __init__(self, output_dir: Path = Path("dist/comparison")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.summarizers = {
            "technical_journal": summarize_conversation_technical_journal,
            "research_article": summarize_conversation_research_article,
            "critique": summarize_conversation_critique,
            "enhanced": summarize_conversation_enhanced,
            "journal": summarize_conversation_journal,
            "narrative": summarize_conversation_narrative,
        }
    
    def _evaluate_draft_quality(self, draft: SubstackDraft, style: str) -> Dict[str, Any]:
        """Evaluates the quality of a draft based on the expected style."""
        full_text = f"{draft.title} {draft.dek} {' '.join(draft.tldr)} {draft.body_markdown}"
        full_text_lower = full_text.lower()
        
        # Basic metrics
        word_count = len(draft.body_markdown.split())
        tldr_count = len(draft.tldr)
        tag_count = len(draft.tags)
        
        # Content quality indicators
        has_narrative_flow = word_count > 200 and any(connector in full_text_lower for connector in ['however', 'therefore', 'moreover', 'furthermore', 'consequently'])
        has_technical_details = any(tech in full_text_lower for tech in ['```', 'code', 'python', 'javascript', 'api', 'cli', 'install', 'command', 'config', 'yaml'])
        has_personal_voice = any(pronoun in full_text_lower for pronoun in ['i think', 'my opinion', 'i believe', 'i found myself', 'my journey', 'i learned'])
        has_structure = any(section in full_text for section in ['##', '###'])
        
        # Style-specific checks
        style_appropriate = False
        if style == "technical_journal":
            style_appropriate = all(section in full_text for section in ["## The Challenge", "## The Approach", "## Results"])
        elif style == "research_article":
            style_appropriate = all(section in full_text for section in ["## Introduction", "## Key Findings", "## Conclusions"])
        elif style == "critique":
            style_appropriate = all(section in full_text for section in ["## Main Arguments", "## Strengths", "## Areas of Concern"])
        elif style == "journal":
            style_appropriate = all(section in full_text for section in ["## The Problem", "## The Approach", "## The Results"])
        elif style == "narrative":
            style_appropriate = all(section in full_text for section in ["## The Conversation That Changed Everything", "## What We Discovered"])
        
        return {
            "word_count": word_count,
            "tldr_count": tldr_count,
            "tag_count": tag_count,
            "has_narrative_flow": has_narrative_flow,
            "has_technical_details": has_technical_details,
            "has_personal_voice": has_personal_voice,
            "has_structure": has_structure,
            "style_appropriate": style_appropriate,
            "overall_quality": self._calculate_overall_quality(word_count, has_narrative_flow, has_technical_details, has_structure, style_appropriate)
        }
    
    def _calculate_overall_quality(self, word_count: int, narrative_flow: bool, technical_details: bool, structure: bool, style_appropriate: bool) -> str:
        """Calculate overall quality rating."""
        score = 0
        
        # Word count scoring
        if word_count >= 400:
            score += 2
        elif word_count >= 200:
            score += 1
        
        # Content quality scoring
        if narrative_flow:
            score += 1
        if technical_details:
            score += 1
        if structure:
            score += 1
        if style_appropriate:
            score += 2
        
        if score >= 6:
            return "Excellent"
        elif score >= 4:
            return "Good"
        elif score >= 2:
            return "Fair"
        else:
            return "Poor"
    
    def run_comprehensive_comparison(self, conversation: NormalizedConversation) -> Path:
        """Runs all summarizers and generates a comprehensive comparison report."""
        results = {}
        
        print(f"Running comprehensive comparison on conversation with {len(conversation.messages)} messages...")
        
        for name, summarizer_func in self.summarizers.items():
            try:
                print(f"  - Running {name} summarizer...")
                draft = summarizer_func(conversation)
                quality_metrics = self._evaluate_draft_quality(draft, name)
                
                results[name] = {
                    "draft": draft,
                    "quality_metrics": quality_metrics,
                    "title": draft.title,
                    "dek": draft.dek,
                    "tldr": draft.tldr,
                    "tags": draft.tags,
                    "word_count": quality_metrics["word_count"],
                    "overall_quality": quality_metrics["overall_quality"]
                }
                
                # Save individual draft for review
                self._save_individual_draft(name, draft)
                
            except Exception as e:
                print(f"  - Error with {name}: {str(e)}")
                results[name] = {"error": str(e)}
        
        # Generate comprehensive report
        report_path = self._generate_comprehensive_report(results)
        
        # Generate summary statistics
        self._generate_summary_statistics(results)
        
        return report_path
    
    def _save_individual_draft(self, name: str, draft: SubstackDraft):
        """Save individual draft for review."""
        draft_content = f"""# {draft.title}

*{draft.dek}*

## TL;DR
{chr(10).join([f"- {t}" for t in draft.tldr])}

## Body

{draft.body_markdown}

## Tags
{', '.join(draft.tags)}

## Further Reading
{chr(10).join([f"- [{fr.title}]({fr.url})" for fr in draft.further_reading or []])}
"""
        
        with open(self.output_dir / f"{name}_draft.md", 'w', encoding='utf-8') as f:
            f.write(draft_content)
    
    def _generate_comprehensive_report(self, results: Dict[str, Any]) -> Path:
        """Generate comprehensive comparison report."""
        report = "# Comprehensive Summarizer Comparison Report\n\n"
        report += f"## Overview\n\n"
        report += f"Tested {len(self.summarizers)} different summarization approaches on the same conversation.\n\n"
        
        # Summary table
        report += "## Summary Table\n\n"
        report += "| Summarizer | Word Count | Quality | Title |\n"
        report += "|------------|------------|---------|-------|\n"
        
        for name, data in results.items():
            if "error" not in data:
                report += f"| {name} | {data['word_count']} | {data['overall_quality']} | {data['title'][:50]}... |\n"
            else:
                report += f"| {name} | ERROR | - | - |\n"
        
        report += "\n"
        
        # Detailed analysis
        report += "## Detailed Analysis\n\n"
        
        for name, data in results.items():
            if "error" not in data:
                report += f"### {name.title()}\n\n"
                report += f"**Title:** {data['title']}\n\n"
                report += f"**Dek:** {data['dek']}\n\n"
                report += f"**Word Count:** {data['word_count']}\n\n"
                report += f"**Overall Quality:** {data['overall_quality']}\n\n"
                
                # Quality metrics
                metrics = data['quality_metrics']
                report += "**Quality Metrics:**\n"
                report += f"- Narrative Flow: {'✅' if metrics['has_narrative_flow'] else '❌'}\n"
                report += f"- Technical Details: {'✅' if metrics['has_technical_details'] else '❌'}\n"
                report += f"- Personal Voice: {'✅' if metrics['has_personal_voice'] else '❌'}\n"
                report += f"- Structure: {'✅' if metrics['has_structure'] else '❌'}\n"
                report += f"- Style Appropriate: {'✅' if metrics['style_appropriate'] else '❌'}\n\n"
                
                # TL;DR
                report += "**TL;DR:**\n"
                for tldr in data['tldr']:
                    report += f"- {tldr}\n"
                report += "\n"
                
                # Tags
                report += f"**Tags:** {', '.join(data['tags'])}\n\n"
                
            else:
                report += f"### {name.title()}\n\n"
                report += f"**Error:** {data['error']}\n\n"
        
        # Recommendations
        report += "## Recommendations\n\n"
        
        # Find best performers
        successful_results = {k: v for k, v in results.items() if "error" not in v}
        if successful_results:
            best_quality = max(successful_results.items(), key=lambda x: x[1]['quality_metrics']['overall_quality'])
            best_word_count = max(successful_results.items(), key=lambda x: x[1]['word_count'])
            
            report += f"**Best Overall Quality:** {best_quality[0]} ({best_quality[1]['overall_quality']})\n\n"
            report += f"**Most Comprehensive:** {best_word_count[0]} ({best_word_count[1]['word_count']} words)\n\n"
            
            # Style-specific recommendations
            report += "**Style-Specific Recommendations:**\n"
            report += "- For technical project discussions: Use `technical_journal`\n"
            report += "- For research and analysis: Use `research_article`\n"
            report += "- For critiques and opinions: Use `critique`\n"
            report += "- For personal journal entries: Use `journal`\n"
            report += "- For narrative storytelling: Use `narrative`\n\n"
        
        report += "## Conclusion\n\n"
        report += "This comparison demonstrates the importance of using the right summarizer for the right content type. "
        report += "Each summarizer has its strengths and is optimized for specific use cases. "
        report += "The specialized summarizers (technical_journal, research_article, critique) provide the most appropriate content structure for their respective domains.\n"
        
        # Save report
        report_path = self.output_dir / "comprehensive_comparison_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report_path
    
    def _generate_summary_statistics(self, results: Dict[str, Any]):
        """Generate summary statistics JSON file."""
        stats = {
            "total_summarizers": len(self.summarizers),
            "successful_summarizers": len([r for r in results.values() if "error" not in r]),
            "failed_summarizers": len([r for r in results.values() if "error" in r]),
            "word_counts": {name: data.get('word_count', 0) for name, data in results.items() if "error" not in data},
            "quality_ratings": {name: data.get('overall_quality', 'Unknown') for name, data in results.items() if "error" not in data},
            "average_word_count": sum(data.get('word_count', 0) for data in results.values() if "error" not in data) / max(1, len([r for r in results.values() if "error" not in r]))
        }
        
        with open(self.output_dir / "summary_statistics.json", 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)


def run_comprehensive_comparison(conversation: NormalizedConversation, output_dir: Path = Path("dist/comparison")) -> Path:
    """Public interface to run comprehensive comparison."""
    comparison = ComprehensiveComparison(output_dir)
    return comparison.run_comprehensive_comparison(conversation)
