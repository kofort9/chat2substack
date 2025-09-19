"""Research article summarizer with anchor-based extraction."""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

class ResearchAnchor(BaseModel):
    """A key research anchor extracted from conversation."""
    msg_id: int
    topic: str
    context: str
    significance: str
    evidence: str

class ResearchMethodology(BaseModel):
    """Research methodology used."""
    approach: str
    data_source: str
    analysis_method: str
    limitations: Optional[str] = None

class ResearchArticleSummarizer:
    """Summarizes conversations into research article format using anchor extraction."""
    
    def __init__(self):
        self.max_title_length = 80
        self.max_dek_length = 200
        self.max_tldr_points = 5
        self.max_tags = 6
        
        # Research domain lexicons for anchor extraction
        self.research_lexicons = {
            'technical': [
                'ray', 'anyscale', 'rag', 'llm', 'fine-tuning', 'distributed', 'parallel',
                'workflow', 'pipeline', 'architecture', 'model', 'training', 'inference',
                'api', 'framework', 'algorithm', 'optimization', 'performance', 'benchmark'
            ],
            'academic': [
                'research', 'study', 'analysis', 'methodology', 'literature', 'review',
                'paper', 'article', 'thesis', 'dissertation', 'citation', 'reference',
                'findings', 'results', 'evidence', 'hypothesis', 'conclusion'
            ],
            'societal': [
                'post-capitalist', 'democracy', 'ethical', 'ai', 'artificial intelligence',
                'reading list', 'book', 'author', 'mba', 'education', 'system', 'economy',
                'policy', 'regulation', 'governance', 'society', 'culture'
            ]
        }
    
    def summarize_conversation(self, conversation: Dict[str, Any]) -> 'SubstackDraft':
        """Summarize a conversation into research article format using anchor extraction."""
        from ..util.schema import SubstackDraft
        
        # Extract full conversation text
        full_text = self._extract_full_conversation_text(conversation)
        
        # Extract research anchors from conversation
        anchors = self._extract_research_anchors(conversation['messages'])
        
        # Extract main research topic and question
        main_topic = self._extract_main_topic(anchors, full_text)
        research_question = self._extract_research_question_from_anchors(anchors, full_text)
        
        # Build research narrative from anchors
        narrative = {
            'main_topic': main_topic,
            'research_question': research_question,
            'anchors': anchors,
            'key_insights': self._extract_insights_from_anchors(anchors),
            'methodology': self._extract_methodology_from_anchors(anchors, full_text),
            'findings': self._extract_findings_from_anchors(anchors)
        }
        
        # Generate post content from narrative
        content = self._generate_post_content_from_narrative(narrative, conversation)
        
        # Convert to SubstackDraft
        return SubstackDraft(
            title=content['title'],
            dek=content['dek'],
            tldr=content['tldr'],
            tags=content['tags'],
            body_markdown=content['body_markdown'],
            further_reading=None
        )
    
    def _extract_full_conversation_text(self, conversation: Dict[str, Any]) -> str:
        """Extract all text from the conversation messages."""
        messages = conversation.get('messages', [])
        return ' '.join([msg.get('content', '') for msg in messages])
    
    def _extract_research_anchors(self, messages: List[Dict[str, Any]]) -> List[ResearchAnchor]:
        """Extract research anchors from conversation messages."""
        anchors = []
        
        # Extract anchors from each message
        for i, msg in enumerate(messages):
            content = msg.get('content', '')
            text_lower = content.lower()
            
            # Extract technical anchors
            for term in self.research_lexicons['technical']:
                if term in text_lower:
                    context = self._extract_context_around_term(content, term)
                    anchors.append(ResearchAnchor(
                        msg_id=i,
                        topic=term.title(),
                        context=context,
                        significance=f"Technical component: {term}",
                        evidence=f"Mentioned in conversation context: {context[:100]}..."
                    ))
            
            # Extract academic anchors
            for term in self.research_lexicons['academic']:
                if term in text_lower:
                    context = self._extract_context_around_term(content, term)
                    anchors.append(ResearchAnchor(
                        msg_id=i,
                        topic=term.title(),
                        context=context,
                        significance=f"Academic concept: {term}",
                        evidence=f"Referenced in discussion: {context[:100]}..."
                    ))
            
            # Extract societal anchors
            for term in self.research_lexicons['societal']:
                if term in text_lower:
                    context = self._extract_context_around_term(content, term)
                    anchors.append(ResearchAnchor(
                        msg_id=i,
                        topic=term.title(),
                        context=context,
                        significance=f"Policy aspect: {term}",
                        evidence=f"Discussed in context: {context[:100]}..."
                    ))
        
        # Remove duplicates and return top anchors
        unique_anchors = []
        seen_topics = set()
        for anchor in anchors:
            if anchor.topic.lower() not in seen_topics:
                unique_anchors.append(anchor)
                seen_topics.add(anchor.topic.lower())
        
        return unique_anchors[:6]  # Top 6 anchors
    
    def _extract_context_around_term(self, text: str, term: str) -> str:
        """Extract context around a specific term."""
        pattern = rf'.{{0,100}}{re.escape(term)}.{{0,100}}'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches[0] if matches else f"Discussion about {term}"
    
    def _extract_main_topic(self, anchors: List[ResearchAnchor], text: str) -> str:
        """Extract the main research topic from anchors."""
        if not anchors:
            return "Research Analysis"
        
        # Find the most significant anchor
        technical_anchors = [a for a in anchors if a.topic.lower() in self.research_lexicons['technical']]
        if technical_anchors:
            return f"{technical_anchors[0].topic} Research"
        
        societal_anchors = [a for a in anchors if a.topic.lower() in self.research_lexicons['societal']]
        if societal_anchors:
            return f"{societal_anchors[0].topic} Analysis"
        
        return f"{anchors[0].topic} Research"
    
    def _extract_research_question_from_anchors(self, anchors: List[ResearchAnchor], text: str) -> str:
        """Extract research question from anchors."""
        if not anchors:
            return "What are the key insights from this research discussion?"
        
        # Build question based on main anchors
        main_topics = [a.topic for a in anchors[:3]]
        if len(main_topics) == 1:
            return f"What are the implications and applications of {main_topics[0]}?"
        elif len(main_topics) == 2:
            return f"How does {main_topics[0]} relate to {main_topics[1]}?"
        else:
            return f"What are the key insights about {', '.join(main_topics[:2])} and their implications?"
    
    def _extract_insights_from_anchors(self, anchors: List[ResearchAnchor]) -> List[str]:
        """Extract key insights from research anchors."""
        insights = []
        
        for anchor in anchors[:4]:
            insights.append(f"{anchor.topic}: {anchor.significance}")
        
        if not insights:
            insights = [
                "The discussion revealed important research insights",
                "Key concepts and methodologies were explored",
                "Practical applications and implications were identified"
            ]
        
        return insights[:5]
    
    def _extract_methodology_from_anchors(self, anchors: List[ResearchAnchor], text: str) -> str:
        """Extract methodology from anchors."""
        technical_terms = [a.topic for a in anchors if a.topic.lower() in self.research_lexicons['technical']]
        
        if 'Ray' in technical_terms and 'Rag' in technical_terms:
            return "Distributed RAG workflow analysis using Ray framework"
        elif 'Reading List' in [a.topic for a in anchors]:
            return "Literature review and curated reading analysis"
        elif 'Fine-Tuning' in technical_terms:
            return "Distributed model fine-tuning methodology"
        else:
            return "Research analysis and discussion methodology"
    
    def _extract_findings_from_anchors(self, anchors: List[ResearchAnchor]) -> List[str]:
        """Extract findings from research anchors."""
        findings = []
        
        for anchor in anchors[:3]:
            findings.append(f"{anchor.topic}: {anchor.context[:100]}...")
        
        if not findings:
            findings = [
                "Key research concepts were identified and discussed",
                "Important insights emerged from the analysis",
                "Practical applications were explored"
            ]
        
        return findings
    
    def _extract_research_methodology(self, text: str) -> ResearchMethodology:
        """Extract research methodology from the conversation."""
        text_lower = text.lower()
        
        if 'survey' in text_lower or 'questionnaire' in text_lower:
            return ResearchMethodology(
                approach="Survey-based research methodology",
                data_source="Primary survey data collection",
                analysis_method="Statistical analysis and correlation studies",
                limitations="Sample size and response bias considerations"
            )
        elif 'interview' in text_lower or 'qualitative' in text_lower:
            return ResearchMethodology(
                approach="Qualitative research methodology",
                data_source="In-depth interviews and case studies",
                analysis_method="Thematic analysis and content coding",
                limitations="Generalizability and researcher bias considerations"
            )
        elif 'experiment' in text_lower or 'trial' in text_lower:
            return ResearchMethodology(
                approach="Experimental research design",
                data_source="Controlled experimental data",
                analysis_method="Statistical hypothesis testing and effect size analysis",
                limitations="External validity and control group considerations"
            )
        else:
            return ResearchMethodology(
                approach="Literature review and analysis",
                data_source="Academic literature and secondary sources",
                analysis_method="Systematic review and meta-analysis",
                limitations="Publication bias and source quality considerations"
            )
    
    def _extract_key_insights(self, text: str) -> List[str]:
        """Extract key insights from the research discussion."""
        insights = []
        text_lower = text.lower()
        
        if 'research' in text_lower:
            insights.append("Research findings provide strong evidence for the proposed hypothesis")
        if 'data' in text_lower:
            insights.append("Data analysis reveals significant patterns and trends")
        if 'evidence' in text_lower:
            insights.append("Multiple lines of evidence support the conclusions")
        if 'methodology' in text_lower:
            insights.append("Robust methodology ensures reliable and valid results")
        if 'implications' in text_lower:
            insights.append("Findings have important practical and theoretical implications")
        
        # Default insights
        if not insights:
            insights = [
                "The research provides valuable insights into the topic",
                "Findings contribute to existing knowledge in the field",
                "Methodology ensures reliable and valid results",
                "Results have important implications for practice",
                "Research opens new avenues for future investigation"
            ]
        
        return insights[:5]  # Top 5 insights
    
    def _extract_research_question(self, text: str) -> str:
        """Extract the main research question or topic."""
        text_lower = text.lower()
        
        if 'artificial intelligence' in text_lower or 'ai' in text_lower:
            return "What are the key trends and implications of artificial intelligence development?"
        elif 'machine learning' in text_lower or 'ml' in text_lower:
            return "How does machine learning impact various industries and applications?"
        elif 'data' in text_lower and 'analysis' in text_lower:
            return "What insights can be gained from data analysis and research?"
        elif 'technology' in text_lower:
            return "What are the implications of technological advancement and innovation?"
        else:
            return "What are the key insights and implications of this research topic?"
    
    def _extract_research_topic(self, text: str) -> str:
        """Extract the main research topic."""
        text_lower = text.lower()
        
        if 'artificial intelligence' in text_lower or 'ai' in text_lower:
            return "Artificial Intelligence"
        elif 'machine learning' in text_lower or 'ml' in text_lower:
            return "Machine Learning"
        elif 'data' in text_lower:
            return "Data Analysis"
        elif 'research' in text_lower:
            return "Research"
        elif 'technology' in text_lower:
            return "Technology"
        else:
            return "Research Analysis"
    
    def _generate_post_content_from_narrative(self, narrative: Dict[str, Any], conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the complete post content from research narrative."""
        title = self._create_title_from_narrative(narrative, conversation)
        dek = self._create_dek_from_narrative(narrative)
        tldr = self._create_tldr_from_narrative(narrative)
        tags = self._create_tags_from_narrative(narrative)
        body_markdown = self._create_body_markdown_from_narrative(narrative)
        
        return {
            'title': title,
            'dek': dek,
            'tldr': tldr,
            'tags': tags,
            'body_markdown': body_markdown
        }
    
    def _create_title_from_narrative(self, narrative: Dict[str, Any], conversation: Dict[str, Any]) -> str:
        """Create a compelling title from research narrative."""
        main_topic = narrative.get('main_topic', 'Research Analysis')
        anchors = narrative.get('anchors', [])
        
        # Create title based on main topic and key anchors
        if anchors:
            key_terms = [a.topic for a in anchors[:2]]
            if len(key_terms) == 2:
                title = f"{key_terms[0]} and {key_terms[1]}: Research Analysis"
            else:
                title = f"{key_terms[0]}: Research Analysis"
        else:
            title = main_topic
        
        return self._truncate_title(title)
    
    def _create_dek_from_narrative(self, narrative: Dict[str, Any]) -> str:
        """Create dek from research narrative."""
        main_topic = narrative.get('main_topic', 'research')
        research_question = narrative.get('research_question', 'key insights')
        
        dek = f"An analysis of {main_topic.lower()}, exploring {research_question.lower()} and their implications for the field."
        return self._truncate_dek(dek)
    
    def _create_tldr_from_narrative(self, narrative: Dict[str, Any]) -> List[str]:
        """Create TL;DR from research narrative."""
        main_topic = narrative.get('main_topic', 'Research')
        research_question = narrative.get('research_question', 'Key insights')
        anchors = narrative.get('anchors', [])
        methodology = narrative.get('methodology', 'Research analysis')
        
        tldr = []
        tldr.append(f"**Topic:** {main_topic}")
        tldr.append(f"**Question:** {research_question}")
        tldr.append(f"**Methodology:** {methodology}")
        
        if anchors:
            tldr.append(f"**Key Concepts:** {', '.join([a.topic for a in anchors[:3]])}")
        
        tldr.append(f"**Insights:** {len(narrative.get('key_insights', []))} key findings identified")
        
        return tldr[:self.max_tldr_points]
    
    def _create_tags_from_narrative(self, narrative: Dict[str, Any]) -> List[str]:
        """Create tags from research narrative."""
        anchors = narrative.get('anchors', [])
        main_topic = narrative.get('main_topic', 'Research').lower()
        
        base_tags = ['research', 'analysis', 'insights']
        
        # Add tags based on anchors
        for anchor in anchors[:3]:
            if anchor.topic.lower() in self.research_lexicons['technical']:
                base_tags.append(anchor.topic.lower().replace(' ', '-'))
            elif anchor.topic.lower() in self.research_lexicons['societal']:
                base_tags.append(anchor.topic.lower().replace(' ', '-'))
        
        # Add topic-specific tags
        if 'ray' in main_topic or 'rag' in main_topic:
            base_tags.extend(['ray', 'rag', 'distributed-computing'])
        elif 'reading' in main_topic or 'list' in main_topic:
            base_tags.extend(['literature-review', 'reading-list', 'academic'])
        elif 'ethical' in main_topic or 'ai' in main_topic:
            base_tags.extend(['ai-ethics', 'artificial-intelligence', 'policy'])
        
        return base_tags[:self.max_tags]
    
    def _create_body_markdown_from_narrative(self, narrative: Dict[str, Any]) -> str:
        """Create body markdown from research narrative."""
        main_topic = narrative.get('main_topic', 'Research Analysis')
        research_question = narrative.get('research_question', 'Key insights')
        anchors = narrative.get('anchors', [])
        key_insights = narrative.get('key_insights', [])
        methodology = narrative.get('methodology', 'Research analysis')
        findings = narrative.get('findings', [])
        
        markdown = []
        
        # Abstract
        markdown.append("## Abstract")
        markdown.append(f"This analysis explores {main_topic.lower()} and addresses: {research_question}")
        markdown.append("")
        
        # Research Question
        markdown.append("## Research Question")
        markdown.append(research_question)
        markdown.append("")
        
        # Methodology
        markdown.append("## Methodology")
        markdown.append(f"**Approach:** {methodology}")
        markdown.append(f"**Data Source:** Conversation analysis and expert discussion")
        markdown.append(f"**Analysis Method:** Anchor extraction and thematic analysis")
        markdown.append("")
        
        # Key Concepts
        if anchors:
            markdown.append("## Key Concepts")
            markdown.append("")
            for i, anchor in enumerate(anchors[:4], 1):
                markdown.append(f"### {i}. {anchor.topic}")
                markdown.append(f"**Context:** {anchor.context[:150]}... (msg {anchor.msg_id})")
                markdown.append(f"**Significance:** {anchor.significance}")
                markdown.append("")
        
        # Key Insights
        if key_insights:
            markdown.append("## Key Insights")
            markdown.append("")
            for i, insight in enumerate(key_insights[:4], 1):
                # Add citation to first insight
                if i == 1 and anchors:
                    markdown.append(f"{i}. {insight} (msg {anchors[0].msg_id})")
                else:
                    markdown.append(f"{i}. {insight}")
            markdown.append("")
        
        # Findings
        if findings:
            markdown.append("## Findings")
            markdown.append("")
            for i, finding in enumerate(findings[:3], 1):
                # Add citation to findings
                if anchors and i <= len(anchors):
                    markdown.append(f"**Finding {i}:** {finding} (msg {anchors[i-1].msg_id})")
                else:
                    markdown.append(f"**Finding {i}:** {finding}")
            markdown.append("")
        
        # Discussion
        markdown.append("## Discussion")
        markdown.append(f"The analysis of {main_topic.lower()} provides insights into the topic and its practical applications.")
        markdown.append("")
        
        # Implications
        markdown.append("## Implications")
        markdown.append("The findings have important implications for:")
        markdown.append("- **Researchers:** New avenues for investigation and methodology")
        markdown.append("- **Practitioners:** Evidence-based approaches and applications")
        markdown.append("- **Policy Makers:** Informed decision-making and strategic planning")
        markdown.append("")
        
        # Conclusion
        markdown.append("## Conclusion")
        markdown.append(f"This research analysis demonstrates the importance of {main_topic.lower()} and provides a foundation for future research in the field. The findings contribute to our collective understanding and offer practical insights for various stakeholders.")
        markdown.append("")
        
        # Future Research
        markdown.append("## Future Research Directions")
        markdown.append("Future research should focus on:")
        markdown.append("- Expanding the scope of investigation to include additional variables")
        markdown.append("- Longitudinal studies to track changes over time")
        markdown.append("- Cross-cultural and comparative analysis")
        markdown.append("- Implementation studies to assess practical applications")
        
        return '\n'.join(markdown)
    
    def _create_title(self, narrative: Dict[str, Any], conversation: Dict[str, Any]) -> str:
        """Create a compelling title for the research article."""
        topic = narrative.get('topic', 'Research')
        research_question = narrative.get('research_question', 'Key Insights')
        
        # Create title based on topic and research question
        if 'artificial intelligence' in topic.lower() or 'ai' in topic.lower():
            title = f"Understanding AI: Research Insights and Implications"
        elif 'machine learning' in topic.lower() or 'ml' in topic.lower():
            title = f"Machine Learning Research: Trends and Applications"
        elif 'data' in topic.lower():
            title = f"Data Analysis Research: Key Findings and Insights"
        else:
            # Truncate research question if too long
            if len(research_question) > 50:
                research_question = research_question[:47] + "..."
            title = f"Research Analysis: {research_question}"
        
        return self._truncate_title(title)
    
    def _create_dek(self, narrative: Dict[str, Any]) -> str:
        """Create a compelling dek (subtitle)."""
        topic = narrative.get('topic', 'research')
        findings = narrative.get('findings', [])
        
        if findings:
            dek = f"An in-depth analysis of {topic.lower()} research, examining key findings, methodology, and implications for the field."
        else:
            dek = f"A comprehensive research analysis exploring {topic.lower()} and its implications."
        
        return self._truncate_dek(dek)
    
    def _create_tldr(self, narrative: Dict[str, Any]) -> List[str]:
        """Create TL;DR points for the research article."""
        findings = narrative.get('findings', [])
        methodology = narrative.get('methodology')
        key_insights = narrative.get('key_insights', [])
        
        tldr = []
        
        # Problem/Question
        research_question = narrative.get('research_question', 'Research analysis')
        tldr.append(f"**Research Question:** {research_question}")
        
        # Methodology
        if methodology:
            tldr.append(f"**Methodology:** {methodology.approach}")
        
        # Key Findings
        if findings:
            tldr.append(f"**Key Findings:** {len(findings)} major findings identified")
        
        # Insights
        if key_insights:
            tldr.append(f"**Insights:** {len(key_insights)} key insights for practitioners")
        
        # Implications
        tldr.append(f"**Implications:** Research has important implications for the field")
        
        return tldr[:self.max_tldr_points]
    
    def _create_tags(self, narrative: Dict[str, Any]) -> List[str]:
        """Create relevant tags for the research article."""
        topic = narrative.get('topic', 'research').lower()
        findings = narrative.get('findings', [])
        
        base_tags = ['research', 'analysis', 'academic', 'insights']
        
        # Add topic-specific tags
        if 'artificial intelligence' in topic or 'ai' in topic:
            base_tags.extend(['ai', 'artificial-intelligence', 'technology'])
        elif 'machine learning' in topic or 'ml' in topic:
            base_tags.extend(['machine-learning', 'ml', 'data-science'])
        elif 'data' in topic:
            base_tags.extend(['data-analysis', 'statistics', 'research'])
        else:
            base_tags.extend(['research', 'analysis', 'insights'])
        
        # Add methodology tags
        if findings:
            base_tags.append('empirical-research')
        
        return base_tags[:self.max_tags]
    
    def _create_body_markdown(self, narrative: Dict[str, Any]) -> str:
        """Create the body markdown with proper research article structure."""
        markdown = []
        
        # Abstract/Introduction
        markdown.append("## Abstract")
        research_question = narrative.get('research_question', 'Research analysis')
        topic = narrative.get('topic', 'the subject')
        markdown.append(f"This research analysis examines {topic.lower()} through a comprehensive review of existing literature and data. The study addresses the question: {research_question}")
        markdown.append("")
        
        # Research Question
        markdown.append("## Research Question")
        markdown.append(research_question)
        markdown.append("")
        
        # Methodology
        methodology = narrative.get('methodology')
        if methodology:
            markdown.append("## Methodology")
            markdown.append(f"**Approach:** {methodology.approach}")
            markdown.append(f"**Data Source:** {methodology.data_source}")
            markdown.append(f"**Analysis Method:** {methodology.analysis_method}")
            if methodology.limitations:
                markdown.append(f"**Limitations:** {methodology.limitations}")
            markdown.append("")
        
        # Key Findings
        findings = narrative.get('findings', [])
        if findings:
            markdown.append("## Key Findings")
            markdown.append("")
            for i, finding in enumerate(findings[:3], 1):
                markdown.append(f"### Finding {i}: {finding.finding}")
                markdown.append(f"**Evidence:** {finding.evidence}")
                markdown.append(f"**Significance:** {finding.significance}")
                if finding.source:
                    markdown.append(f"**Source:** {finding.source}")
                markdown.append("")
        
        # Key Insights
        key_insights = narrative.get('key_insights', [])
        if key_insights:
            markdown.append("## Key Insights")
            markdown.append("")
            for i, insight in enumerate(key_insights[:4], 1):
                markdown.append(f"{i}. {insight}")
            markdown.append("")
        
        # Discussion
        markdown.append("## Discussion")
        markdown.append("The research findings provide valuable insights into the topic and contribute to our understanding of the field. The methodology employed ensures reliable and valid results that can inform future research and practice.")
        markdown.append("")
        
        # Implications
        markdown.append("## Implications")
        markdown.append("The findings have important implications for:")
        markdown.append("- **Researchers:** New avenues for investigation and methodology")
        markdown.append("- **Practitioners:** Evidence-based approaches and best practices")
        markdown.append("- **Policy Makers:** Informed decision-making and strategic planning")
        markdown.append("")
        
        # Conclusion
        markdown.append("## Conclusion")
        markdown.append("This research analysis demonstrates the importance of evidence-based investigation and provides a foundation for future research in the field. The findings contribute to our collective understanding and offer practical insights for various stakeholders.")
        markdown.append("")
        
        # Future Research
        markdown.append("## Future Research Directions")
        markdown.append("Future research should focus on:")
        markdown.append("- Expanding the scope of investigation to include additional variables")
        markdown.append("- Longitudinal studies to track changes over time")
        markdown.append("- Cross-cultural and comparative analysis")
        markdown.append("- Implementation studies to assess practical applications")
        
        return '\n'.join(markdown)
    
    def _truncate_title(self, title: str) -> str:
        """Truncate title to fit within character limit."""
        if len(title) <= self.max_title_length:
            return title
        return title[:self.max_title_length-3] + "..."
    
    def _truncate_dek(self, dek: str) -> str:
        """Truncate dek to fit within character limit."""
        if len(dek) <= self.max_dek_length:
            return dek
        return dek[:self.max_dek_length-3] + "..."
