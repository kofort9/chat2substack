"""Content category detection and prompt selection system."""

import re
from typing import Dict, List, Any, Optional, Tuple
from ..util.schema import NormalizedConversation

PostCategory = str  # "technical_journal", "research_article", "critique"

class CategoryDetectionResult:
    """Result of category detection with confidence score."""
    def __init__(self, category: PostCategory, confidence: float, scores: Dict[str, float]):
        self.category = category
        self.confidence = confidence
        self.scores = scores

class ContentCategoryDetector:
    """Detects the type of content and selects appropriate summarizer."""
    
    def __init__(self):
        self.category_indicators = {
            "technical_journal": {
                "keywords": [
                    "project", "built", "created", "developed", "implemented", "coded",
                    "programmed", "prototype", "demo", "app", "tool", "script", "library",
                    "framework", "platform", "system", "feature", "functionality",
                    "github", "repository", "commit", "pull request", "deployment",
                    "testing", "debugging", "optimization", "performance", "sentry",
                    "litellm", "ollama", "api", "config", "yaml", "bash", "command",
                    "pip", "npm", "install", "setup", "configure", "deploy", "run"
                ],
                "patterns": [
                    r"i (built|created|developed|made|designed)",
                    r"working on (a|an|my)",
                    r"project (i|we) (built|created|developed)",
                    r"building (a|an|my)",
                    r"code (i|we) (wrote|developed|created)",
                    r"app (i|we) (built|created|developed)",
                    r"tool (i|we) (built|created|developed)"
                ]
            },
            "research_article": {
                "keywords": [
                    # Academic research terms (more specific)
                    "research findings", "study results", "data analysis", "statistical analysis", 
                    "survey results", "experimental data", "hypothesis testing", "research methodology",
                    "literature review", "academic paper", "peer-reviewed", "published study",
                    "research paper", "thesis", "dissertation", "research report", "empirical evidence",
                    "research demonstrates", "study indicates", "research suggests", "findings show",
                    "research proves", "study confirms", "research validates", "evidence supports",
                    "research contradicts", "study refutes", "correlation analysis", "causal relationship",
                    "research association", "trend analysis", "pattern recognition", "phenomenon study",
                    "research observation", "scientific discovery", "research insight",
                    # Technical research terms (more specific)
                    "dataset analysis", "benchmark study", "research workflow", "research architecture", 
                    "model training", "research pipeline", "research api", "research framework",
                    "algorithm research", "performance evaluation", "research metrics",
                    # Reading and learning terms (more specific)
                    "reading list", "research book", "research author", "research citation", 
                    "research reference", "research source", "research exploration", "research investigation",
                    # Specific research domains (more specific)
                    "ai research", "artificial intelligence research", "machine learning research", 
                    "llm research", "rag research", "distributed research", "parallel research"
                ],
                "patterns": [
                    r"research (on|about|into|shows|indicates|suggests)",
                    r"study (of|on|about|finds|shows|indicates)",
                    r"analysis (of|on|about|reveals|shows|indicates)",
                    r"investigation (into|of|finds|shows|reveals)",
                    r"findings (show|indicate|suggest|reveal|demonstrate)",
                    r"data (shows|indicates|suggests|reveals|demonstrates)",
                    r"according to (research|studies|data|evidence)",
                    r"evidence (shows|indicates|suggests|demonstrates)",
                    r"results (show|indicate|suggest|reveal|demonstrate)",
                    r"the (study|research|analysis|investigation) (shows|finds|indicates)",
                    r"this (research|study|analysis) (shows|indicates|suggests)",
                    r"based on (research|studies|data|evidence|findings)",
                    r"the (data|evidence|findings) (suggests|indicates|shows)",
                    r"research (has|hasn't|has not) (shown|proven|demonstrated)",
                    r"studies (have|haven't|have not) (shown|proven|demonstrated)"
                ]
            },
            "critique": {
                "keywords": [
                    "critique", "review", "opinion", "perspective", "viewpoint",
                    "analysis", "evaluation", "assessment", "judgment", "commentary",
                    "discussion", "debate", "argument", "position", "stance",
                    "agree", "disagree", "support", "oppose", "believe", "think",
                    "feel", "consider", "view", "see", "regard", "perceive",
                    "criticize", "praise", "applaud", "condemn", "endorse", "reject",
                    "approve", "disapprove", "favor", "disfavor", "prefer", "dislike",
                    "good", "bad", "excellent", "terrible", "amazing", "awful",
                    "interesting", "boring", "fascinating", "disappointing", "impressive",
                    "concerning", "worrying", "encouraging", "discouraging", "hopeful",
                    "problematic", "beneficial", "harmful", "useful", "useless"
                ],
                "patterns": [
                    r"i (think|believe|feel|agree|disagree|consider|view|see|regard)",
                    r"my (opinion|perspective|view|belief|stance|position)",
                    r"in my (view|opinion|perspective|belief|estimation)",
                    r"i (support|oppose|criticize|praise|endorse|reject|condemn)",
                    r"this (is|was) (good|bad|excellent|terrible|amazing|awful)",
                    r"i (like|dislike|love|hate|prefer|favor|disfavor) (this|that|it)",
                    r"i (find|consider|think) (this|that|it) (to be|is|was)",
                    r"in my (experience|view|opinion), (this|that|it)",
                    r"i (am|was) (impressed|disappointed|concerned|pleased) (by|with)",
                    r"this (seems|appears|looks) (good|bad|interesting|concerning)",
                    r"i (would|wouldn't) (recommend|suggest|advise) (this|that|it)",
                    r"the (problem|issue|concern|benefit|advantage) (is|with|of)",
                    r"what (i|we) (like|dislike|appreciate|don't like) (about|is)",
                    r"i (think|believe|feel) (that|this|it) (is|was|should|could)",
                    r"this (makes|doesn't make) (sense|sense to me|me think)"
                ]
            }
        }
    
    def detect_category(self, conversation: NormalizedConversation) -> PostCategory:
        """Detect the most likely content category."""
        result = self.detect_category_with_confidence(conversation)
        return result.category
    
    def detect_category_with_confidence(self, conversation: NormalizedConversation) -> CategoryDetectionResult:
        """Detect the most likely content category with confidence scoring."""
        all_text = " ".join([msg.text for msg in conversation.messages])
        text_lower = all_text.lower()
        
        category_scores = {}
        total_possible_score = 0
        
        for category, indicators in self.category_indicators.items():
            score = 0
            
            # Count keyword matches (weight: 1)
            keyword_matches = 0
            for keyword in indicators["keywords"]:
                if keyword in text_lower:
                    keyword_matches += 1
            score += keyword_matches
            
            # Count pattern matches (weight: 2)
            pattern_matches = 0
            for pattern in indicators["patterns"]:
                matches = re.findall(pattern, text_lower)
                pattern_matches += len(matches)
            score += pattern_matches * 2
            
            category_scores[category] = score
            total_possible_score += score
        
        # Apply tie-break rules for research detection
        research_source_indicators = [
            "paper", "benchmark", "api", "reading list", "model", "dataset", 
            "workflow", "architecture", "fine-tuning", "rag", "ray", "anyscale"
        ]
        research_source_count = sum(1 for indicator in research_source_indicators if indicator in text_lower)
        
        # Check for technical journal indicators (building/developing systems)
        technical_journal_indicators = [
            "summarizer", "pipeline", "system", "build", "develop", "create", "implement",
            "failure modes", "alignment", "redundancy", "hallucinations", "golden set",
            "heuristics", "signal extraction", "sprint plan", "validation rules",
            "input features", "templates", "automated routing", "testing steps"
        ]
        technical_journal_count = sum(1 for indicator in technical_journal_indicators if indicator in text_lower)
        
        # If we have 2+ research source indicators, boost research score
        if research_source_count >= 2:
            category_scores["research_article"] += research_source_count * 3
        
        # If we have 3+ technical journal indicators, boost technical journal score
        if technical_journal_count >= 3:
            category_scores["technical_journal"] += technical_journal_count * 2
        
        # Calculate confidence as percentage of total score
        if total_possible_score > 0:
            best_category = max(category_scores, key=category_scores.get)
            best_score = category_scores[best_category]
            confidence = (best_score / total_possible_score) * 100 if total_possible_score > 0 else 0
        else:
            best_category = "technical_journal"
            confidence = 0
        
        # Normalize scores to percentages
        normalized_scores = {}
        for category, score in category_scores.items():
            normalized_scores[category] = (score / total_possible_score * 100) if total_possible_score > 0 else 0
        
        # Debug output
        print(f"Category detection scores: {normalized_scores}")
        print(f"Best category: {best_category} (confidence: {confidence:.1f}%)")
        
        return CategoryDetectionResult(best_category, confidence, normalized_scores)
    
    def get_category_description(self, category: PostCategory) -> str:
        """Get a description of the category."""
        descriptions = {
            "technical_journal": "A personal technical journal entry about a project you built or worked on",
            "research_article": "A research-based article analyzing a topic or subject matter",
            "critique": "A critique or opinion piece about something you observed or experienced"
        }
        return descriptions[category]
    
    def get_category_requirements(self, category: PostCategory) -> List[str]:
        """Get the requirements for each category."""
        requirements = {
            "technical_journal": [
                "Clear problem statement and motivation",
                "Step-by-step implementation details",
                "Technical challenges and solutions",
                "Results and outcomes",
                "Personal reflection and lessons learned"
            ],
            "research_article": [
                "Clear research question or topic",
                "Methodology and approach",
                "Key findings and insights",
                "Data and evidence to support claims",
                "Conclusions and implications"
            ],
            "critique": [
                "Clear subject being critiqued",
                "Specific points of analysis",
                "Evidence and examples to support critique",
                "Balanced perspective with pros and cons",
                "Constructive conclusions and recommendations"
            ]
        }
        return requirements[category]


def detect_content_category(conversation: NormalizedConversation) -> PostCategory:
    """Detect the content category for a conversation."""
    detector = ContentCategoryDetector()
    return detector.detect_category(conversation)
