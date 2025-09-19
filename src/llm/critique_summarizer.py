"""Critique summarizer for opinion and review content."""

from typing import Dict, List, Any
import re
from ..util.schema import SubstackDraft

class CritiqueSummarizer:
    """Summarizes conversations into critique/opinion format."""
    
    def __init__(self):
        self.max_title_length = 80
        self.max_dek_length = 200
        self.max_tldr_points = 5
        self.max_tags = 6
    
    def summarize_conversation(self, conversation: Dict[str, Any]) -> SubstackDraft:
        """Summarize a conversation into critique format."""
        from ..analysis.anchors import AnchorExtractor
        
        # Extract anchors from conversation
        anchor_extractor = AnchorExtractor()
        anchors = anchor_extractor.extract_anchors(conversation['messages'])
        
        # Extract full conversation text
        full_text = self._extract_full_conversation_text(conversation)
        
        # Extract critique components
        thesis = self._extract_thesis(full_text, anchors)
        context = self._extract_context(full_text, anchors)
        arguments = self._extract_arguments(full_text, anchors)
        counterpoints = self._extract_counterpoints(full_text, anchors)
        stakes = self._extract_stakes(full_text, anchors)
        
        # Build critique narrative
        narrative = {
            'thesis': thesis,
            'context': context,
            'arguments': arguments,
            'counterpoints': counterpoints,
            'stakes': stakes,
            'anchors': anchors
        }
        
        # Generate post content
        content = self._generate_post_content(narrative, conversation)
        
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
    
    def _extract_thesis(self, text: str, anchors: List[Any]) -> str:
        """Extract the main thesis or claim."""
        # Look for explicit thesis statements
        thesis_patterns = [
            r'\b(I argue|I contend|I believe|I think|My thesis|The claim|In my opinion)\b[^.]*\.',
            r'\b(I agree|I disagree)\b[^.]*\.',
            r'\b(My stance|My position)\b[^.]*\.'
        ]
        
        for pattern in thesis_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # Fallback: look for opinion anchors
        opinion_anchors = [a for a in anchors if a.type == 'opinion']
        if opinion_anchors:
            return f"The main argument is that {opinion_anchors[0].text}"
        
        # Default thesis
        return "This discussion presents a critical perspective on the topic"
    
    def _extract_context(self, text: str, anchors: List[Any]) -> str:
        """Extract the context of what is being critiqued."""
        # Look for context indicators
        context_patterns = [
            r'\b(about|regarding|concerning|on the topic of|when it comes to)\b[^.]*\.',
            r'\b(the issue|the problem|the situation|the current state)\b[^.]*\.'
        ]
        
        for pattern in context_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # Fallback: use first part of conversation
        sentences = text.split('.')[:2]
        return '. '.join(sentences).strip() + '.'
    
    def _extract_arguments(self, text: str, anchors: List[Any]) -> List[str]:
        """Extract supporting arguments."""
        arguments = []
        
        # Look for argument indicators
        argument_patterns = [
            r'\b(because|since|given that|the reason|the evidence)\b[^.]*\.',
            r'\b(First|Second|Third|Additionally|Furthermore|Moreover)\b[^.]*\.',
            r'\b(The data|The research|The evidence|Studies show)\b[^.]*\.'
        ]
        
        for pattern in argument_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 20:  # Avoid very short matches
                    arguments.append(match.strip())
        
        # Add anchor-based arguments
        for anchor in anchors[:3]:
            if anchor.type in ['decision', 'research_noun']:
                arguments.append(f"{anchor.text}: {anchor.context[:100]}...")
        
        return arguments[:4]  # Top 4 arguments
    
    def _extract_counterpoints(self, text: str, anchors: List[Any]) -> List[str]:
        """Extract counterpoints or opposing views."""
        counterpoints = []
        
        # Look for counterpoint indicators
        counterpoint_patterns = [
            r'\b(however|but|on the other hand|critics might|steelman|opponents argue)\b[^.]*\.',
            r'\b(while|although|despite|in contrast|conversely)\b[^.]*\.',
            r'\b(Some might say|It could be argued|One might counter)\b[^.]*\.'
        ]
        
        for pattern in counterpoint_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 20:
                    counterpoints.append(match.strip())
        
        # Default counterpoints if none found
        if not counterpoints:
            counterpoints = [
                "Critics might argue that this perspective is too narrow",
                "Some may counter that the evidence is insufficient",
                "Opponents could claim that this approach has limitations"
            ]
        
        return counterpoints[:3]  # Top 3 counterpoints
    
    def _extract_stakes(self, text: str, anchors: List[Any]) -> str:
        """Extract the stakes or consequences."""
        # Look for consequence terms
        consequence_terms = ['risk', 'cost', 'harm', 'benefit', 'trade-off', 'consequence', 'impact', 'implication']
        
        for term in consequence_terms:
            pattern = rf'\b{term}\b[^.]*\.'
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # Default stakes
        return "The implications of this perspective affect how we approach the issue and make decisions"
    
    def _generate_post_content(self, narrative: Dict[str, Any], conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the complete post content."""
        title = self._create_title(narrative, conversation)
        dek = self._create_dek(narrative)
        tldr = self._create_tldr(narrative)
        tags = self._create_tags(narrative)
        body_markdown = self._create_body_markdown(narrative)
        
        return {
            'title': title,
            'dek': dek,
            'tldr': tldr,
            'tags': tags,
            'body_markdown': body_markdown
        }
    
    def _create_title(self, narrative: Dict[str, Any], conversation: Dict[str, Any]) -> str:
        """Create a compelling title for the critique."""
        thesis = narrative.get('thesis', 'Critical Analysis')
        
        # Extract key terms from thesis
        if 'argue' in thesis.lower():
            title = f"Critical Analysis: {thesis.split('argue')[1].strip()[:50]}"
        elif 'think' in thesis.lower():
            title = f"My Take: {thesis.split('think')[1].strip()[:50]}"
        elif 'believe' in thesis.lower():
            title = f"Opinion: {thesis.split('believe')[1].strip()[:50]}"
        else:
            title = f"Critical Analysis: {thesis[:50]}"
        
        return self._truncate_title(title)
    
    def _create_dek(self, narrative: Dict[str, Any]) -> str:
        """Create dek for the critique."""
        thesis = narrative.get('thesis', 'critical perspective')
        context = narrative.get('context', 'the topic')
        
        dek = f"A critical examination of {context.lower()}, arguing that {thesis.lower()[:100]}"
        return self._truncate_dek(dek)
    
    def _create_tldr(self, narrative: Dict[str, Any]) -> List[str]:
        """Create TL;DR for the critique."""
        tldr = []
        
        thesis = narrative.get('thesis', 'Critical perspective')
        tldr.append(f"**Thesis:** {thesis}")
        
        arguments = narrative.get('arguments', [])
        if arguments:
            tldr.append(f"**Arguments:** {len(arguments)} key points")
        
        counterpoints = narrative.get('counterpoints', [])
        if counterpoints:
            tldr.append(f"**Counterpoints:** {len(counterpoints)} opposing views")
        
        stakes = narrative.get('stakes', 'Important implications')
        tldr.append(f"**Stakes:** {stakes[:50]}...")
        
        tldr.append("**Takeaway:** Critical analysis with balanced perspective")
        
        return tldr[:self.max_tldr_points]
    
    def _create_tags(self, narrative: Dict[str, Any]) -> List[str]:
        """Create tags for the critique."""
        base_tags = ['critique', 'opinion', 'analysis']
        
        # Add tags based on content
        thesis = narrative.get('thesis', '').lower()
        if 'argue' in thesis or 'contend' in thesis:
            base_tags.append('argument')
        if 'think' in thesis or 'believe' in thesis:
            base_tags.append('perspective')
        if 'agree' in thesis or 'disagree' in thesis:
            base_tags.append('stance')
        
        # Add tags based on anchors
        anchors = narrative.get('anchors', [])
        for anchor in anchors[:3]:
            if anchor.type == 'opinion':
                base_tags.append(anchor.text.lower().replace(' ', '-'))
        
        return base_tags[:self.max_tags]
    
    def _create_body_markdown(self, narrative: Dict[str, Any]) -> str:
        """Create body markdown for the critique."""
        thesis = narrative.get('thesis', 'Critical Analysis')
        context = narrative.get('context', 'the topic')
        arguments = narrative.get('arguments', [])
        counterpoints = narrative.get('counterpoints', [])
        stakes = narrative.get('stakes', 'Important implications')
        anchors = narrative.get('anchors', [])
        
        markdown = []
        
        # Thesis
        markdown.append("## Thesis")
        markdown.append(thesis)
        markdown.append("")
        
        # Context
        markdown.append("## Context")
        markdown.append(context)
        markdown.append("")
        
        # Arguments
        if arguments:
            markdown.append("## Arguments")
            markdown.append("")
            for i, argument in enumerate(arguments, 1):
                # Add citation if we have anchors
                if anchors and i <= len(anchors):
                    markdown.append(f"{i}. {argument} (msg {anchors[i-1].msg_id})")
                else:
                    markdown.append(f"{i}. {argument}")
            markdown.append("")
        
        # Counterpoints
        if counterpoints:
            markdown.append("## Counterpoints")
            markdown.append("")
            for i, counterpoint in enumerate(counterpoints, 1):
                # Add citation if we have anchors
                if anchors and i <= len(anchors):
                    markdown.append(f"{i}. {counterpoint} (msg {anchors[i-1].msg_id})")
                else:
                    markdown.append(f"{i}. {counterpoint}")
            markdown.append("")
        
        # Stakes
        markdown.append("## Stakes")
        markdown.append(stakes)
        markdown.append("")
        
        # Takeaway
        markdown.append("## Takeaway")
        markdown.append("This critique provides a balanced perspective on the issue, considering both supporting arguments and opposing views. The analysis highlights the key implications and consequences of different approaches.")
        
        return '\n'.join(markdown)
    
    def _truncate_title(self, title: str, max_length: int = 80) -> str:
        """Truncate title to fit within character limit."""
        if len(title) <= max_length:
            return title
        return title[:max_length-3] + "..."
    
    def _truncate_dek(self, dek: str, max_length: int = 200) -> str:
        """Truncate dek to fit within character limit."""
        if len(dek) <= max_length:
            return dek
        return dek[:max_length-3] + "..."