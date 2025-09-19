"""Golden set testing framework for chat2substack pipeline."""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from src.util.schema import NormalizedConversation, SubstackDraft
from src.llm.category_detector import ContentCategoryDetector
from src.llm.decision_centric_journal import DecisionCentricJournalSummarizer
from src.llm.research_article import ResearchArticleSummarizer
from src.llm.critique_summarizer import CritiqueSummarizer


@dataclass
class GoldenSetTestCase:
    """A single test case in the golden set."""
    name: str
    content_type: str
    input_file: str
    expected_output_file: str
    description: str
    expected_metrics: Dict[str, Any]


@dataclass
class TestResult:
    """Result of a golden set test."""
    test_case: GoldenSetTestCase
    passed: bool
    actual_output: SubstackDraft
    expected_output: SubstackDraft
    metrics: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class GoldenSetTester:
    """Tests the pipeline against curated golden set data."""
    
    def __init__(self, golden_sets_dir: str = "tests/golden_sets"):
        self.golden_sets_dir = Path(golden_sets_dir)
        self.test_cases = []
        self.results = []
        
        # Initialize summarizers
        self.category_detector = ContentCategoryDetector()
        self.technical_journal_summarizer = DecisionCentricJournalSummarizer()
        self.research_article_summarizer = ResearchArticleSummarizer()
        self.critique_summarizer = CritiqueSummarizer()
    
    def load_test_cases(self) -> List[GoldenSetTestCase]:
        """Load all test cases from the golden sets directory."""
        test_cases = []
        
        # Load technical journal test cases
        tech_dir = self.golden_sets_dir / "technical_journal"
        if tech_dir.exists():
            for test_file in tech_dir.glob("*.json"):
                test_case = self._load_test_case(test_file, "technical_journal")
                if test_case:
                    test_cases.append(test_case)
        
        # Load research article test cases
        research_dir = self.golden_sets_dir / "research_article"
        if research_dir.exists():
            for test_file in research_dir.glob("*.json"):
                test_case = self._load_test_case(test_file, "research_article")
                if test_case:
                    test_cases.append(test_case)
        
        # Load critique test cases
        critique_dir = self.golden_sets_dir / "critique"
        if critique_dir.exists():
            for test_file in critique_dir.glob("*.json"):
                test_case = self._load_test_case(test_file, "critique")
                if test_case:
                    test_cases.append(test_case)
        
        self.test_cases = test_cases
        return test_cases
    
    def _load_test_case(self, test_file: Path, content_type: str) -> GoldenSetTestCase:
        """Load a single test case from a JSON file."""
        try:
            with open(test_file, 'r') as f:
                data = json.load(f)
            
            return GoldenSetTestCase(
                name=data.get('name', test_file.stem),
                content_type=content_type,
                input_file=str(test_file),
                expected_output_file=data.get('expected_output_file', ''),
                description=data.get('description', ''),
                expected_metrics=data.get('expected_metrics', {})
            )
        except Exception as e:
            print(f"Error loading test case {test_file}: {e}")
            return None
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all golden set tests."""
        if not self.test_cases:
            self.load_test_cases()
        
        results = []
        for test_case in self.test_cases:
            result = self.run_single_test(test_case)
            results.append(result)
        
        self.results = results
        return results
    
    def run_single_test(self, test_case: GoldenSetTestCase) -> TestResult:
        """Run a single golden set test."""
        print(f"Running test: {test_case.name} ({test_case.content_type})")
        
        try:
            # Load input conversation
            conversation = self._load_conversation(test_case.input_file)
            if not conversation:
                return TestResult(
                    test_case=test_case,
                    passed=False,
                    actual_output=None,
                    expected_output=None,
                    metrics={},
                    errors=[f"Failed to load conversation from {test_case.input_file}"],
                    warnings=[]
                )
            
            # Generate output using appropriate summarizer
            actual_output = self._generate_output(conversation, test_case.content_type)
            
            # Load expected output if available
            expected_output = None
            if test_case.expected_output_file and os.path.exists(test_case.expected_output_file):
                expected_output = self._load_expected_output(test_case.expected_output_file)
            
            # Calculate metrics
            metrics = self._calculate_metrics(actual_output, expected_output)
            
            # Determine if test passed
            passed = self._evaluate_test(actual_output, expected_output, metrics, test_case.expected_metrics)
            
            # Collect errors and warnings
            errors = self._collect_errors(actual_output, expected_output, metrics)
            warnings = self._collect_warnings(actual_output, expected_output, metrics)
            
            return TestResult(
                test_case=test_case,
                passed=passed,
                actual_output=actual_output,
                expected_output=expected_output,
                metrics=metrics,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            return TestResult(
                test_case=test_case,
                passed=False,
                actual_output=None,
                expected_output=None,
                metrics={},
                errors=[f"Test execution failed: {str(e)}"],
                warnings=[]
            )
    
    def _load_conversation(self, input_file: str) -> NormalizedConversation:
        """Load a conversation from a file."""
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            # Convert to NormalizedConversation
            messages = []
            for msg_data in data.get('messages', []):
                messages.append({
                    'text': msg_data.get('content', ''),
                    'role': msg_data.get('role', 'user')
                })
            
            # Generate required fields
            from datetime import datetime
            conversation_id = datetime.now().isoformat()
            
            return NormalizedConversation(
                id=conversation_id,
                source={
                    'type': 'manual_text',
                    'path': input_file
                },
                title_hint=data.get('title_hint', 'Test Conversation'),
                messages=messages
            )
        except Exception as e:
            print(f"Error loading conversation from {input_file}: {e}")
            return None
    
    def _generate_output(self, conversation: NormalizedConversation, content_type: str) -> SubstackDraft:
        """Generate output using the appropriate summarizer."""
        # Convert to dict format expected by summarizers
        conversation_dict = {
            'messages': [
                {'content': msg.text, 'role': msg.role} 
                for msg in conversation.messages
            ],
            'title_hint': getattr(conversation, 'title_hint', 'Test')
        }
        
        if content_type == "technical_journal":
            return self.technical_journal_summarizer.summarize_conversation(conversation_dict)
        elif content_type == "research_article":
            return self.research_article_summarizer.summarize_conversation(conversation_dict)
        elif content_type == "critique":
            return self.critique_summarizer.summarize(conversation)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def _load_expected_output(self, expected_file: str) -> SubstackDraft:
        """Load expected output from a file."""
        try:
            with open(expected_file, 'r') as f:
                data = json.load(f)
            
            return SubstackDraft(
                title=data.get('title', ''),
                dek=data.get('dek', ''),
                tldr=data.get('tldr', []),
                tags=data.get('tags', []),
                body_markdown=data.get('body_markdown', ''),
                further_reading=data.get('further_reading')
            )
        except Exception as e:
            print(f"Error loading expected output from {expected_file}: {e}")
            return None
    
    def _calculate_metrics(self, actual: SubstackDraft, expected: SubstackDraft) -> Dict[str, Any]:
        """Calculate quality metrics for the output."""
        metrics = {}
        
        if actual:
            # Basic metrics
            metrics['title_length'] = len(actual.title)
            metrics['dek_length'] = len(actual.dek)
            metrics['tldr_count'] = len(actual.tldr)
            metrics['tags_count'] = len(actual.tags)
            metrics['body_word_count'] = len(actual.body_markdown.split())
            
            # Content quality metrics
            metrics['has_title'] = bool(actual.title.strip())
            metrics['has_dek'] = bool(actual.dek.strip())
            metrics['has_tldr'] = len(actual.tldr) > 0
            metrics['has_tags'] = len(actual.tags) > 0
            metrics['has_body'] = bool(actual.body_markdown.strip())
            
            # Length validation
            metrics['title_valid'] = len(actual.title) <= 80
            metrics['dek_valid'] = len(actual.dek) <= 200
            metrics['tldr_valid'] = len(actual.tldr) <= 5
            metrics['tags_valid'] = len(actual.tags) <= 6
            metrics['body_word_count_valid'] = 300 <= len(actual.body_markdown.split()) <= 900
            
            # Content structure metrics
            metrics['has_sections'] = '##' in actual.body_markdown
            metrics['has_bullets'] = '-' in actual.body_markdown or '*' in actual.body_markdown
            metrics['has_numbered_lists'] = any(line.strip().startswith(f'{i}.') for i in range(1, 10) for line in actual.body_markdown.split('\n'))
        
        if expected:
            # Comparison metrics
            metrics['title_match'] = actual.title == expected.title if actual and expected else False
            metrics['dek_match'] = actual.dek == expected.dek if actual and expected else False
            metrics['tldr_match'] = actual.tldr == expected.tldr if actual and expected else False
            metrics['tags_match'] = actual.tags == expected.tags if actual and expected else False
        
        return metrics
    
    def _evaluate_test(self, actual: SubstackDraft, expected: SubstackDraft, 
                      metrics: Dict[str, Any], expected_metrics: Dict[str, Any]) -> bool:
        """Evaluate whether a test passed."""
        if not actual:
            return False
        
        # Check basic requirements
        basic_checks = [
            metrics.get('has_title', False),
            metrics.get('has_dek', False),
            metrics.get('has_tldr', False),
            metrics.get('has_tags', False),
            metrics.get('has_body', False)
        ]
        
        if not all(basic_checks):
            return False
        
        # Check validation requirements
        validation_checks = [
            metrics.get('title_valid', False),
            metrics.get('dek_valid', False),
            metrics.get('tldr_valid', False),
            metrics.get('tags_valid', False),
            metrics.get('body_word_count_valid', False)
        ]
        
        if not all(validation_checks):
            return False
        
        # Check expected metrics if provided
        for key, expected_value in expected_metrics.items():
            if key in metrics and metrics[key] != expected_value:
                return False
        
        return True
    
    def _collect_errors(self, actual: SubstackDraft, expected: SubstackDraft, 
                       metrics: Dict[str, Any]) -> List[str]:
        """Collect errors from the test."""
        errors = []
        
        if not actual:
            errors.append("No output generated")
            return errors
        
        # Validation errors
        if not metrics.get('title_valid', False):
            errors.append(f"Title too long: {metrics.get('title_length', 0)} characters")
        
        if not metrics.get('dek_valid', False):
            errors.append(f"Dek too long: {metrics.get('dek_length', 0)} characters")
        
        if not metrics.get('tldr_valid', False):
            errors.append(f"Too many TL;DR points: {metrics.get('tldr_count', 0)}")
        
        if not metrics.get('tags_valid', False):
            errors.append(f"Too many tags: {metrics.get('tags_count', 0)}")
        
        if not metrics.get('body_word_count_valid', False):
            errors.append(f"Body word count invalid: {metrics.get('body_word_count', 0)} words")
        
        return errors
    
    def _collect_warnings(self, actual: SubstackDraft, expected: SubstackDraft, 
                         metrics: Dict[str, Any]) -> List[str]:
        """Collect warnings from the test."""
        warnings = []
        
        if not actual:
            return warnings
        
        # Content quality warnings
        if not metrics.get('has_sections', False):
            warnings.append("No sections found in body")
        
        if not metrics.get('has_bullets', False) and not metrics.get('has_numbered_lists', False):
            warnings.append("No lists found in body")
        
        # Length warnings
        word_count = metrics.get('body_word_count', 0)
        if word_count < 400:
            warnings.append(f"Body may be too short: {word_count} words")
        elif word_count > 800:
            warnings.append(f"Body may be too long: {word_count} words")
        
        return warnings
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        if not self.results:
            return "No test results available."
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("# Golden Set Test Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append(f"## Summary")
        report.append(f"- Total Tests: {total_tests}")
        report.append(f"- Passed: {passed_tests}")
        report.append(f"- Failed: {failed_tests}")
        report.append(f"- Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        report.append("")
        
        # Group by content type
        by_type = {}
        for result in self.results:
            content_type = result.test_case.content_type
            if content_type not in by_type:
                by_type[content_type] = []
            by_type[content_type].append(result)
        
        for content_type, results in by_type.items():
            report.append(f"## {content_type.replace('_', ' ').title()}")
            report.append("")
            
            type_passed = sum(1 for r in results if r.passed)
            type_total = len(results)
            report.append(f"Passed: {type_passed}/{type_total} ({(type_passed/type_total)*100:.1f}%)")
            report.append("")
            
            for result in results:
                status = "✅ PASS" if result.passed else "❌ FAIL"
                report.append(f"### {result.test_case.name} - {status}")
                report.append(f"**Description:** {result.test_case.description}")
                
                if result.errors:
                    report.append("**Errors:**")
                    for error in result.errors:
                        report.append(f"- {error}")
                
                if result.warnings:
                    report.append("**Warnings:**")
                    for warning in result.warnings:
                        report.append(f"- {warning}")
                
                if result.metrics:
                    report.append("**Metrics:**")
                    for key, value in result.metrics.items():
                        report.append(f"- {key}: {value}")
                
                report.append("")
        
        return "\n".join(report)
    
    def save_report(self, output_file: str = "tests/golden_sets/test_report.md"):
        """Save the test report to a file."""
        report = self.generate_report()
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Test report saved to {output_file}")


def main():
    """Run golden set tests."""
    tester = GoldenSetTester()
    results = tester.run_all_tests()
    tester.save_report()
    
    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    print(f"\nGolden Set Test Results: {passed}/{total} passed ({(passed/total)*100:.1f}%)")


if __name__ == "__main__":
    main()
