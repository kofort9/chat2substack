# Chat2Substack

A Proof of Concept (PoC) personal efficiency tool that converts ChatGPT conversations into professional Substack draft content. Built with a judge-driven quality system, anchor-based extraction, and decision-centric summarization to streamline content creation workflows.

## Purpose

Chat2Substack is a personal efficiency tool designed to streamline the process of transforming AI conversations into structured content. It addresses common workflow challenges:

- **Content Quality**: Provides structured output with quality scoring for personal review
- **Privacy Protection**: Local PII redaction prevents sensitive information leakage
- **Content Structure**: Transforms conversational data into organized, narrative content
- **Type Specialization**: Automatically detects and optimizes for different content types
- **Workflow Efficiency**: Generates draft content that can be refined and published

## Architecture

### Core Pipeline Flow

```
Input → Ingest → Redact → Analyze → Route → Summarize → Judge → Render → Output
```

### System Components

#### 1. **Input Processing** (`src/ingest/`)
- **HTML Parser**: Extracts conversation structure from ChatGPT shared links by parsing the embedded JavaScript data and converting it to a normalized conversation format. Handles the complex HTML structure that ChatGPT uses to store conversation data.
- **Text Parser**: Handles manual text input with intelligent role detection using patterns like "User:", "Assistant:", "Q:", "A:" to identify speaker turns and maintain conversation flow.
- **Content Normalization**: Standardizes conversation format across different input types, ensuring consistent data structure for downstream processing regardless of input source.

#### 2. **Privacy Protection** (`src/redact/`)
- **PII Detection**: Uses regex patterns and heuristics to identify emails, phone numbers, addresses, SSNs, and private names. Implements sophisticated pattern matching to catch various formats and edge cases.
- **Deterministic Redaction**: Applies consistent replacement patterns (e.g., `[email-redacted]`, `[phone-redacted]`) to ensure privacy while maintaining text readability and structure.
- **Public Figure Preservation**: Maintains references to well-known public individuals while redacting private personal information, using configurable whitelists and heuristics.

#### 3. **Content Analysis** (`src/analysis/`)
- **Anchor Extraction**: Identifies and extracts key concepts, engineering decisions, commands, citations, and other important elements from conversations. Uses pattern matching, keyword detection, and context analysis to build a comprehensive knowledge graph of the conversation.
- **Signal Detection**: Extracts technical, academic, and opinion indicators to help determine content type and appropriate summarization approach. Analyzes language patterns, terminology, and discourse markers.
- **Coverage Analysis**: Measures how comprehensively the content extraction captures the original conversation, providing metrics on what percentage of important elements are referenced in the final output.

#### 4. **Intelligent Routing** (`src/routing/`)
- **Content Type Detection**: Automatically categorizes conversations into technical journal, research article, critique, or other types using keyword analysis, pattern matching, and confidence scoring. Implements tie-breaking logic for ambiguous cases.
- **Confidence Scoring**: Provides reliability metrics for classification decisions, allowing the system to abstain from processing when confidence is too low or content is too ambiguous.
- **Fallback Logic**: Handles ambiguous content with abstain mechanisms, ensuring the system doesn't force inappropriate content types when the conversation doesn't clearly fit established patterns.

#### 5. **Specialized Summarization** (`src/llm/`)
- **Technical Journal**: Generates decision-centric engineering narratives that focus on key technical decisions, their rationale, evidence, and outcomes. Structures content around engineering decision logs, technical stack, challenges, and results.
- **Research Article**: Creates academic-style analysis with methodology sections, research questions, findings, and discussion. Emphasizes evidence-based conclusions and scholarly presentation.
- **Critique**: Produces balanced opinion and argument structure with thesis statements, supporting arguments, counterpoints, and stakes analysis. Maintains objective tone while presenting subjective viewpoints.
- **Self-Play Improvement**: Implements one-retry enhancement for failed content by analyzing judge feedback and attempting to address specific quality issues through content expansion or structural improvements.

#### 6. **Quality Validation** (`src/validate/`)
- **Judge System**: Implements comprehensive 0-100 scoring with hard fail detection based on multiple criteria including section completeness, anchor coverage, evidence density, and content quality. Provides detailed feedback on why content passes or fails.
- **Section Completeness**: Ensures required content sections are present and properly formatted, checking for TL;DR, decision logs, commands, and other content-type-specific requirements.
- **Anchor Coverage**: Validates that a sufficient percentage (50%+) of conversation elements are referenced in the final output, ensuring comprehensive content extraction.
- **Evidence Density**: Measures the substantiation quality of claims and decisions, ensuring the output is well-supported rather than purely speculative.

#### 7. **Output Generation** (`src/render/`)
- **Markdown Rendering**: Produces clean, Substack-optimized formatting with proper headers, lists, code blocks, and citations. Ensures compatibility with Substack's markdown parser and display requirements.
- **HTML Conversion**: Converts markdown to web-ready HTML with proper structure, styling, and accessibility considerations. Maintains formatting consistency across different display contexts.
- **Metadata Generation**: Creates comprehensive metadata including quality scores, coverage metrics, processing statistics, and content type information for tracking and analysis purposes.

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

## Disclaimer

**This is a Proof of Concept (PoC) personal efficiency tool. It is not production-ready software and should not be used for commercial purposes. The tool is provided as-is for personal experimentation and learning purposes.**

### Important Notes:
- Generated content should always be reviewed before publication
- The tool may produce inaccurate or incomplete content
- No warranty or support is provided
- Use at your own risk

## License

MIT License - see LICENSE file for details.

## Current Status

✅ **PoC Features Implemented:**
- **Judge-Driven Quality System**: 0-100 scoring with hard fail detection
- **Anchor-Based Extraction**: 50%+ coverage with comprehensive referencing
- **Decision-Centric Technical Journal**: Engineering narrative generation
- **Content Type Detection**: Automatic categorization with confidence scoring
- **Self-Play Improvement**: One-retry enhancement for failed content
- **PII Redaction**: Local, deterministic privacy protection
- **Comprehensive Testing**: Unit, integration, and E2E test coverage
- **CI/CD Pipeline**: Automated testing and artifact generation

✅ **Content Types Supported:**
- **Technical Journal** (PoC Complete): Engineering decision extraction, 80/100 pass rate, 54.3% anchor coverage
- **Research Article** (PoC Complete): Academic-style summarization with anchor-based extraction, 60/100 pass rate
- **Critique** (PoC Complete): Opinion and analysis with balanced perspective, 60/100 pass rate

### 🎯 **PoC Technical Achievements**

- **Quality System**: Judge-driven validation with 0-100 scoring and hard fail detection
- **Anchor Coverage**: 50%+ conversation element referencing for comprehensive content extraction
- **Pass Rate**: 80/100+ quality threshold for technical journals
- **Content Types**: 3 specialized summarizers with automatic routing
- **Testing Coverage**: Golden set, synthetic benchmark, and mutation testing
- **Self-Play**: One-retry improvement system for failed content
- **Privacy**: Local PII redaction with deterministic patterns
- **Performance**: 1,400+ word technical journals with full section completeness

### ⚠️ **PoC Limitations**

- **Personal Use Only**: Not designed for production or commercial use
- **Experimental**: Some features may be unstable or incomplete
- **Local Processing**: Requires local setup and configuration
- **Manual Review**: Generated content should be reviewed before publication
- **Limited Support**: Community-driven development with no formal support

## Next Steps

### 🔧 **PoC Enhancement**

**1. Content Type Completion**
- [x] **Research Article**: ✅ Anchor-based extraction and validation implemented
- [x] **Critique**: ✅ Balanced perspective and argument structure implemented
- [ ] **Personal Journal**: Add reflective summarization capabilities
- [ ] **News Analysis**: Current events commentary and analysis

**2. Quality Enhancement**
- [x] **Golden Set Testing**: ✅ Curated test conversations with expected outputs implemented
- [x] **Coverage Analysis**: ✅ Comprehensive content extraction validation implemented
- [ ] **User Feedback Integration**: Incorporate user feedback for improvement
- [ ] **A/B Testing**: Compare different summarizer approaches

**3. Performance Optimization**
- [ ] **Processing Speed**: Optimize anchor extraction and routing
- [ ] **Memory Usage**: Reduce resource consumption for large conversations
- [ ] **Caching**: Implement intelligent caching for repeated content
- [ ] **Parallel Processing**: Multi-threaded content processing

### 🔄 **Development Enhancement**

**1. Testing Pipeline**
- [x] **Multi-Content Type Testing**: ✅ Test all summarizer types in CI implemented
- [x] **Quality Metrics Validation**: ✅ Enforce minimum quality thresholds implemented
- [x] **Regression Testing**: ✅ Prevent quality degradation over time implemented
- [ ] **Performance Benchmarking**: Track processing speed and resource usage

**2. Development Features**
- [x] **Automated Content Generation**: ✅ Generate sample posts for each content type implemented
- [ ] **Quality Dashboard**: Visual metrics and coverage reports
- [x] **Artifact Management**: ✅ Organized storage of generated content implemented
- [ ] **Development Automation**: Streamlined development workflows

**3. Testing Infrastructure**
- [x] **Test Data Management**: ✅ Curated conversation datasets implemented
- [x] **Mock LLM Integration**: ✅ Deterministic testing without external APIs implemented
- [x] **Coverage Reporting**: ✅ Detailed analysis of content extraction implemented
- [ ] **Performance Monitoring**: Track and optimize processing speed

## Roadmap

- [ ] Local LLM integration (Ollama, etc.)
- [ ] Image and OG generation
- [ ] Topic segmentation
- [ ] Multi-language support
- [ ] Advanced content analysis
- [ ] User interface improvements
- [ ] Batch processing capabilities