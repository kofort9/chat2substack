# Golden Set Testing

This directory contains a curated set of high-quality conversations with expected outputs for testing summarizer quality.

## Purpose
- Baseline for measuring summarizer quality
- Regression testing for summarizer changes
- Quality validation against known good examples

## Structure
```
tests/golden_set/
├── conversations/          # Original conversation files
├── expected_outputs/       # Expected summary outputs
├── test_cases.json        # Test case definitions
└── quality_metrics.py     # Quality scoring functions
```

## Usage
```bash
python -m tests.golden_set.quality_metrics
```
