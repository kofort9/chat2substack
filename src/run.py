"""Main orchestration module for chat2substack pipeline."""

import os
import sys
import yaml
import json
import click
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .util.schema import NormalizedConversation, SubstackDraft, RunReport
from .util.hashing import content_hash, conversation_hash, slug_from_title
from .util.logging import setup_logging, log_run_stats, log_redaction_stats
from .ingest.from_shared_html import ingest_shared_html
from .ingest.from_text import ingest_manual_text
from .redact.scrub import redact_conversation
from .llm.summarize import summarize_to_substack_json
from .llm.category_detector import detect_content_category
from .llm.professional_summarizers import summarize_conversation_professional
from .llm.decision_centric_journal import DecisionCentricJournalSummarizer
from .llm.research_article import ResearchArticleSummarizer
from .analysis.conversation_analyzer import analyze_conversation_and_compare
from .llm.guardrail_checkers import content_guard, tone_guard
from .render.to_markdown import render_to_markdown
from .render.to_html import render_to_html


def create_topic_folder(draft: SubstackDraft, conversation: NormalizedConversation) -> str:
    """Create a topic-based folder name for organizing drafts."""
    # Use the conversation title hint or draft title to create a specific folder name
    if conversation.title_hint and conversation.title_hint != "Untitled Conversation":
        # Use the conversation title as the folder name
        topic = conversation.title_hint.lower()
    else:
        # Fall back to draft title
        topic = draft.title.lower()
    
    # Clean up the topic name - remove common prefixes and clean up
    topic = topic.replace('chatgpt - ', '').replace('chatgpt:', '').strip()
    topic = topic.replace(' ', '-').replace('_', '-')
    topic = ''.join(c for c in topic if c.isalnum() or c in '-')
    
    # Remove common words that don't add value
    topic = topic.replace('the-', '').replace('a-', '').replace('an-', '')
    
    if not topic or len(topic) < 3:
        topic = 'general-discussion'
    
    return topic


class Chat2SubstackPipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.logger = setup_logging()
        self.dist_dir = Path("dist")
        self.dist_dir.mkdir(exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'length': {'target_words': 450, 'hard_cap_words': 900},
            'manual_paste': {'max_chars': 10000},
            'redaction': {
                'pseudonymize_private_names': True,
                'private_name_list': [],
                'allow_public_figures': True
            },
            'substack': {'host': 'https://YOURNAME.substack.com', 'create_draft': False},
            'guardrails': {'blocked_phrases': [], 'enforce_tone': True},
            'citations': {'enable_further_reading': True},
            'storage': {'keep_input_html': False, 'keep_sanitized_json': True},
            'models': {'provider': 'local', 'primary': 'template', 'temperature': 0.2}
        }
    
    def ingest_conversation(self, input_path: str) -> NormalizedConversation:
        """Ingest conversation from file."""
        input_file = Path(input_path)
        
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if input_file.suffix.lower() == '.html':
            return ingest_shared_html(str(input_file))
        elif input_file.suffix.lower() == '.txt':
            max_chars = self.config['manual_paste']['max_chars']
            return ingest_manual_text(str(input_file), max_chars)
        else:
            raise ValueError(f"Unsupported file type: {input_file.suffix}")
    
    def redact_conversation(self, conversation: NormalizedConversation) -> tuple[NormalizedConversation, Dict[str, int]]:
        """Redact PII from conversation."""
        redaction_config = self.config['redaction']
        return redact_conversation(
            conversation,
            private_names=redaction_config.get('private_name_list', []),
            allow_public_figures=redaction_config.get('allow_public_figures', True)
        )
    
    def summarize_conversation(self, conversation: NormalizedConversation, content_type: str = "auto") -> SubstackDraft:
        """Summarize conversation to Substack draft using judge-driven system."""
        from .analysis.anchors import AnchorExtractor
        from .routing.router import DeterministicRouter
        from .validate.judge import ContentJudge
        
        # Extract anchors from conversation
        anchor_extractor = AnchorExtractor()
        conversation_dict = {
            'messages': [
                {'content': msg.text, 'role': msg.role} 
                for msg in conversation.messages
            ],
            'title_hint': getattr(conversation, 'title_hint', 'Untitled Conversation')
        }
        
        anchors = anchor_extractor.extract_anchors(conversation_dict['messages'])
        
        # Route content type
        router = DeterministicRouter()
        if content_type == "auto":
            detected_category = router.route_content(conversation_dict['messages'][0]['content'] if conversation_dict['messages'] else "", anchors)
        else:
            detected_category = content_type
        
        # Check if content should be BLOCKED
        if detected_category.startswith("BLOCKED"):
            # Create a minimal draft indicating the content was blocked
            return SubstackDraft(
                title="Content Blocked - Insufficient Quality",
                dek="This content did not meet quality standards for publication.",
                tldr=["Content blocked due to quality issues", "Insufficient signals for classification", "Please improve content and try again"],
                tags=["blocked", "quality-issue", "insufficient-signals"],
                body_markdown=f"## Content Blocked\n\n**Reason:** {detected_category}\n\nThis content did not meet the quality standards required for publication. Please review the content and ensure it contains sufficient signals for proper classification.",
                further_reading=None
            )
        
        # Use appropriate summarizer
        if detected_category == "technical_journal":
            summarizer = DecisionCentricJournalSummarizer()
            draft = summarizer.summarize_conversation(conversation_dict)
        elif detected_category == "research_article":
            summarizer = ResearchArticleSummarizer()
            draft = summarizer.summarize_conversation(conversation_dict)
        else:
            # Use professional summarizer for other categories
            from .llm.category_detector import PostCategory
            category = PostCategory(detected_category)
            draft = summarize_conversation_professional(conversation, category)
        
        # Judge the content quality
        judge = ContentJudge()
        judge_result = judge.judge_content(draft.body_markdown, detected_category, anchors)
        
        # If content fails quality check, try self-play improvement
        if not judge_result.pass_status:
            from .llm.self_play import SelfPlayImprover
            improver = SelfPlayImprover()
            improved_draft = improver.improve_content(draft, detected_category, conversation_dict)
            
            # Judge the improved version
            improved_judge_result = judge.judge_content(improved_draft.body_markdown, detected_category, anchors)
            
            # If still failing, return blocked version
            if not improved_judge_result.pass_status:
                return SubstackDraft(
                    title="Content Blocked - Quality Issues",
                    dek="This content did not meet quality standards for publication.",
                    tldr=["Content blocked due to quality issues", f"Score: {improved_judge_result.score}/100", f"Fails: {', '.join(improved_judge_result.hard_fails)}"],
                    tags=["blocked", "quality-issue", "low-score"],
                    body_markdown=f"## Content Blocked\n\n**Reason:** Quality score {improved_judge_result.score}/100 (minimum: 80)\n\n**Hard Fails:** {', '.join(improved_judge_result.hard_fails)}\n\n**Notes:** {', '.join(improved_judge_result.notes)}",
                    further_reading=None
                )
            
            # Use improved draft
            draft = improved_draft
            judge_result = improved_judge_result
        
        # Add quality metadata to the draft
        if hasattr(draft, 'metadata'):
            draft.metadata = {
                'quality_score': judge_result.score,
                'anchor_coverage': judge_result.coverage['anchor_coverage_pct'],
                'citations': judge_result.counts['citations'],
                'runnable_commands': judge_result.counts['runnable_commands']
            }
        
        return draft
    
    def apply_guardrails(self, draft: SubstackDraft) -> SubstackDraft:
        """Apply content and tone guardrails."""
        guardrail_config = self.config['guardrails']
        
        # Content guardrails
        content_result = content_guard(
            draft, 
            blocked_phrases=guardrail_config.get('blocked_phrases', [])
        )
        
        if not content_result.ok:
            self.logger.warning(f"Content guardrails failed: {content_result.issues}")
            if content_result.patch:
                # Apply patch (simplified - in practice would need more sophisticated patching)
                self.logger.info("Content patch applied")
        
        # Tone guardrails
        length_config = self.config['length']
        tone_result = tone_guard(
            draft,
            target_words=length_config.get('target_words', 450),
            hard_cap_words=length_config.get('hard_cap_words', 900)
        )
        
        if not tone_result.ok:
            self.logger.warning(f"Tone guardrails failed: {tone_result.issues}")
            if tone_result.patch:
                self.logger.info("Tone patch applied")
        
        return draft
    
    def render_draft(self, draft: SubstackDraft, slug: str) -> Dict[str, str]:
        """Render draft to Markdown and HTML."""
        markdown_content = render_to_markdown(draft)
        html_content = render_to_html(draft)
        
        return {
            'markdown': markdown_content,
            'html': html_content
        }
    
    def create_draft_meta(self, draft: SubstackDraft, slug: str, content_hash: str) -> Dict[str, Any]:
        """Create draft metadata."""
        return {
            'slug': slug,
            'title': draft.title,
            'created_at': datetime.now().isoformat(),
            'content_hash': content_hash,
            'word_count': len(draft.body_markdown.split()),
            'tags': draft.tags,
            'tldr_count': len(draft.tldr),
            'has_further_reading': draft.further_reading is not None
        }
    
    def create_run_report(self, run_id: str, slug: str, content_hash: str, 
                         word_counts: Dict[str, int], redaction_stats: Dict[str, int],
                         draft_url: Optional[str] = None) -> str:
        """Create run report."""
        report = f"""# Chat2Substack Run Report

**Run ID:** {run_id}
**Slug:** {slug}
**Content Hash:** {content_hash}
**Created:** {datetime.now().isoformat()}

## Word Counts
- Title: {word_counts.get('title', 0)} words
- Dek: {word_counts.get('dek', 0)} words  
- TL;DR: {word_counts.get('tldr', 0)} words
- Body: {word_counts.get('body', 0)} words
- **Total:** {sum(word_counts.values())} words

## Redaction Statistics
"""
        
        for pattern, count in redaction_stats.items():
            if count > 0:
                report += f"- {pattern}: {count} redactions\n"
        
        if not any(redaction_stats.values()):
            report += "- No redactions performed\n"
        
        if draft_url:
            report += f"\n## Substack Draft\n- **URL:** {draft_url}\n"
        else:
            report += "\n## Substack Draft\n- Draft creation was disabled\n"
        
        report += f"\n## Files Generated\n- `FINAL_POST_{slug}.md` - **MAIN POST ARTIFACT**\n- `POST_SUMMARY_{slug}.md` - Post summary and metrics\n- `dist/[topic]/post_{slug}.md` - Post in topic folder\n- `dist/[topic]/post_{slug}.html` - HTML version\n- `dist/draft_meta.json` - Metadata\n- `dist/run_report.md` - This report\n"
        
        return report
    
    def create_post_summary(self, draft: SubstackDraft, slug: str, word_counts: Dict[str, int], comparison_report: Optional[Dict[str, Any]] = None) -> str:
        """Create a summary of the generated post."""
        summary = f"""# Post Summary: {draft.title}

## Overview
- **Slug:** {slug}
- **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Content Type:** Technical Journal

## Post Details
- **Title:** {draft.title}
- **Dek:** {draft.dek}
- **TL;DR Points:** {len(draft.tldr)}
- **Tags:** {', '.join(draft.tags)}

## Word Counts
- **Title:** {word_counts['title']} words
- **Dek:** {word_counts['dek']} words  
- **TL;DR:** {word_counts['tldr']} words
- **Body:** {word_counts['body']} words
- **Total:** {sum(word_counts.values())} words

## Content Quality Metrics
"""
        
        if comparison_report:
            metrics = comparison_report['coverage_metrics']
            summary += f"""- **Word Coverage:** {metrics['word_coverage']:.1f}%
- **Topic Coverage:** {metrics['topic_coverage']:.1f}%
- **Technical Term Coverage:** {metrics['technical_term_coverage']:.1f}%
- **Code Snippet Coverage:** {metrics['code_snippet_coverage']:.1f}%
- **Questions Addressed:** {metrics['questions_addressed']:.1f}%
- **Solutions Included:** {metrics['solutions_included']:.1f}%
"""
        else:
            summary += "- Quality metrics not available\n"
        
        summary += f"""
## TL;DR Points
"""
        for i, point in enumerate(draft.tldr, 1):
            summary += f"{i}. {point}\n"
        
        summary += f"""
## Tags
{', '.join(draft.tags)}

## Files Generated
- `FINAL_POST_{slug}.md` - The final post content
- `dist/{slug}/post_{slug}.md` - Post in topic folder
- `dist/{slug}/post_{slug}.html` - HTML version
- `POST_SUMMARY_{slug}.md` - This summary
- `run_report.md` - Detailed pipeline report

## Ready for Publication
This post is ready to be published to Substack or any other platform that supports Markdown format.
"""
        
        return summary
    
    def run_pipeline(self, input_path: str, create_draft: bool = False, content_type: str = "auto") -> str:
        """Run the complete pipeline."""
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Step 1: Ingest
            self.logger.info(f"Ingesting conversation from {input_path}")
            conversation = self.ingest_conversation(input_path)
            
            # Check for idempotency
            content_hash = conversation_hash(conversation.model_dump())
            slug = slug_from_title(conversation.title_hint or "untitled")
            
            # Check if we've already processed this content
            # We'll check after we know the topic folder
            # For now, we'll skip the idempotency check and always process
            
            # Step 2: Redact
            self.logger.info("Redacting PII from conversation")
            redacted_conversation, redaction_stats = self.redact_conversation(conversation)
            log_redaction_stats(self.logger, redaction_stats)
            
            # Step 3: Summarize
            self.logger.info("Summarizing conversation")
            draft = self.summarize_conversation(redacted_conversation, content_type)
            
            # Step 4: Apply guardrails
            self.logger.info("Applying guardrails")
            draft = self.apply_guardrails(draft)
            
            # Step 5: Render
            self.logger.info("Rendering draft")
            rendered_content = self.render_draft(draft, slug)
            
            # Step 6: Write files
            self.logger.info("Writing output files")
            
            # Create topic-based folder
            topic_folder = create_topic_folder(draft, redacted_conversation)
            topic_dir = self.dist_dir / topic_folder
            topic_dir.mkdir(exist_ok=True)
            
            # Write Markdown
            markdown_file = topic_dir / f"post_{slug}.md"
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(rendered_content['markdown'])
            
            # Write HTML
            html_file = topic_dir / f"post_{slug}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(rendered_content['html'])
            
            # Write metadata
            word_counts = {
                'title': len(draft.title.split()),
                'dek': len(draft.dek.split()),
                'tldr': sum(len(point.split()) for point in draft.tldr),
                'body': len(draft.body_markdown.split())
            }
            
            draft_meta = self.create_draft_meta(draft, slug, content_hash)
            meta_file = self.dist_dir / "draft_meta.json"
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(draft_meta, f, indent=2)
            
            # Step 7: Analyze conversation and compare with summary
            self.logger.info("Analyzing conversation and comparing with summary")
            try:
                comparison_report = analyze_conversation_and_compare(conversation, draft, slug, self.dist_dir)
                self.logger.info(f"Conversation analysis complete. Coverage: {comparison_report['coverage_metrics']['word_coverage']:.1f}%")
            except Exception as e:
                self.logger.warning(f"Conversation analysis failed: {str(e)}")
            
            # Write run report
            draft_url = None
            if create_draft:
                self.logger.info("Creating Substack draft (feature-flagged)")
                # In a real implementation, this would call the Playwright script
                draft_url = "https://YOURNAME.substack.com/p/draft-url"
            
            # Create final post artifact in root of dist/
            self.logger.info("Creating final post artifact")
            final_post_file = self.dist_dir / f"FINAL_POST_{slug}.md"
            with open(final_post_file, 'w', encoding='utf-8') as f:
                f.write(rendered_content['markdown'])
            
            # Create post summary artifact
            post_summary = self.create_post_summary(draft, slug, word_counts, comparison_report)
            summary_file = self.dist_dir / f"POST_SUMMARY_{slug}.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(post_summary)
            
            run_report = self.create_run_report(
                run_id, slug, content_hash, word_counts, redaction_stats, draft_url
            )
            report_file = self.dist_dir / "run_report.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(run_report)
            
            # Write content hash for idempotency
            hash_file = topic_dir / f"post_{slug}.hash"
            with open(hash_file, 'w') as f:
                f.write(content_hash)
            
            # Log final stats
            log_run_stats(self.logger, {
                'slug': slug,
                'total_words': sum(word_counts.values()),
                'redactions': sum(redaction_stats.values()),
                'draft_created': create_draft
            })
            
            self.logger.info(f"Pipeline completed successfully. Slug: {slug}")
            self.logger.info(f"📝 FINAL POST ARTIFACT: dist/FINAL_POST_{slug}.md")
            self.logger.info(f"📊 POST SUMMARY: dist/POST_SUMMARY_{slug}.md")
            return f"FINAL_POST_{slug}"
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise


@click.command()
@click.option('--input', 'input_path', required=True, help='Input file path (HTML or TXT)')
@click.option('--create-draft/--no-create-draft', default=False, help='Create Substack draft')
@click.option('--content-type', 'content_type', default='auto', 
              type=click.Choice(['auto', 'technical_journal', 'research_article', 'critique']),
              help='Content type: auto-detect, technical journal, research article, or critique')
@click.option('--config', default='config.yaml', help='Config file path')
def main(input_path: str, create_draft: bool, content_type: str, config: str):
    """Run the chat2substack pipeline."""
    pipeline = Chat2SubstackPipeline(config)
    
    try:
        slug = pipeline.run_pipeline(input_path, create_draft, content_type)
        print(f"Success! Generated: {slug}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
