"""Synthetic benchmark conversations for testing edge cases."""

from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class SyntheticConversation:
    """A synthetic conversation for testing."""
    id: str
    category: str
    messages: List[Dict[str, str]]
    expected_route: str
    expected_score_range: tuple
    must_include_phrases: List[str]
    description: str

class SyntheticBenchmarkGenerator:
    """Generates synthetic conversations for testing edge cases."""
    
    def __init__(self):
        self.conversations = []
        self._generate_technical_journal_conversations()
        self._generate_research_article_conversations()
        self._generate_critique_conversations()
        self._generate_edge_case_conversations()
    
    def _generate_technical_journal_conversations(self):
        """Generate technical journal test cases."""
        
        # Success path - Ollama only, 2 commands
        self.conversations.append(SyntheticConversation(
            id="tech_success_ollama",
            category="technical_journal",
            messages=[
                {"role": "user", "content": "I need to set up a local LLM for development. Let's use Ollama."},
                {"role": "assistant", "content": "Great choice! Here's how to get started with Ollama:"},
                {"role": "user", "content": "Perfect, I'll run these commands and test the setup."}
            ],
            expected_route="technical_journal",
            expected_score_range=(80, 100),
            must_include_phrases=["ollama", "commands", "decision"],
            description="Success path with Ollama and clear commands"
        ))
        
        # Flaky path - timeouts → backoff
        self.conversations.append(SyntheticConversation(
            id="tech_flaky_timeouts",
            category="technical_journal",
            messages=[
                {"role": "user", "content": "The model download is timing out. What should I do?"},
                {"role": "assistant", "content": "Let's implement retry logic with exponential backoff:"},
                {"role": "user", "content": "I'll add this retry mechanism and test it."}
            ],
            expected_route="technical_journal",
            expected_score_range=(70, 90),
            must_include_phrases=["timeout", "retry", "backoff", "decision"],
            description="Flaky path with timeouts and retry logic"
        ))
        
        # Multi-decision - bypass → revert
        self.conversations.append(SyntheticConversation(
            id="tech_multi_decision",
            category="technical_journal",
            messages=[
                {"role": "user", "content": "We decided to bypass LiteLLM and use Ollama directly."},
                {"role": "assistant", "content": "Good decision. Here's the implementation:"},
                {"role": "user", "content": "Actually, let's revert back to LiteLLM for compatibility."}
            ],
            expected_route="technical_journal",
            expected_score_range=(80, 100),
            must_include_phrases=["bypass", "revert", "decision", "ollama", "litellm"],
            description="Multi-decision path with bypass and revert"
        ))
        
        # No commands - should BLOCK
        self.conversations.append(SyntheticConversation(
            id="tech_no_commands",
            category="technical_journal",
            messages=[
                {"role": "user", "content": "I'm thinking about using a local LLM for my project."},
                {"role": "assistant", "content": "That's a great idea! Local LLMs are very useful."},
                {"role": "user", "content": "Yes, I agree. It would be better than cloud APIs."}
            ],
            expected_route="BLOCKED",
            expected_score_range=(0, 50),
            must_include_phrases=[],
            description="No commands - should be blocked"
        ))
        
        # System building keywords
        self.conversations.append(SyntheticConversation(
            id="tech_system_building",
            category="technical_journal",
            messages=[
                {"role": "user", "content": "I need to build a summarizer pipeline with validation rules."},
                {"role": "assistant", "content": "Let's design the architecture with input features and automated routing."},
                {"role": "user", "content": "I'll implement the failure modes detection and golden set testing."}
            ],
            expected_route="technical_journal",
            expected_score_range=(80, 100),
            must_include_phrases=["summarizer", "pipeline", "validation", "architecture", "routing"],
            description="System building with technical keywords"
        ))
    
    def _generate_research_article_conversations(self):
        """Generate research article test cases."""
        
        # Ray/Anyscale RAG
        self.conversations.append(SyntheticConversation(
            id="research_ray_rag",
            category="research_article",
            messages=[
                {"role": "user", "content": "I'm researching Ray for distributed RAG workflows with Anyscale."},
                {"role": "assistant", "content": "Ray is excellent for distributed computing. Here's what the research shows:"},
                {"role": "user", "content": "The benchmark results show significant performance improvements."}
            ],
            expected_route="research_article",
            expected_score_range=(80, 100),
            must_include_phrases=["ray", "rag", "anyscale", "benchmark", "research"],
            description="Ray RAG research with benchmarks"
        ))
        
        # Ethics + reading list
        self.conversations.append(SyntheticConversation(
            id="research_ethics_reading",
            category="research_article",
            messages=[
                {"role": "user", "content": "I'm compiling a reading list on AI ethics and post-capitalist democracy."},
                {"role": "assistant", "content": "Here are some key papers and authors to include:"},
                {"role": "user", "content": "The literature review reveals important patterns in ethical AI development."}
            ],
            expected_route="research_article",
            expected_score_range=(80, 100),
            must_include_phrases=["reading list", "ethics", "literature", "papers", "research"],
            description="Ethics research with reading list"
        ))
        
        # Benchmark discussion with citations
        self.conversations.append(SyntheticConversation(
            id="research_benchmark_citations",
            category="research_article",
            messages=[
                {"role": "user", "content": "The dataset analysis shows interesting patterns in model performance."},
                {"role": "assistant", "content": "According to the research findings, this aligns with previous studies."},
                {"role": "user", "content": "The methodology used in this paper provides a solid foundation."}
            ],
            expected_route="research_article",
            expected_score_range=(80, 100),
            must_include_phrases=["dataset", "analysis", "findings", "methodology", "research"],
            description="Benchmark research with citations"
        ))
        
        # Research-ish but actually opinion - should route Critique
        self.conversations.append(SyntheticConversation(
            id="research_opinion_disguised",
            category="critique",
            messages=[
                {"role": "user", "content": "I think the current research on AI is fundamentally flawed."},
                {"role": "assistant", "content": "I agree, the methodology is questionable and the conclusions are biased."},
                {"role": "user", "content": "The researchers are clearly pushing an agenda rather than seeking truth."}
            ],
            expected_route="critique",
            expected_score_range=(70, 90),
            must_include_phrases=["think", "flawed", "biased", "agenda", "opinion"],
            description="Opinion disguised as research - should route to critique"
        ))
        
        # Academic paper discussion
        self.conversations.append(SyntheticConversation(
            id="research_academic_paper",
            category="research_article",
            messages=[
                {"role": "user", "content": "This peer-reviewed paper presents novel findings on distributed training."},
                {"role": "assistant", "content": "The experimental data supports the hypothesis about scalability."},
                {"role": "user", "content": "The statistical analysis reveals significant correlations between variables."}
            ],
            expected_route="research_article",
            expected_score_range=(80, 100),
            must_include_phrases=["peer-reviewed", "findings", "experimental", "statistical", "research"],
            description="Academic paper discussion"
        ))
    
    def _generate_critique_conversations(self):
        """Generate critique test cases."""
        
        # Strong thesis + counterpoint
        self.conversations.append(SyntheticConversation(
            id="critique_strong_thesis",
            category="critique",
            messages=[
                {"role": "user", "content": "I argue that remote work is fundamentally better than office work."},
                {"role": "assistant", "content": "However, critics might point out the loss of collaboration and team building."},
                {"role": "user", "content": "While that's a valid concern, the data shows productivity actually increases."}
            ],
            expected_route="critique",
            expected_score_range=(80, 100),
            must_include_phrases=["argue", "critics", "however", "thesis", "counterpoint"],
            description="Strong thesis with counterpoint"
        ))
        
        # Meandering rant - should BLOCK
        self.conversations.append(SyntheticConversation(
            id="critique_meandering_rant",
            category="critique",
            messages=[
                {"role": "user", "content": "Everything is terrible and nothing works and I hate it all."},
                {"role": "assistant", "content": "I understand your frustration, but let's try to be constructive."},
                {"role": "user", "content": "No, you don't understand, it's all broken and stupid."}
            ],
            expected_route="BLOCKED",
            expected_score_range=(0, 50),
            must_include_phrases=[],
            description="Meandering rant without clear thesis - should be blocked"
        ))
        
        # Tech critique with clear stance
        self.conversations.append(SyntheticConversation(
            id="critique_tech_stance",
            category="critique",
            messages=[
                {"role": "user", "content": "My thesis is that microservices are overhyped and create more problems than they solve."},
                {"role": "assistant", "content": "On the other hand, proponents argue that microservices enable better scalability."},
                {"role": "user", "content": "The evidence shows that most teams struggle with the complexity overhead."}
            ],
            expected_route="critique",
            expected_score_range=(80, 100),
            must_include_phrases=["thesis", "microservices", "proponents", "evidence", "critique"],
            description="Tech critique with clear stance and counterpoint"
        ))
        
        # Policy critique
        self.conversations.append(SyntheticConversation(
            id="critique_policy",
            category="critique",
            messages=[
                {"role": "user", "content": "I contend that the current AI regulation approach is too restrictive."},
                {"role": "assistant", "content": "Critics might argue that stronger regulation is needed to prevent harm."},
                {"role": "user", "content": "The risk is that over-regulation will stifle innovation and progress."}
            ],
            expected_route="critique",
            expected_score_range=(80, 100),
            must_include_phrases=["contend", "regulation", "critics", "risk", "critique"],
            description="Policy critique with clear argument"
        ))
    
    def _generate_edge_case_conversations(self):
        """Generate edge case conversations."""
        
        # Empty conversation
        self.conversations.append(SyntheticConversation(
            id="edge_empty",
            category="edge_case",
            messages=[],
            expected_route="BLOCKED",
            expected_score_range=(0, 20),
            must_include_phrases=[],
            description="Empty conversation - should be blocked"
        ))
        
        # Single word
        self.conversations.append(SyntheticConversation(
            id="edge_single_word",
            category="edge_case",
            messages=[{"role": "user", "content": "hello"}],
            expected_route="BLOCKED",
            expected_score_range=(0, 20),
            must_include_phrases=[],
            description="Single word - should be blocked"
        ))
        
        # Mixed signals - both research and critique
        self.conversations.append(SyntheticConversation(
            id="edge_mixed_signals",
            category="edge_case",
            messages=[
                {"role": "user", "content": "I'm researching AI ethics but I think the current approach is wrong."},
                {"role": "assistant", "content": "The literature shows mixed results, but I agree with your assessment."},
                {"role": "user", "content": "The data suggests we need a different methodology."}
            ],
            expected_route="research_article",  # Should prefer research due to data/literature
            expected_score_range=(60, 80),
            must_include_phrases=["research", "ethics", "literature", "data"],
            description="Mixed signals - should prefer research"
        ))
        
        # Template filler only
        self.conversations.append(SyntheticConversation(
            id="edge_template_filler",
            category="edge_case",
            messages=[
                {"role": "user", "content": "Key technical component in the research discussion."},
                {"role": "assistant", "content": "The methodology employed ensures comprehensive coverage."},
                {"role": "user", "content": "This research analysis examines various aspects."}
            ],
            expected_route="BLOCKED",
            expected_score_range=(0, 30),
            must_include_phrases=[],
            description="Template filler only - should be blocked"
        ))
        
        # Very short but valid
        self.conversations.append(SyntheticConversation(
            id="edge_short_valid",
            category="technical_journal",
            messages=[
                {"role": "user", "content": "Let's use Ollama. Run: ollama pull llama2"},
                {"role": "assistant", "content": "Done. Test with: curl localhost:11434/api/generate"}
            ],
            expected_route="technical_journal",
            expected_score_range=(70, 90),
            must_include_phrases=["ollama", "curl", "commands"],
            description="Short but valid technical journal"
        ))
    
    def get_conversations_by_category(self, category: str) -> List[SyntheticConversation]:
        """Get conversations by category."""
        return [conv for conv in self.conversations if conv.category == category]
    
    def get_all_conversations(self) -> List[SyntheticConversation]:
        """Get all synthetic conversations."""
        return self.conversations
    
    def get_conversation_by_id(self, conv_id: str) -> SyntheticConversation:
        """Get a specific conversation by ID."""
        for conv in self.conversations:
            if conv.id == conv_id:
                return conv
        raise ValueError(f"Conversation {conv_id} not found")
    
    def export_to_json(self, filepath: str):
        """Export conversations to JSON file."""
        import json
        
        data = []
        for conv in self.conversations:
            data.append({
                'id': conv.id,
                'category': conv.category,
                'messages': conv.messages,
                'expected_route': conv.expected_route,
                'expected_score_range': conv.expected_score_range,
                'must_include_phrases': conv.must_include_phrases,
                'description': conv.description
            })
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def print_summary(self):
        """Print summary of synthetic conversations."""
        print(f"Generated {len(self.conversations)} synthetic conversations:")
        
        categories = {}
        for conv in self.conversations:
            if conv.category not in categories:
                categories[conv.category] = []
            categories[conv.category].append(conv)
        
        for category, convs in categories.items():
            print(f"\n{category.upper()} ({len(convs)} conversations):")
            for conv in convs:
                print(f"  - {conv.id}: {conv.description}")

if __name__ == "__main__":
    generator = SyntheticBenchmarkGenerator()
    generator.print_summary()
    generator.export_to_json("tests/synthetic_benchmark/conversations.json")
