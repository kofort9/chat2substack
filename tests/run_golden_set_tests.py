#!/usr/bin/env python3
"""Run golden set tests for chat2substack pipeline."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.golden_sets.golden_set_tester import GoldenSetTester


def main():
    """Run all golden set tests and generate report."""
    print("🧪 Running Golden Set Tests for Chat2Substack Pipeline")
    print("=" * 60)
    
    # Initialize tester
    tester = GoldenSetTester()
    
    # Load test cases
    print("📋 Loading test cases...")
    test_cases = tester.load_test_cases()
    print(f"Found {len(test_cases)} test cases")
    
    if not test_cases:
        print("❌ No test cases found. Please add test cases to tests/golden_sets/")
        return 1
    
    # Run tests
    print("\n🚀 Running tests...")
    results = tester.run_all_tests()
    
    # Generate and save report
    print("\n📊 Generating test report...")
    tester.save_report()
    
    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    
    print(f"\n📈 Test Results Summary:")
    print(f"   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    # Show failed tests
    if failed > 0:
        print(f"\n❌ Failed Tests:")
        for result in results:
            if not result.passed:
                print(f"   - {result.test_case.name} ({result.test_case.content_type})")
                for error in result.errors:
                    print(f"     Error: {error}")
    
    # Show warnings
    warnings = []
    for result in results:
        warnings.extend(result.warnings)
    
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)} total):")
        for warning in warnings[:5]:  # Show first 5 warnings
            print(f"   - {warning}")
        if len(warnings) > 5:
            print(f"   ... and {len(warnings) - 5} more")
    
    print(f"\n📄 Detailed report saved to: tests/golden_sets/test_report.md")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
