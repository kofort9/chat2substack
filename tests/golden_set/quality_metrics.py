"""Quality metrics and testing for golden set validation."""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ingest.from_shared_html import ingest_shared_html
from src.llm.comprehensive_summarizer import summarize_conversation_comprehensive
from src.analysis.conversation_analyzer import analyze_conversation_and_compare


@dataclass
class QualityScore:
    """Quality score for a test case."""
    test_case_id: str
    word_coverage: float
    topic_coverage: float
    technical_term_coverage: float
    code_snippet_coverage: float
    questions_addressed: float
    solutions_included: float
    overall_score: float
    passed: bool
    issues: List[str]


class GoldenSetTester:
    """Test summarizer quality against golden set."""
    
    def __init__(self, golden_set_dir: str = "tests/golden_set"):
        self.golden_set_dir = Path(golden_set_dir)
        self.test_cases_file = self.golden_set_dir / "test_cases.json"
        self.conversations_dir = self.golden_set_dir / "conversations"
        self.expected_outputs_dir = self.golden_set_dir / "expected_outputs"
        
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test case definitions."""
        with open(self.test_cases_file, 'r') as f:
            data = json.load(f)
        return data['test_cases']
    
    def run_golden_set_tests(self) -> List[QualityScore]:
        """Run all golden set tests and return quality scores."""
        test_cases = self.load_test_cases()
        results = []
        
        for test_case in test_cases:
            print(f"\\n=== Testing: {test_case['name']} ===")
            score = self._test_single_case(test_case)
            results.append(score)
            
        return results
    
    def _test_single_case(self, test_case: Dict[str, Any]) -> QualityScore:
        """Test a single golden set case."""
        try:
            # Load conversation
            conversation_file = self.conversations_dir / test_case['conversation_file']
            if not conversation_file.exists():
                return QualityScore(
                    test_case_id=test_case['id'],
                    word_coverage=0.0,
                    topic_coverage=0.0,
                    technical_term_coverage=0.0,
                    code_snippet_coverage=0.0,
                    questions_addressed=0.0,
                    solutions_included=0.0,
                    overall_score=0.0,
                    passed=False,
                    issues=[f"Conversation file not found: {conversation_file}"]
                )
            
            conversation = ingest_shared_html(str(conversation_file))
            
            # Generate summary
            draft = summarize_conversation_comprehensive(conversation)
            
            # Analyze and compare
            comparison_report = analyze_conversation_and_compare(
                conversation, draft, f"golden-test-{test_case['id']}", Path("dist")
            )
            
            # Extract metrics
            metrics = comparison_report['coverage_metrics']
            word_coverage = metrics['word_coverage']
            topic_coverage = metrics['topic_coverage']
            technical_term_coverage = metrics['technical_term_coverage']
            code_snippet_coverage = metrics['code_snippet_coverage']
            questions_addressed = metrics['questions_addressed']
            solutions_included = metrics['solutions_included']
            
            # Calculate overall score (weighted average)
            overall_score = (
                word_coverage * 0.2 +
                topic_coverage * 0.25 +
                technical_term_coverage * 0.15 +
                code_snippet_coverage * 0.1 +
                questions_addressed * 0.15 +
                solutions_included * 0.15
            )
            
            # Check against expected metrics
            expected = test_case['expected_metrics']
            issues = []
            passed = True
            
            if word_coverage < expected['min_word_coverage']:
                issues.append(f"Word coverage {word_coverage:.1f}% below minimum {expected['min_word_coverage']}%")
                passed = False
            
            if topic_coverage < expected['min_topic_coverage']:
                issues.append(f"Topic coverage {topic_coverage:.1f}% below minimum {expected['min_topic_coverage']}%")
                passed = False
            
            if technical_term_coverage < expected['min_technical_term_coverage']:
                issues.append(f"Technical term coverage {technical_term_coverage:.1f}% below minimum {expected['min_technical_term_coverage']}%")
                passed = False
            
            if solutions_included < expected['min_solutions_included']:
                issues.append(f"Solutions included {solutions_included:.1f}% below minimum {expected['min_solutions_included']}%")
                passed = False
            
            if questions_addressed < expected['min_questions_addressed']:
                issues.append(f"Questions addressed {questions_addressed:.1f}% below minimum {expected['min_questions_addressed']}%")
                passed = False
            
            print(f"Word Coverage: {word_coverage:.1f}%")
            print(f"Topic Coverage: {topic_coverage:.1f}%")
            print(f"Technical Terms: {technical_term_coverage:.1f}%")
            print(f"Solutions: {solutions_included:.1f}%")
            print(f"Overall Score: {overall_score:.1f}%")
            print(f"Status: {'PASS' if passed else 'FAIL'}")
            
            return QualityScore(
                test_case_id=test_case['id'],
                word_coverage=word_coverage,
                topic_coverage=topic_coverage,
                technical_term_coverage=technical_term_coverage,
                code_snippet_coverage=code_snippet_coverage,
                questions_addressed=questions_addressed,
                solutions_included=solutions_included,
                overall_score=overall_score,
                passed=passed,
                issues=issues
            )
            
        except Exception as e:
            return QualityScore(
                test_case_id=test_case['id'],
                word_coverage=0.0,
                topic_coverage=0.0,
                technical_term_coverage=0.0,
                code_snippet_coverage=0.0,
                questions_addressed=0.0,
                solutions_included=0.0,
                overall_score=0.0,
                passed=False,
                issues=[f"Test failed with error: {str(e)}"]
            )
    
    def generate_report(self, results: List[QualityScore]) -> str:
        """Generate a comprehensive test report."""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        avg_score = sum(r.overall_score for r in results) / total_tests if total_tests > 0 else 0
        
        report = f"""# Golden Set Test Report

## Summary
- **Total Tests**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {total_tests - passed_tests}
- **Success Rate**: {(passed_tests/total_tests)*100:.1f}%
- **Average Score**: {avg_score:.1f}%

## Individual Results

"""
        
        for result in results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            report += f"""### {result.test_case_id}
**Status**: {status}
**Overall Score**: {result.overall_score:.1f}%

**Metrics**:
- Word Coverage: {result.word_coverage:.1f}%
- Topic Coverage: {result.topic_coverage:.1f}%
- Technical Terms: {result.technical_term_coverage:.1f}%
- Code Snippets: {result.code_snippet_coverage:.1f}%
- Questions Addressed: {result.questions_addressed:.1f}%
- Solutions Included: {result.solutions_included:.1f}%

"""
            if result.issues:
                report += "**Issues**:\\n"
                for issue in result.issues:
                    report += f"- {issue}\\n"
                report += "\\n"
        
        return report


def main():
    """Run golden set tests and generate report."""
    tester = GoldenSetTester()
    results = tester.run_golden_set_tests()
    report = tester.generate_report(results)
    
    # Save report
    report_file = Path("dist/golden_set_test_report.md")
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\\n=== GOLDEN SET TEST COMPLETE ===")
    print(f"Report saved to: {report_file}")
    
    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    print(f"Tests: {passed}/{total} passed ({(passed/total)*100:.1f}%)")


if __name__ == "__main__":
    main()
