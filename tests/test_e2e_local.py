"""End-to-end tests for the complete pipeline."""

import pytest
import tempfile
import json
from pathlib import Path
from src.run import Chat2SubstackPipeline


class TestE2EPipeline:
    """Test end-to-end pipeline functionality."""
    
    def test_pipeline_with_html_input(self):
        """Test complete pipeline with HTML input."""
        # Create sample HTML content
        html_content = """
        <html>
        <head><title>AI Discussion - ChatGPT</title></head>
        <body>
            <h1>Understanding Artificial Intelligence</h1>
            <div class="conversation-turn">
                <div data-message-author-role="user">What is artificial intelligence and how does it work?</div>
            </div>
            <div class="conversation-turn">
                <div data-message-author-role="assistant">Artificial intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior. It works by using algorithms and data to make decisions, learn from experience, and solve problems in ways that mimic human intelligence.</div>
            </div>
            <div class="conversation-turn">
                <div data-message-author-role="user">What are the main types of AI?</div>
            </div>
            <div class="conversation-turn">
                <div data-message-author-role="assistant">There are three main types of AI: Narrow AI (or Weak AI) which is designed for specific tasks, General AI (or Strong AI) which can perform any intellectual task a human can, and Superintelligence which would surpass human intelligence in all areas.</div>
            </div>
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            # Run pipeline
            pipeline = Chat2SubstackPipeline()
            slug = pipeline.run_pipeline(temp_path, create_draft=False)
            
            # Verify output files exist
            dist_dir = Path("dist")
            assert dist_dir.exists()
            
            markdown_file = dist_dir / f"post_{slug}.md"
            html_file = dist_dir / f"post_{slug}.html"
            meta_file = dist_dir / "draft_meta.json"
            report_file = dist_dir / "run_report.md"
            
            assert markdown_file.exists()
            assert html_file.exists()
            assert meta_file.exists()
            assert report_file.exists()
            
            # Verify markdown content
            markdown_content = markdown_file.read_text()
            assert "# " in markdown_content  # Has title
            assert "**TL;DR**" in markdown_content  # Has TL;DR section
            assert "## Main" in markdown_content  # Has main section
            assert "## Takeaways" in markdown_content  # Has takeaways
            
            # Verify HTML content
            html_content = html_file.read_text()
            assert "<!DOCTYPE html>" in html_content
            assert "<h1>" in html_content
            assert "<h3>TL;DR</h3>" in html_content
            
            # Verify metadata
            meta_content = json.loads(meta_file.read_text())
            assert "slug" in meta_content
            assert "title" in meta_content
            assert "word_count" in meta_content
            assert "tags" in meta_content
            
            # Verify run report
            report_content = report_file.read_text()
            assert "# Chat2Substack Run Report" in report_content
            assert "Word Counts" in report_content
            assert "Redaction Statistics" in report_content
            
        finally:
            Path(temp_path).unlink()
    
    def test_pipeline_with_text_input(self):
        """Test complete pipeline with text input."""
        # Create sample text content
        text_content = """User: What are the benefits of machine learning?

Assistant: Machine learning offers several key benefits including automation of complex tasks, improved decision-making through data analysis, personalization of user experiences, and the ability to identify patterns in large datasets that would be difficult for humans to detect manually.

User: What are some common applications of machine learning?

Assistant: Common applications include recommendation systems (like those used by Netflix and Amazon), image and speech recognition, natural language processing, fraud detection in financial services, medical diagnosis assistance, autonomous vehicles, and predictive analytics in various industries.

User: What challenges does machine learning face?

Assistant: Machine learning faces several challenges including the need for large amounts of high-quality training data, potential bias in algorithms, interpretability issues (black box problem), computational resource requirements, data privacy concerns, and the need for skilled professionals to develop and maintain ML systems."""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(text_content)
            temp_path = f.name
        
        try:
            # Run pipeline
            pipeline = Chat2SubstackPipeline()
            slug = pipeline.run_pipeline(temp_path, create_draft=False)
            
            # Verify output files exist
            dist_dir = Path("dist")
            assert dist_dir.exists()
            
            markdown_file = dist_dir / f"post_{slug}.md"
            html_file = dist_dir / f"post_{slug}.html"
            meta_file = dist_dir / "draft_meta.json"
            
            assert markdown_file.exists()
            assert html_file.exists()
            assert meta_file.exists()
            
            # Verify content quality
            markdown_content = markdown_file.read_text()
            assert "machine learning" in markdown_content.lower()
            assert "benefits" in markdown_content.lower()
            assert "applications" in markdown_content.lower()
            
        finally:
            Path(temp_path).unlink()
    
    def test_pipeline_with_pii_redaction(self):
        """Test pipeline with PII that needs redaction."""
        # Create HTML with PII
        html_content = """
        <html>
        <body>
            <div class="conversation-turn">
                <div data-message-author-role="user">My email is john@example.com and my phone is (555) 123-4567</div>
            </div>
            <div class="conversation-turn">
                <div data-message-author-role="assistant">I understand. Please contact me at support@company.com if you need help.</div>
            </div>
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            # Run pipeline
            pipeline = Chat2SubstackPipeline()
            slug = pipeline.run_pipeline(temp_path, create_draft=False)
            
            # Verify redaction occurred
            markdown_file = Path("dist") / f"post_{slug}.md"
            markdown_content = markdown_file.read_text()
            
            # PII should be redacted
            assert "[email-redacted]" in markdown_content
            assert "[phone-redacted]" in markdown_content
            assert "john@example.com" not in markdown_content
            assert "(555) 123-4567" not in markdown_content
            
            # Verify redaction stats in report
            report_file = Path("dist") / "run_report.md"
            report_content = report_file.read_text()
            assert "emails: 2 redactions" in report_content
            assert "phones: 1 redactions" in report_content
            
        finally:
            Path(temp_path).unlink()
    
    def test_pipeline_idempotency(self):
        """Test that pipeline is idempotent."""
        # Create sample HTML
        html_content = """
        <html>
        <body>
            <div class="conversation-turn">
                <div data-message-author-role="user">What is Python?</div>
            </div>
            <div class="conversation-turn">
                <div data-message-author-role="assistant">Python is a programming language.</div>
            </div>
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            pipeline = Chat2SubstackPipeline()
            
            # Run pipeline first time
            slug1 = pipeline.run_pipeline(temp_path, create_draft=False)
            
            # Get file modification times
            markdown_file = Path("dist") / f"post_{slug1}.md"
            first_mtime = markdown_file.stat().st_mtime
            
            # Run pipeline second time
            slug2 = pipeline.run_pipeline(temp_path, create_draft=False)
            
            # Should be same slug
            assert slug1 == slug2
            
            # File should not have been modified (idempotency)
            second_mtime = markdown_file.stat().st_mtime
            assert first_mtime == second_mtime
            
        finally:
            Path(temp_path).unlink()
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling."""
        # Test with non-existent file
        pipeline = Chat2SubstackPipeline()
        
        with pytest.raises(FileNotFoundError):
            pipeline.run_pipeline("nonexistent.html", create_draft=False)
        
        # Test with invalid file type
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                pipeline.run_pipeline(temp_path, create_draft=False)
        finally:
            Path(temp_path).unlink()
    
    def test_pipeline_with_long_content(self):
        """Test pipeline with longer content."""
        # Create longer conversation
        html_content = """
        <html>
        <body>
        """ + "".join(f"""
            <div class="conversation-turn">
                <div data-message-author-role="user">Question {i}: What is the answer to question {i}?</div>
            </div>
            <div class="conversation-turn">
                <div data-message-author-role="assistant">Answer {i}: This is a detailed answer to question {i} that provides comprehensive information about the topic and explains various aspects in detail.</div>
            </div>
        """ for i in range(1, 11)) + """
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            pipeline = Chat2SubstackPipeline()
            slug = pipeline.run_pipeline(temp_path, create_draft=False)
            
            # Verify output
            markdown_file = Path("dist") / f"post_{slug}.md"
            markdown_content = markdown_file.read_text()
            
            # Should have substantial content
            assert len(markdown_content) > 500
            assert "Question" in markdown_content
            assert "Answer" in markdown_content
            
            # Verify word count in metadata
            meta_file = Path("dist") / "draft_meta.json"
            meta_content = json.loads(meta_file.read_text())
            assert meta_content["word_count"] > 100
            
        finally:
            Path(temp_path).unlink()
    
    def test_pipeline_config_loading(self):
        """Test pipeline with custom config."""
        # Create custom config
        custom_config = {
            'length': {'target_words': 200, 'hard_cap_words': 500},
            'manual_paste': {'max_chars': 5000},
            'redaction': {
                'pseudonymize_private_names': True,
                'private_name_list': ['John Doe'],
                'allow_public_figures': True
            },
            'substack': {'host': 'https://test.substack.com', 'create_draft': False},
            'guardrails': {'blocked_phrases': ['spam'], 'enforce_tone': True},
            'citations': {'enable_further_reading': True},
            'storage': {'keep_input_html': False, 'keep_sanitized_json': True},
            'models': {'provider': 'local', 'primary': 'template', 'temperature': 0.2}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(custom_config, f)
            config_path = f.name
        
        try:
            # Create sample content
            html_content = """
            <html>
            <body>
                <div class="conversation-turn">
                    <div data-message-author-role="user">John Doe asked about spam prevention</div>
                </div>
                <div class="conversation-turn">
                    <div data-message-author-role="assistant">Spam prevention involves several techniques.</div>
                </div>
            </body>
            </html>
            """
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_content)
                temp_path = f.name
            
            try:
                # Run pipeline with custom config
                pipeline = Chat2SubstackPipeline(config_path)
                slug = pipeline.run_pipeline(temp_path, create_draft=False)
                
                # Verify redaction of private name
                markdown_file = Path("dist") / f"post_{slug}.md"
                markdown_content = markdown_file.read_text()
                assert "J(pseudonym)" in markdown_content
                assert "John Doe" not in markdown_content
                
            finally:
                Path(temp_path).unlink()
                
        finally:
            Path(config_path).unlink()
