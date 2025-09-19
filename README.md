# Chat2Substack

A production-ready pipeline that converts ChatGPT conversations into professional Substack draft content. Built with a judge-driven quality system, anchor-based extraction, and decision-centric summarization to ensure high-quality, publication-ready content.

## Purpose

Chat2Substack solves the problem of transforming raw AI conversations into polished, professional content suitable for publication. It addresses key challenges:

- **Content Quality**: Ensures output meets professional standards with 80/100+ quality scores
- **Privacy Protection**: Local PII redaction prevents sensitive information leakage
- **Content Structure**: Transforms conversational data into structured, narrative content
- **Type Specialization**: Automatically detects and optimizes for different content types
- **Production Readiness**: Generates publication-ready Markdown with proper formatting

## Architecture

### Core Pipeline Flow

```
Input → Ingest → Redact → Analyze → Route → Summarize → Judge → Render → Output
```

### System Components

#### 1. **Input Processing** (`src/ingest/`)
- **HTML Parser**: Extracts conversation structure from ChatGPT shared links
- **Text Parser**: Handles manual text input with role detection
- **Content Normalization**: Standardizes conversation format across input types

#### 2. **Privacy Protection** (`src/redact/`)
- **PII Detection**: Identifies emails, phones, addresses, and private names
- **Deterministic Redaction**: Consistent replacement patterns for privacy
- **Public Figure Preservation**: Maintains references to public individuals

#### 3. **Content Analysis** (`src/analysis/`)
- **Anchor Extraction**: Identifies key concepts, decisions, commands, and citations
- **Signal Detection**: Extracts technical, academic, and opinion indicators
- **Coverage Analysis**: Measures content extraction completeness

#### 4. **Intelligent Routing** (`src/routing/`)
- **Content Type Detection**: Automatically categorizes conversations
- **Confidence Scoring**: Provides reliability metrics for classification
- **Fallback Logic**: Handles ambiguous content with abstain mechanisms

#### 5. **Specialized Summarization** (`src/llm/`)
- **Technical Journal**: Decision-centric engineering narratives
- **Research Article**: Academic-style analysis with methodology
- **Critique**: Balanced opinion and argument structure
- **Self-Play Improvement**: One-retry enhancement for failed content

#### 6. **Quality Validation** (`src/validate/`)
- **Judge System**: 0-100 scoring with hard fail detection
- **Section Completeness**: Ensures required content sections
- **Anchor Coverage**: Validates comprehensive content extraction
- **Evidence Density**: Measures substantiation quality

#### 7. **Output Generation** (`src/render/`)
- **Markdown Rendering**: Clean, Substack-optimized formatting
- **HTML Conversion**: Web-ready content with proper structure
- **Metadata Generation**: Quality scores, coverage metrics, and processing stats

### Quality Assurance System

The pipeline implements a comprehensive quality assurance system:

#### Judge-Driven Validation
- **Hard Fails**: Critical issues that block publication
- **Quality Scoring**: 0-100 scale with detailed subscores
- **Section Requirements**: Enforces content structure completeness
- **Anchor Coverage**: Ensures 50%+ conversation element referencing

#### Self-Play Improvement
- **One-Retry Logic**: Attempts improvement for failed content
- **Content Expansion**: Adds missing sections and details
- **Quality Re-evaluation**: Re-judges improved content

#### Testing Framework
- **Golden Set Testing**: Curated conversations with expected outputs
- **Synthetic Benchmark**: 30+ adversarial test cases
- **Mutation Testing**: Robustness validation through input perturbation
- **Coverage Analysis**: Comprehensive content extraction validation

## Features

- **Input Processing**: Ingest ChatGPT shared HTML or manual text input
- **PII Redaction**: Local, deterministic scrubbing of emails, phones, addresses, and private names
- **Decision-Centric Summarization**: Professional technical journal generation with engineering decision extraction
- **Content Guardrails**: Safety and tone checks with automatic patching
- **Professional Rendering**: Clean Markdown and HTML output optimized for Substack
- **Idempotency**: Content hashing prevents duplicate processing
- **CI/CD Ready**: GitHub Actions workflow with artifact generation
- **Feature-Flagged Publishing**: Optional Substack draft creation via Playwright
- **Content Type Detection**: Automatic categorization and specialized summarizers

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/chat2substack.git
cd chat2substack

# Install dependencies
make setup
```

### Basic Usage

```bash
# Process a ChatGPT HTML export with technical journal summarizer
python -m src.run --input inbox/chat.html --content-type technical_journal

# Process with automatic content type detection
python -m src.run --input inbox/chat.html --content-type auto

# Process manual text input
python -m src.run --input inbox/manual.txt --content-type technical_journal

# Create Substack draft (requires credentials)
python -m src.run --input inbox/chat.html --content-type technical_journal --create-draft=true
```

### Input Formats

**ChatGPT HTML Export:**
- Save shared ChatGPT conversation as HTML
- Place in `inbox/chat.html`
- Pipeline extracts conversation structure automatically

**Manual Text Input:**
- Plain text file with conversation
- Supports delimiters: `User:`, `Assistant:`, `Q:`, `A:`
- Place in `inbox/manual.txt` (max 10,000 characters)

## Output

The pipeline generates organized output in the `dist/` directory:

### 📝 **Posts** (`dist/posts/`)
- `FINAL_POST_<slug>.md` - Ready-to-publish Substack posts
- `POST_SUMMARY_<slug>.md` - Detailed summaries with metrics

### 💬 **Conversations** (`dist/conversations/`)
- `chatgpt-<topic>/` - Individual conversation folders
  - `full_conversation.json` - Complete conversation data
  - `full_conversation.md` - Human-readable conversation
  - `conversation_vs_summary_analysis.json` - Detailed coverage analysis
  - `conversation_vs_summary_analysis.md` - Human-readable analysis

### 📊 **Reports** (`dist/reports/`)
- `run_report.md` - Latest processing report with redaction stats
- `golden_set_test_report.md` - Test suite results

### 🗂️ **Archives** (`dist/archives/`)
- Historical test runs and development artifacts

### 📋 **Index** (`dist/index.json`)
- Complete index of all generated content with metadata

## Configuration

Edit `config.yaml` to customize:

```yaml
length:
  target_words: 450
  hard_cap_words: 900

redaction:
  pseudonymize_private_names: true
  private_name_list: []
  allow_public_figures: true

guardrails:
  blocked_phrases: []
  enforce_tone: true

substack:
  host: "https://YOURNAME.substack.com"
  create_draft: false
```

## PII Redaction

The system automatically redacts:

- **Emails**: `john@example.com` → `[email-redacted]`
- **Phones**: `(555) 123-4567` → `[phone-redacted]`
- **Addresses**: `123 Main St` → `[address-redacted]`
- **IDs**: SSNs, credit cards, long numeric IDs → `[id-redacted]`
- **Private Names**: `John Smith` → `J(pseudonym)` (configurable list)

Public figures are preserved by default.

## Content Guardrails

Two guardrail systems ensure quality:

**Content Safety:**
- PII leakage detection
- Blocked phrases filtering
- Career-sensitive content detection
- Unverified claims identification

**Tone & Structure:**
- Length validation (300-900 words)
- Professional tone enforcement
- Required section validation
- Tag format compliance

## Substack Integration

To enable draft creation:

1. Set environment variables:
   ```bash
   export SUBSTACK_EMAIL="your@email.com"
   export SUBSTACK_PASSWORD="your_password"
   export SUBSTACK_HOST="https://yourname.substack.com"
   ```

2. Run with draft creation:
   ```bash
   python -m src.run --input inbox/chat.html --create-draft=true
   ```

3. Check `dist/run_report.md` for draft URL

## Development

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_ingest_html.py -v

# Run with coverage
pytest --cov=src tests/
```

### Testing with Real Conversations

The project includes curated test URLs for validation:

```bash
# Test with Primary Test URL (Sentry conversation)
python -m src.run --input-url https://chatgpt.com/share/68cc337e-4cf0-8013-9b24-960236a8df4b --content-type technical_journal

# Test with additional URLs
python -m src.run --input-url https://chatgpt.com/share/68cc3fb2-2ac4-8013-857d-0ba20e2f2d68 --content-type auto
```

Test URLs are maintained in `test_urls.txt` for consistent validation across development cycles.

### Content Types

The pipeline currently supports the following content types:

**✅ Technical Journal** (Production Ready)
- Decision-centric summarization
- Engineering decision extraction
- Professional narrative structure
- Rationale and evidence documentation

**🚧 Research Article** (In Development)
- Academic-style summarization
- Research methodology extraction
- Evidence-based conclusions
- Citation and reference handling

**🚧 Critique** (Planned)
- Opinion and analysis summarization
- Critical thinking extraction
- Balanced perspective presentation
- Argument structure analysis

**🚧 Personal Journal** (Planned)
- Reflective summarization
- Personal insight extraction
- Emotional context preservation
- Life lesson documentation

### Project Structure

```
chat2substack/
├── src/                 # Core pipeline source code
│   ├── ingest/          # HTML and text ingestion
│   ├── redact/          # PII redaction system
│   ├── llm/             # Summarization and guardrails
│   ├── render/          # Markdown and HTML rendering
│   ├── publish/         # Substack integration
│   ├── analysis/        # Anchor extraction and analysis
│   ├── routing/         # Content type detection and routing
│   ├── validate/        # Quality validation and judging
│   └── util/            # Schemas and utilities
├── tests/               # Comprehensive test suite
│   ├── golden_sets/     # Golden set testing framework
│   └── synthetic_benchmark/ # Synthetic test conversations
├── dist/                # Organized output directory
│   ├── posts/           # Final post artifacts
│   ├── conversations/   # Conversation data and analysis
│   ├── reports/         # Processing reports
│   └── archives/        # Historical test runs
├── test_files/          # Development test HTML files
├── tools/               # Development and integration tools
│   └── playwright/      # Node.js dependencies for Substack integration
├── prompts/             # System prompts
├── inbox/               # Input files for processing
├── config.yaml          # Configuration
└── README.md            # This file
```

## CI/CD

The GitHub Actions workflow:

1. **Tests**: Runs full test suite
2. **Build**: Processes sample input
3. **Security**: Scans for vulnerabilities
4. **Artifacts**: Uploads generated content
5. **Draft Creation**: Optional Substack publishing

Trigger manually with:
- `input_path`: Path to input file
- `create_draft`: Enable Substack draft creation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Current Status

✅ **Production Ready Features:**
- **Judge-Driven Quality System**: 0-100 scoring with hard fail detection
- **Anchor-Based Extraction**: 50%+ coverage with comprehensive referencing
- **Decision-Centric Technical Journal**: Professional engineering narratives
- **Content Type Detection**: Automatic categorization with confidence scoring
- **Self-Play Improvement**: One-retry enhancement for failed content
- **PII Redaction**: Local, deterministic privacy protection
- **Comprehensive Testing**: Unit, integration, and E2E test coverage
- **CI/CD Pipeline**: Automated testing and artifact generation

✅ **Content Types Supported:**
- **Technical Journal** (Production Ready): Engineering decision extraction, 80/100 pass rate, 54.3% anchor coverage
- **Research Article** (Production Ready): Academic-style summarization with anchor-based extraction, 60/100 pass rate
- **Critique** (Production Ready): Opinion and analysis with balanced perspective, 60/100 pass rate

### 🎯 **Technical Achievements**

- **Quality System**: Judge-driven validation with 0-100 scoring and hard fail detection
- **Anchor Coverage**: 50%+ conversation element referencing for comprehensive content extraction
- **Pass Rate**: 80/100+ quality threshold for production-ready content
- **Content Types**: 3 specialized summarizers with automatic routing
- **Testing Coverage**: Golden set, synthetic benchmark, and mutation testing
- **Self-Play**: One-retry improvement system for failed content
- **Privacy**: Local PII redaction with deterministic patterns
- **Performance**: 1,400+ word technical journals with full section completeness

## Next Steps

### 🚀 **Production Optimization**

**1. Content Type Completion**
- [x] **Research Article**: ✅ Anchor-based extraction and validation implemented
- [x] **Critique**: ✅ Balanced perspective and argument structure implemented
- [ ] **Personal Journal**: Add reflective summarization capabilities
- [ ] **News Analysis**: Current events commentary and analysis

**2. Quality Enhancement**
- [x] **Golden Set Testing**: ✅ Curated test conversations with expected outputs implemented
- [x] **Coverage Analysis**: ✅ Comprehensive content extraction validation implemented
- [ ] **Professional Review**: Human evaluation of output quality
- [ ] **A/B Testing**: Compare different summarizer approaches

**3. Performance Optimization**
- [ ] **Processing Speed**: Optimize anchor extraction and routing
- [ ] **Memory Usage**: Reduce resource consumption for large conversations
- [ ] **Caching**: Implement intelligent caching for repeated content
- [ ] **Parallel Processing**: Multi-threaded content processing

### 🔄 **CI/CD Enhancement**

**1. Automated Testing Pipeline**
- [x] **Multi-Content Type Testing**: ✅ Test all summarizer types in CI implemented
- [x] **Quality Metrics Validation**: ✅ Enforce minimum quality thresholds implemented
- [x] **Regression Testing**: ✅ Prevent quality degradation over time implemented
- [ ] **Performance Benchmarking**: Track processing speed and resource usage

**2. Continuous Integration Features**
- [x] **Automated Content Generation**: ✅ Generate sample posts for each content type implemented
- [ ] **Quality Dashboard**: Visual metrics and coverage reports
- [x] **Artifact Management**: ✅ Organized storage of generated content implemented
- [ ] **Deployment Automation**: Automated publishing to test environments

**3. Testing Infrastructure**
- [x] **Test Data Management**: ✅ Curated conversation datasets implemented
- [x] **Mock LLM Integration**: ✅ Deterministic testing without external APIs implemented
- [x] **Coverage Reporting**: ✅ Detailed analysis of content extraction implemented
- [ ] **Performance Monitoring**: Track and optimize processing speed

## Roadmap

- [ ] Local LLM integration (Ollama, etc.)
- [ ] Image and OG generation
- [ ] Topic segmentation
- [ ] Builder Sentry dashboard
- [ ] Multi-language support
- [ ] Advanced content analysis