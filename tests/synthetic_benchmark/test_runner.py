"""Test runner for synthetic benchmark conversations."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from synthetic_conversations import SyntheticBenchmarkGenerator, SyntheticConversation
from src.analysis.anchors import AnchorExtractor
from src.routing.router import DeterministicRouter
from src.validate.judge import ContentJudge
from src.llm.decision_centric_journal import DecisionCentricJournalSummarizer
from src.llm.research_article import ResearchArticleSummarizer
from src.llm.critique_summarizer import CritiqueSummarizer
from src.util.schema import SubstackDraft
from typing import Dict, List, Any
import json

class SyntheticBenchmarkTester:
    """Tests the pipeline with synthetic conversations."""
    
    def __init__(self):
        self.generator = SyntheticBenchmarkGenerator()
        self.anchor_extractor = AnchorExtractor()
        self.router = DeterministicRouter()
        self.judge = ContentJudge()
        
        # Initialize summarizers
        self.summarizers = {
            'technical_journal': DecisionCentricJournalSummarizer(),
            'research_article': ResearchArticleSummarizer(),
            'critique': CritiqueSummarizer()
        }
    
    def test_conversation(self, conv: SyntheticConversation) -> Dict[str, Any]:
        """Test a single synthetic conversation."""
        print(f"\nTesting: {conv.id} - {conv.description}")
        
        # Extract anchors
        anchors = self.anchor_extractor.extract_anchors(conv.messages)
        print(f"  Anchors extracted: {len(anchors)}")
        
        # Route content
        content = conv.messages[0]['content'] if conv.messages else ""
        detected_route = self.router.route_content(content, anchors)
        print(f"  Detected route: {detected_route}")
        print(f"  Expected route: {conv.expected_route}")
        
        # Check routing accuracy
        routing_correct = detected_route == conv.expected_route
        print(f"  Routing correct: {routing_correct}")
        
        # If not blocked, try to summarize
        if not detected_route.startswith("BLOCKED"):
            try:
                # Convert to conversation format
                conversation_dict = {
                    'messages': conv.messages,
                    'title_hint': f"Test: {conv.id}"
                }
                
                # Summarize
                summarizer = self.summarizers.get(detected_route)
                if summarizer:
                    draft = summarizer.summarize_conversation(conversation_dict)
                    
                    # Judge the content
                    judge_result = self.judge.judge_content(draft.body_markdown, detected_route, anchors)
                    print(f"  Judge score: {judge_result.score}/100")
                    print(f"  Pass status: {judge_result.pass_status}")
                    print(f"  Hard fails: {judge_result.hard_fails}")
                    
                    # Check if score is in expected range
                    score_in_range = conv.expected_score_range[0] <= judge_result.score <= conv.expected_score_range[1]
                    print(f"  Score in range: {score_in_range}")
                    
                    # Check must-include phrases
                    body_text = draft.body_markdown.lower()
                    phrases_found = [phrase for phrase in conv.must_include_phrases if phrase.lower() in body_text]
                    print(f"  Phrases found: {phrases_found}/{len(conv.must_include_phrases)}")
                    
                    return {
                        'id': conv.id,
                        'category': conv.category,
                        'routing_correct': routing_correct,
                        'detected_route': detected_route,
                        'expected_route': conv.expected_route,
                        'score': judge_result.score,
                        'pass_status': judge_result.pass_status,
                        'score_in_range': score_in_range,
                        'phrases_found': len(phrases_found),
                        'phrases_total': len(conv.must_include_phrases),
                        'hard_fails': judge_result.hard_fails,
                        'anchor_coverage': judge_result.coverage['anchor_coverage_pct']
                    }
                else:
                    print(f"  No summarizer for route: {detected_route}")
                    return {
                        'id': conv.id,
                        'category': conv.category,
                        'routing_correct': routing_correct,
                        'detected_route': detected_route,
                        'expected_route': conv.expected_route,
                        'score': 0,
                        'pass_status': False,
                        'score_in_range': False,
                        'phrases_found': 0,
                        'phrases_total': len(conv.must_include_phrases),
                        'hard_fails': ['no_summarizer'],
                        'anchor_coverage': 0
                    }
            except Exception as e:
                print(f"  Error during summarization: {e}")
                return {
                    'id': conv.id,
                    'category': conv.category,
                    'routing_correct': routing_correct,
                    'detected_route': detected_route,
                    'expected_route': conv.expected_route,
                    'score': 0,
                    'pass_status': False,
                    'score_in_range': False,
                    'phrases_found': 0,
                    'phrases_total': len(conv.must_include_phrases),
                    'hard_fails': ['summarization_error'],
                    'anchor_coverage': 0,
                    'error': str(e)
                }
        else:
            print(f"  Content blocked - no summarization needed")
            return {
                'id': conv.id,
                'category': conv.category,
                'routing_correct': routing_correct,
                'detected_route': detected_route,
                'expected_route': conv.expected_route,
                'score': 0,
                'pass_status': False,
                'score_in_range': True,  # Blocked content is expected
                'phrases_found': 0,
                'phrases_total': len(conv.must_include_phrases),
                'hard_fails': ['blocked'],
                'anchor_coverage': 0
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all synthetic benchmark tests."""
        print("=" * 60)
        print("SYNTHETIC BENCHMARK TESTING")
        print("=" * 60)
        
        results = []
        categories = {}
        
        for conv in self.generator.get_all_conversations():
            result = self.test_conversation(conv)
            results.append(result)
            
            # Group by category
            if conv.category not in categories:
                categories[conv.category] = []
            categories[conv.category].append(result)
        
        # Calculate summary statistics
        total_tests = len(results)
        routing_correct = sum(1 for r in results if r['routing_correct'])
        scores_in_range = sum(1 for r in results if r['score_in_range'])
        pass_status = sum(1 for r in results if r['pass_status'])
        
        print("\n" + "=" * 60)
        print("SUMMARY STATISTICS")
        print("=" * 60)
        print(f"Total tests: {total_tests}")
        print(f"Routing accuracy: {routing_correct}/{total_tests} ({routing_correct/total_tests*100:.1f}%)")
        print(f"Scores in range: {scores_in_range}/{total_tests} ({scores_in_range/total_tests*100:.1f}%)")
        print(f"Pass status: {pass_status}/{total_tests} ({pass_status/total_tests*100:.1f}%)")
        
        # Category breakdown
        print("\n" + "=" * 60)
        print("CATEGORY BREAKDOWN")
        print("=" * 60)
        for category, cat_results in categories.items():
            cat_total = len(cat_results)
            cat_routing = sum(1 for r in cat_results if r['routing_correct'])
            cat_scores = sum(1 for r in cat_results if r['score_in_range'])
            cat_pass = sum(1 for r in cat_results if r['pass_status'])
            
            print(f"\n{category.upper()}:")
            print(f"  Tests: {cat_total}")
            print(f"  Routing: {cat_routing}/{cat_total} ({cat_routing/cat_total*100:.1f}%)")
            print(f"  Scores: {cat_scores}/{cat_total} ({cat_scores/cat_total*100:.1f}%)")
            print(f"  Pass: {cat_pass}/{cat_total} ({cat_pass/cat_total*100:.1f}%)")
        
        # Detailed results
        print("\n" + "=" * 60)
        print("DETAILED RESULTS")
        print("=" * 60)
        for result in results:
            print(f"\n{result['id']}:")
            print(f"  Route: {result['detected_route']} (expected: {result['expected_route']}) ✓" if result['routing_correct'] else f"  Route: {result['detected_route']} (expected: {result['expected_route']}) ✗")
            print(f"  Score: {result['score']}/100")
            print(f"  Pass: {result['pass_status']}")
            print(f"  Phrases: {result['phrases_found']}/{result['phrases_total']}")
            if result['hard_fails']:
                print(f"  Hard fails: {', '.join(result['hard_fails'])}")
        
        return {
            'total_tests': total_tests,
            'routing_accuracy': routing_correct / total_tests,
            'scores_in_range': scores_in_range / total_tests,
            'pass_rate': pass_status / total_tests,
            'category_breakdown': categories,
            'detailed_results': results
        }
    
    def run_category_tests(self, category: str) -> Dict[str, Any]:
        """Run tests for a specific category."""
        conversations = self.generator.get_conversations_by_category(category)
        results = []
        
        print(f"\nTesting {category.upper()} conversations:")
        for conv in conversations:
            result = self.test_conversation(conv)
            results.append(result)
        
        return results

if __name__ == "__main__":
    tester = SyntheticBenchmarkTester()
    results = tester.run_all_tests()
    
    # Export results
    with open("tests/synthetic_benchmark/test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults exported to: tests/synthetic_benchmark/test_results.json")
