"""Judge-driven validators with calibrated 0-100 scoring."""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ..analysis.anchors import AnchorExtractor, Anchor

@dataclass
class JudgeResult:
    """Result of judge validation."""
    mode: str
    score: int  # 0-100
    pass_status: bool
    hard_fails: List[str]
    subscores: Dict[str, int]
    coverage: Dict[str, Any]
    counts: Dict[str, int]
    notes: List[str]

class ContentJudge:
    """Judge-driven content validator with hard rules and calibrated scoring."""
    
    def __init__(self):
        self.anchor_extractor = AnchorExtractor()
        
        # Regex patterns for section detection
        self.section_patterns = {
            'tldr': r'^##\s*TL;?DR\b',
            'decision_log': r'^##\s*(Decision\s+Log|Key\s+Decisions|Key\s+Engineering\s+Decisions)\b',
            'commands': r'^##\s*(Exact\s+Commands|Commands|How\s+to\s+Reproduce)\b',
            'open_questions': r'^##\s*(Open\s+Questions|Next|Next\s+Work|Future\s+Work)\b',
            'tags': r'^##\s*Tags?\b',
            'abstract': r'^##\s*(Abstract|Dek)\b',
            'research_questions': r'^##\s*(Research\s+Question|Questions)\b',
            'findings': r'^##\s*(Findings|Key\s+Insights|Results)\b',
            'thesis': r'^##\s*(Thesis|Claim|Stance)\b',
            'counterpoints': r'^##\s*(Counterpoints|Counter-?arguments|Steelman)\b'
        }
        
        # Command detection patterns
        self.cmd_line_pattern = r'(?m)^(?:\$|\s{0,3}(?:curl|bash|sh|ollama|litellm|pytest|git|python3?|docker|brew)\b).*'
        self.cmd_block_pattern = r'```(?:bash|sh|zsh|shell)?\n[\s\S]*?```'
        self.has_flag_pattern = r'\s--[A-Za-z0-9_-]+'
        
        # Citation pattern
        self.citation_pattern = r'\(msg\s+\d+\)'
        
        # Research domain terms
        self.research_terms_pattern = r'\b(dataset|benchmark|paper|citation|RAG|graphRAG|Ray|Anyscale|architecture|method|methodology|experiment|reading\s+list|evaluation|ablation|baseline|fine-?tuning)\b'
        
        # Critique tokens
        self.critique_tokens_pattern = r'\b(thesis|claim|counterpoint|counter-?argument|stance|agree|disagree|critique|opinion|believe|think|argue|contend)\b'
        
        # Model patterns
        self.ollama_pattern = r'\bollama\b'
        self.litellm_pattern = r'\blitellm\b'
        self.quant_pattern = r'\bq[45]_K_M\b'
        
        # Decision patterns
        self.decision_pattern = r'\b(shipped|bypass|decided|rollback|we used|we\'ll use|chose|selected|went with)\b'
    
    def judge_content(self, content: str, mode: str, anchors: List[Anchor]) -> JudgeResult:
        """Judge content quality with calibrated scoring."""
        
        # Calculate subscores
        section_completeness = self._score_section_completeness(content, mode)
        anchor_coverage = self._score_anchor_coverage(content, anchors)
        evidence_density = self._score_evidence_density(content)
        mode_specific = self._score_mode_specific(content, mode, anchors)
        no_filler_penalty = self._score_no_filler(content)
        length_fit = self._score_length_fit(content, mode)
        
        # Calculate counts
        counts = self._calculate_counts(content, anchors)
        
        # Calculate coverage
        coverage = self.anchor_extractor.get_anchor_coverage(anchors, content)
        
        # Check for hard fails
        hard_fails = self._check_hard_fails(content, mode, anchors, counts, coverage)
        
        # Calculate total score
        total_score = (
            section_completeness + 
            anchor_coverage + 
            evidence_density + 
            mode_specific + 
            no_filler_penalty + 
            length_fit
        )
        
        # Ensure score is within bounds
        total_score = max(0, min(100, total_score))
        
        # Determine pass status
        pass_status = len(hard_fails) == 0 and total_score >= 80
        
        # Generate notes
        notes = self._generate_notes(hard_fails, counts, coverage, mode)
        
        return JudgeResult(
            mode=mode,
            score=total_score,
            pass_status=pass_status,
            hard_fails=hard_fails,
            subscores={
                'section_completeness': section_completeness,
                'anchor_coverage': anchor_coverage,
                'evidence_density': evidence_density,
                'mode_specific': mode_specific,
                'no_filler_penalty': no_filler_penalty,
                'length_fit': length_fit
            },
            coverage=coverage,
            counts=counts,
            notes=notes
        )
    
    def _score_section_completeness(self, content: str, mode: str) -> int:
        """Score section completeness (0-25 points)."""
        required_sections = self._get_required_sections(mode)
        present_sections = 0
        
        for section_name, pattern in self.section_patterns.items():
            if section_name in required_sections:
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    present_sections += 1
        
        completeness_ratio = present_sections / len(required_sections) if required_sections else 1.0
        return int(completeness_ratio * 25)
    
    def _get_required_sections(self, mode: str) -> List[str]:
        """Get required sections for each mode."""
        if mode == 'technical_journal':
            return ['tldr', 'decision_log', 'commands', 'open_questions', 'tags']
        elif mode == 'research_article':
            return ['abstract', 'research_questions', 'findings', 'tags']
        elif mode == 'critique':
            return ['thesis', 'counterpoints', 'tags']
        return []
    
    def _score_anchor_coverage(self, content: str, anchors: List[Anchor]) -> int:
        """Score anchor coverage (0-25 points)."""
        coverage = self.anchor_extractor.get_anchor_coverage(anchors, content)
        coverage_pct = coverage['anchor_coverage_pct']
        
        if coverage_pct >= 80:
            return 25
        elif coverage_pct >= 60:
            return 20
        elif coverage_pct >= 40:
            return 15
        elif coverage_pct >= 20:
            return 10
        else:
            return 5
    
    def _score_evidence_density(self, content: str) -> int:
        """Score evidence density (0-15 points)."""
        citations = len(re.findall(self.citation_pattern, content))
        word_count = len(content.split())
        citations_per_200_words = (citations / word_count * 200) if word_count > 0 else 0
        
        return min(int(citations_per_200_words * 5), 15)
    
    def _score_mode_specific(self, content: str, mode: str, anchors: List[Anchor]) -> int:
        """Score mode-specific requirements (0-25 points)."""
        if mode == 'technical_journal':
            return self._score_technical_journal(content, anchors)
        elif mode == 'research_article':
            return self._score_research_article(content, anchors)
        elif mode == 'critique':
            return self._score_critique(content, anchors)
        return 0
    
    def _score_technical_journal(self, content: str, anchors: List[Anchor]) -> int:
        """Score technical journal specific requirements."""
        score = 0
        
        # Check for runnable commands
        cmd_matches = re.findall(self.cmd_line_pattern, content) + re.findall(self.cmd_block_pattern, content)
        if len(cmd_matches) >= 2:
            score += 10
            # Check for commands with flags
            flag_commands = [cmd for cmd in cmd_matches if re.search(self.has_flag_pattern, cmd)]
            if len(flag_commands) >= 1:
                score += 5
        
        # Check for model mentions
        if re.search(self.ollama_pattern, content, re.IGNORECASE):
            score += 5
        if re.search(self.litellm_pattern, content, re.IGNORECASE):
            score += 5
        
        # Check for quant tags
        if re.search(self.quant_pattern, content):
            score += 5
        
        # Check for shipping decision
        if re.search(self.decision_pattern, content, re.IGNORECASE):
            score += 5
        
        return min(score, 25)
    
    def _score_research_article(self, content: str, anchors: List[Anchor]) -> int:
        """Score research article specific requirements."""
        score = 0
        
        # Check for domain terms
        domain_terms = len(re.findall(self.research_terms_pattern, content, re.IGNORECASE))
        if domain_terms >= 3:
            score += 10
        
        # Check for findings with citations
        findings_section = re.search(r'##\s*(Findings|Key\s+Insights)', content, re.IGNORECASE)
        if findings_section:
            findings_text = content[findings_section.end():]
            next_section = re.search(r'##\s+', findings_text)
            if next_section:
                findings_text = findings_text[:next_section.start()]
            
            bullets = re.findall(r'^\s*[-*]\s+', findings_text, re.MULTILINE)
            cited_bullets = [bullet for bullet in bullets if re.search(self.citation_pattern, bullet)]
            
            if len(bullets) >= 3 and len(cited_bullets) >= 2:
                score += 10
        
        # Check for concrete tooling mentions
        tooling_terms = ['Ray', 'RAG', 'FAISS', 'LangChain', 'Anyscale']
        tooling_mentions = sum(1 for term in tooling_terms if re.search(rf'\b{term}\b', content, re.IGNORECASE))
        if tooling_mentions >= 1:
            score += 5
        
        return min(score, 25)
    
    def _score_critique(self, content: str, anchors: List[Anchor]) -> int:
        """Score critique specific requirements."""
        score = 0
        
        # Check for explicit stance
        stance_patterns = [
            r'\b(I argue|I contend|I agree|I disagree|My thesis|The claim)\b',
            r'\b(I believe|I think|In my opinion)\b'
        ]
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in stance_patterns):
            score += 10
        
        # Check for counterpoints with citations
        counterpoints_section = re.search(r'##\s*(Counterpoints|Counter-?arguments)', content, re.IGNORECASE)
        if counterpoints_section:
            counterpoints_text = content[counterpoints_section.end():]
            next_section = re.search(r'##\s+', counterpoints_text)
            if next_section:
                counterpoints_text = counterpoints_text[:next_section.start()]
            
            if re.search(self.citation_pattern, counterpoints_text):
                score += 10
        
        # Check for consequence terms
        consequence_terms = ['risk', 'cost', 'harm', 'benefit', 'trade-off', 'consequence', 'impact']
        consequence_mentions = sum(1 for term in consequence_terms if re.search(rf'\b{term}\b', content, re.IGNORECASE))
        if consequence_mentions >= 2:
            score += 5
        
        return min(score, 25)
    
    def _score_no_filler(self, content: str) -> int:
        """Score no filler penalty (-10 to 0 points)."""
        banned_phrases = self.anchor_extractor.detect_banned_phrases(content)
        penalty = min(len(banned_phrases) * -5, -10)
        return penalty
    
    def _score_length_fit(self, content: str, mode: str) -> int:
        """Score length fit (0-10 points)."""
        word_count = len(content.split())
        
        # Mode-specific length targets - very lenient for synthetic testing
        length_targets = {
            'technical_journal': (100, 1400),
            'research_article': (100, 1000),
            'critique': (100, 1100)
        }
        
        if mode not in length_targets:
            return 5
        
        min_words, max_words = length_targets[mode]
        
        if min_words <= word_count <= max_words:
            return 10
        elif min_words * 0.5 <= word_count <= max_words * 1.2:
            return 5
        else:
            return 0
    
    def _calculate_counts(self, content: str, anchors: List[Anchor]) -> Dict[str, int]:
        """Calculate various counts for reporting."""
        citations = len(re.findall(self.citation_pattern, content))
        
        # Count runnable commands
        cmd_matches = re.findall(self.cmd_line_pattern, content) + re.findall(self.cmd_block_pattern, content)
        runnable_commands = len(cmd_matches)
        
        # Count unique sections present
        unique_sections = 0
        for pattern in self.section_patterns.values():
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                unique_sections += 1
        
        # Count banned phrases
        banned_phrases = self.anchor_extractor.detect_banned_phrases(content)
        banned_count = len(banned_phrases)
        
        return {
            'citations': citations,
            'runnable_commands': runnable_commands,
            'unique_sections_present': unique_sections,
            'banned_phrases': banned_count
        }
    
    def _check_hard_fails(self, content: str, mode: str, anchors: List[Anchor], counts: Dict[str, int], coverage: Dict[str, Any]) -> List[str]:
        """Check for hard failure conditions."""
        hard_fails = []
        
        # Universal hard fails
        if counts['citations'] < 2:
            hard_fails.append('missing_citations')
        
        if coverage['anchor_coverage_pct'] < 35:
            hard_fails.append('low_anchor_coverage')
        
        if counts['banned_phrases'] > 0:
            hard_fails.append('template_filler_detected')
        
        # Length extremes - be more lenient for synthetic testing
        word_count = len(content.split())
        if word_count < 50:  # Only block if extremely short
            hard_fails.append('length_extreme_short')
        elif word_count > 2000:
            hard_fails.append('length_extreme_long')
        
        # Mode-specific hard fails
        if mode == 'technical_journal':
            if not re.search(self.section_patterns['decision_log'], content, re.MULTILINE | re.IGNORECASE):
                hard_fails.append('missing_decision_log')
            if counts['runnable_commands'] < 2:
                hard_fails.append('no_commands')
            if not re.search(self.decision_pattern, content, re.IGNORECASE):
                hard_fails.append('no_shipping_decision')
        
        elif mode == 'research_article':
            if not re.search(self.section_patterns['abstract'], content, re.MULTILINE | re.IGNORECASE):
                hard_fails.append('missing_abstract_or_dek')
            if not re.search(self.section_patterns['research_questions'], content, re.MULTILINE | re.IGNORECASE):
                hard_fails.append('missing_research_questions')
            if not re.search(self.section_patterns['findings'], content, re.MULTILINE | re.IGNORECASE):
                hard_fails.append('missing_findings_section')
            
            domain_terms = len(re.findall(self.research_terms_pattern, content, re.IGNORECASE))
            if domain_terms < 3:
                hard_fails.append('insufficient_domain_terms')
        
        elif mode == 'critique':
            if not re.search(self.section_patterns['thesis'], content, re.MULTILINE | re.IGNORECASE):
                hard_fails.append('missing_thesis')
            if not re.search(self.section_patterns['counterpoints'], content, re.MULTILINE | re.IGNORECASE):
                hard_fails.append('missing_counterpoint')
        
        return hard_fails
    
    def _generate_notes(self, hard_fails: List[str], counts: Dict[str, int], coverage: Dict[str, Any], mode: str) -> List[str]:
        """Generate human-readable notes and suggestions."""
        notes = []
        
        if hard_fails:
            notes.append(f"Hard fails: {', '.join(hard_fails)}")
        
        if counts['citations'] < 2:
            notes.append(f"Add more citations (found {counts['citations']}, need 2+)")
        
        if coverage['anchor_coverage_pct'] < 50:
            notes.append(f"Low anchor coverage: {coverage['anchor_coverage_pct']:.1f}% (target: 50%+)")
        
        if mode == 'technical_journal' and counts['runnable_commands'] < 2:
            notes.append(f"Add more runnable commands (found {counts['runnable_commands']}, need 2+)")
        
        if counts['banned_phrases'] > 0:
            notes.append(f"Remove template filler phrases ({counts['banned_phrases']} found)")
        
        return notes
