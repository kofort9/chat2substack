# Golden Set Testing

This directory contains curated test cases for validating the chat2substack pipeline across different content types.

## Overview

Golden set testing ensures consistent quality and catches regressions by testing the pipeline against known, high-quality conversations with expected outputs.

## Test Structure

```
tests/golden_sets/
├── technical_journal/     # Technical journal test cases
├── research_article/      # Research article test cases  
├── critique/             # Critique test cases
├── golden_set_tester.py  # Testing framework
├── config.yaml          # Test configuration
└── test_report.md       # Generated test report
```

## Test Cases

### Technical Journal (2 test cases)
- **Sentry Integration Technical Journal**: Synthetic test case for Sentry integration
- **Primary Test URL - Sentry Integration**: Real conversation from Primary Test URL

### Research Article (1 test case)
- **AI Ethics Research Analysis**: Synthetic test case for AI ethics research

### Critique (2 test cases)
- **Technology Critique Analysis**: Synthetic test case for technology critique
- **Real Critique Test - LRM Reasoning Analysis**: Real conversation from critique test URL

## Running Tests

### Quick Test
```bash
python run_golden_tests.py
```

### Detailed Test
```bash
python -c "
import sys
sys.path.insert(0, '.')
from tests.golden_sets.golden_set_tester import GoldenSetTester
tester = GoldenSetTester()
results = tester.run_all_tests()
tester.save_report()
"
```

## Test Metrics

Each test validates:
- **Content Structure**: Title, dek, TL;DR, tags, body
- **Length Validation**: Character/word count limits
- **Content Quality**: Sections, lists, proper formatting
- **Schema Compliance**: Pydantic validation
- **Content Type Specific**: Requirements per content type

## Adding New Test Cases

1. Create a JSON file in the appropriate content type directory
2. Follow the format in existing test cases
3. Include expected metrics for validation
4. Run tests to validate the new case

### Test Case Format
```json
{
  "name": "Test Case Name",
  "description": "Description of what this tests",
  "content_type": "technical_journal|research_article|critique",
  "expected_metrics": {
    "has_title": true,
    "has_dek": true,
    "title_valid": true,
    "body_word_count_valid": true
  },
  "messages": [
    {
      "role": "user",
      "content": "User message content"
    },
    {
      "role": "assistant", 
      "content": "Assistant response"
    }
  ],
  "title_hint": "Conversation title hint"
}
```

## Test Results

Current test results: **5/5 tests passing (100% success rate)**

- ✅ Technical Journal: 2/2 passing
- ✅ Research Article: 1/1 passing  
- ✅ Critique: 2/2 passing

## Quality Thresholds

- **Word Count**: 300-900 words
- **Title Length**: ≤80 characters
- **Dek Length**: ≤200 characters
- **TL;DR Points**: 3-5 points
- **Tags**: 3-6 tags
- **Structure**: Must have sections and lists

## Continuous Integration

The golden set tests can be integrated into CI/CD pipelines to:
- Catch regressions automatically
- Validate quality before deployment
- Ensure consistent output across changes
- Monitor performance over time
