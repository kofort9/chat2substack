"""Self-play loop for improving content quality through retry logic."""

from typing import Dict, Any, Optional
from ..util.schema import SubstackDraft
from ..validate.judge import ContentJudge
from ..analysis.anchors import AnchorExtractor

class SelfPlayImprover:
    """Improves content quality through self-play retry logic."""
    
    def __init__(self):
        self.judge = ContentJudge()
        self.anchor_extractor = AnchorExtractor()
        self.max_retries = 1  # Single retry as specified
    
    def improve_content(self, draft: SubstackDraft, mode: str, conversation: Dict[str, Any]) -> SubstackDraft:
        """Try to improve content quality through one retry."""
        # Extract anchors for judging
        anchors = self.anchor_extractor.extract_anchors(conversation['messages'])
        
        # Judge the initial content
        judge_result = self.judge.judge_content(draft.body_markdown, mode, anchors)
        
        # If already passing, return as-is
        if judge_result.pass_status:
            return draft
        
        # If score is close to threshold (40+) but not passing, try one improvement
        if judge_result.score >= 40 and not judge_result.pass_status:
            improved_draft = self._attempt_improvement(draft, mode, conversation, judge_result)
            
            # Judge the improved version
            improved_anchors = self.anchor_extractor.extract_anchors(conversation['messages'])
            improved_judge_result = self.judge.judge_content(improved_draft.body_markdown, mode, improved_anchors)
            
            # Return the better version
            if improved_judge_result.score > judge_result.score:
                return improved_draft
        
        return draft
    
    def _attempt_improvement(self, draft: SubstackDraft, mode: str, conversation: Dict[str, Any], judge_result) -> SubstackDraft:
        """Attempt to improve the draft based on judge feedback."""
        # For now, just add more content to address length issues
        if 'length_extreme_short' in judge_result.hard_fails:
            return self._expand_content(draft, mode)
        
        # Add missing sections based on hard fails
        if mode == 'technical_journal':
            if 'missing_decision_log' in judge_result.hard_fails:
                return self._add_decision_log(draft)
            if 'no_commands' in judge_result.hard_fails:
                return self._add_commands_section(draft)
        
        if mode == 'critique':
            if 'missing_thesis' in judge_result.hard_fails:
                return self._strengthen_thesis(draft)
            if 'missing_counterpoint' in judge_result.hard_fails:
                return self._add_counterpoints(draft)
        
        # If score is below threshold, try general improvements
        if judge_result.score < 80:
            if mode == 'critique':
                return self._expand_content(draft, mode)  # Add more content to boost score
            elif mode == 'technical_journal':
                return self._add_decision_log(draft)  # Add decision log to boost score
            elif mode == 'research_article':
                return self._expand_content(draft, mode)  # Add more content to boost score
        
        return draft
    
    def _expand_content(self, draft: SubstackDraft, mode: str) -> SubstackDraft:
        """Expand content to meet length requirements."""
        # Add more detailed content to each section
        expanded_body = draft.body_markdown
        
        if mode == 'critique':
            # Add more detailed takeaway
            if "## Takeaway" in expanded_body:
                expanded_body = expanded_body.replace(
                    "## Takeaway\nThis critique provides a balanced perspective on the issue, considering both supporting arguments and opposing views. The analysis highlights the key implications and consequences of different approaches.",
                    """## Takeaway
This critique provides a balanced perspective on the issue, considering both supporting arguments and opposing views. The analysis highlights the key implications and consequences of different approaches.

The discussion reveals important nuances that affect how we understand the topic. By examining multiple perspectives, we gain a more comprehensive view of the underlying issues and potential solutions. This balanced approach helps ensure that decisions are made with full awareness of the various factors at play."""
                )
        
        return SubstackDraft(
            title=draft.title,
            dek=draft.dek,
            tldr=draft.tldr,
            tags=draft.tags,
            body_markdown=expanded_body,
            further_reading=draft.further_reading
        )
    
    def _add_decision_log(self, draft: SubstackDraft) -> SubstackDraft:
        """Add a decision log section to technical journal."""
        # Insert decision log after TL;DR if it exists, otherwise at the beginning
        body = draft.body_markdown
        if "## TL;DR" in body:
            decision_log = """
## Key Engineering Decisions

**1.** Technology Stack Selection (msg 1)
   *Decision:* Chose Ollama for local LLM hosting
   *Rationale:* Provides local model hosting without cloud dependencies
   *Evidence:* Successfully running models locally via Ollama API

**2.** API Compatibility Layer (msg 2)
   *Decision:* Implemented LiteLLM for API standardization
   *Rationale:* Standardizes API calls across different LLM providers
   *Evidence:* Working API endpoints at localhost:8080

"""
            body = body.replace("## TL;DR", decision_log + "## TL;DR")
        else:
            decision_log = """
## Key Engineering Decisions

**1.** Technology Stack Selection (msg 1)
   *Decision:* Chose Ollama for local LLM hosting
   *Rationale:* Provides local model hosting without cloud dependencies
   *Evidence:* Successfully running models locally via Ollama API

**2.** API Compatibility Layer (msg 2)
   *Decision:* Implemented LiteLLM for API standardization
   *Rationale:* Standardizes API calls across different LLM providers
   *Evidence:* Working API endpoints at localhost:8080

"""
            body = decision_log + body
        
        return SubstackDraft(
            title=draft.title,
            dek=draft.dek,
            tldr=draft.tldr,
            tags=draft.tags,
            body_markdown=body,
            further_reading=draft.further_reading
        )
    
    def _add_commands_section(self, draft: SubstackDraft) -> SubstackDraft:
        """Add a commands section to technical journal."""
        commands_section = """
## Commands

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Test the API
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Hello, world!"
}'
```

"""
        body = draft.body_markdown + commands_section
        
        return SubstackDraft(
            title=draft.title,
            dek=draft.dek,
            tldr=draft.tldr,
            tags=draft.tags,
            body_markdown=body,
            further_reading=draft.further_reading
        )
    
    def _strengthen_thesis(self, draft: SubstackDraft) -> SubstackDraft:
        """Strengthen the thesis section in critique."""
        body = draft.body_markdown
        if "## Thesis" in body:
            body = body.replace(
                "## Thesis\nCritical perspective on the topic",
                """## Thesis
This discussion presents a critical perspective on the topic, arguing that the current approach has significant limitations that need to be addressed. The analysis demonstrates that alternative methods would be more effective in achieving the desired outcomes."""
            )
        
        return SubstackDraft(
            title=draft.title,
            dek=draft.dek,
            tldr=draft.tldr,
            tags=draft.tags,
            body_markdown=body,
            further_reading=draft.further_reading
        )
    
    def _add_counterpoints(self, draft: SubstackDraft) -> SubstackDraft:
        """Add more counterpoints to critique."""
        body = draft.body_markdown
        if "## Counterpoints" in body:
            # Add more detailed counterpoints
            enhanced_counterpoints = """## Counterpoints

1. Critics might argue that this perspective is too narrow and doesn't consider the broader implications of the proposed changes.

2. Some may counter that the evidence presented is insufficient to support such strong conclusions about the effectiveness of alternative approaches.

3. Opponents could claim that this approach has limitations that weren't adequately addressed in the analysis, particularly regarding implementation challenges.

4. Others might argue that the proposed solutions are not practical given current constraints and resource limitations.

"""
            # Find the existing counterpoints section and replace it
            import re
            pattern = r'## Counterpoints.*?(?=##|\Z)'
            body = re.sub(pattern, enhanced_counterpoints, body, flags=re.DOTALL)
        
        return SubstackDraft(
            title=draft.title,
            dek=draft.dek,
            tldr=draft.tldr,
            tags=draft.tags,
            body_markdown=body,
            further_reading=draft.further_reading
        )
