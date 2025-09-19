# Test Files

This directory contains HTML test files used for development and testing of the chat2substack pipeline.

## Files

- `critique_test.html` - Test file for critique content type
- `primary_test_conversation.html` - Primary test conversation (Sentry integration)
- `research_test_1.html` - Research article test file 1
- `research_test_2.html` - Research article test file 2
- `test_conversation.html` - General test conversation
- `updated_conversation.html` - Updated test conversation

## Usage

These files can be used for testing the pipeline:

```bash
# Test with primary conversation
python -m src.run --input test_files/primary_test_conversation.html --content-type technical_journal

# Test with research conversation
python -m src.run --input test_files/research_test_1.html --content-type research_article

# Test with critique conversation
python -m src.run --input test_files/critique_test.html --content-type critique
```

## Note

These are development test files and should not be committed to the repository in production.
