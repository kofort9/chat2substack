"""Advanced topic extraction algorithms for better content analysis."""

import re
from typing import List, Dict, Any, Tuple
from collections import Counter


class AdvancedTopicExtractor:
    """Advanced topic extraction using multiple algorithms and techniques."""
    
    def __init__(self):
        self.technical_domains = {
            'ai_ml': [
                'machine learning', 'artificial intelligence', 'neural network', 'deep learning',
                'llm', 'language model', 'transformer', 'gpt', 'ollama', 'litellm',
                'reinforcement learning', 'self-correcting', 'function calling', 'reasoning',
                'deepseek', 'qwen', 'llama', 'codestral', 'mistral'
            ],
            'development': [
                'programming', 'coding', 'development', 'software', 'application', 'app',
                'python', 'javascript', 'typescript', 'bash', 'shell', 'yaml', 'json',
                'api', 'rest', 'graphql', 'database', 'server', 'client', 'framework',
                'library', 'package', 'module', 'function', 'class', 'method', 'variable'
            ],
            'devops': [
                'deployment', 'ci/cd', 'github actions', 'docker', 'kubernetes', 'aws',
                'azure', 'gcp', 'infrastructure', 'runner', 'self-hosted', 'workflow',
                'pipeline', 'automation', 'testing', 'pytest', 'coverage', 'quality'
            ],
            'tools': [
                'git', 'github', 'cursor', 'vscode', 'terminal', 'cli', 'gui',
                'homebrew', 'pip', 'npm', 'yarn', 'conda', 'venv', 'virtualenv',
                'black', 'flake8', 'mypy', 'isort', 'linting', 'formatting'
            ],
            'hardware': [
                'gpu', 'rtx', 'vram', 'memory', 'cpu', 'm1', 'macos', 'linux',
                'windows', 'hardware', 'performance', 'optimization', 'quantization'
            ]
        }
        
        self.project_keywords = [
            'sentry', 'testsentry', 'docsentry', 'project', 'build', 'create',
            'implement', 'develop', 'design', 'architecture', 'system'
        ]
        
        self.problem_keywords = [
            'problem', 'issue', 'challenge', 'difficulty', 'trouble', 'error',
            'bug', 'obstacle', 'stuck', 'confused', 'unsure', 'help'
        ]
        
        self.solution_keywords = [
            'solution', 'answer', 'fix', 'resolve', 'solve', 'approach',
            'method', 'technique', 'strategy', 'recommend', 'suggest'
        ]
    
    def extract_topics_advanced(self, text: str) -> Dict[str, Any]:
        """Extract topics using advanced algorithms with improved coverage."""
        text_lower = text.lower()
        
        # 1. Domain-based topic extraction
        domain_topics = self._extract_domain_topics(text_lower)
        
        # 2. N-gram based topic extraction
        ngram_topics = self._extract_ngram_topics(text)
        
        # 3. Context-based topic extraction
        context_topics = self._extract_context_topics(text)
        
        # 4. Project-specific topic extraction
        project_topics = self._extract_project_topics(text_lower)
        
        # 5. Problem-solution topic extraction
        problem_solution_topics = self._extract_problem_solution_topics(text)
        
        # 6. Enhanced semantic topic extraction
        semantic_topics = self._extract_semantic_topics(text)
        
        # 7. Key phrase extraction
        key_phrases = self._extract_key_phrases(text)
        
        # 8. Technical concept extraction
        technical_concepts = self.extract_technical_concepts(text)
        
        # Combine and rank topics with improved weighting
        all_topics = self._combine_and_rank_topics_enhanced(
            domain_topics, ngram_topics, context_topics, 
            project_topics, problem_solution_topics, semantic_topics, key_phrases, technical_concepts
        )
        
        return {
            'primary_topics': all_topics[:8],  # Increased from 5 to 8
            'domain_breakdown': domain_topics,
            'ngram_topics': ngram_topics,
            'context_topics': context_topics,
            'project_topics': project_topics,
            'problem_solution_topics': problem_solution_topics,
            'semantic_topics': semantic_topics,
            'key_phrases': key_phrases,
            'technical_concepts': technical_concepts,
            'all_topics': all_topics
        }
    
    def _extract_domain_topics(self, text_lower: str) -> Dict[str, List[str]]:
        """Extract topics by technical domain."""
        domain_topics = {}
        
        for domain, keywords in self.technical_domains.items():
            found_keywords = []
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
            if found_keywords:
                domain_topics[domain] = found_keywords
        
        return domain_topics
    
    def _extract_ngram_topics(self, text: str) -> List[str]:
        """Extract topics using n-gram analysis."""
        # Extract 2-grams and 3-grams
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 2-grams
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        
        # 3-grams
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
        
        # Count frequency
        all_ngrams = bigrams + trigrams
        ngram_counts = Counter(all_ngrams)
        
        # Filter for meaningful n-grams (length > 5, frequency > 1)
        meaningful_ngrams = [
            ngram for ngram, count in ngram_counts.most_common(20)
            if len(ngram) > 5 and count > 1
        ]
        
        return meaningful_ngrams[:10]
    
    def _extract_context_topics(self, text: str) -> List[str]:
        """Extract topics based on context and patterns."""
        topics = []
        
        # Look for topic indicators in sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
                
            # Look for topic introduction patterns
            topic_patterns = [
                r'(?:discussing|talking about|focusing on|working on|exploring)\s+([^.!?]+)',
                r'(?:topic|subject|issue|problem|challenge)\s+(?:is|of|about|with)\s+([^.!?]+)',
                r'(?:let\'s|we\'ll|i\'m)\s+(?:discuss|talk about|focus on|explore|work on)\s+([^.!?]+)',
                r'(?:the main|key|important)\s+(?:topic|subject|issue|point)\s+(?:is|was)\s+([^.!?]+)',
                r'(?:we\'re|i\'m)\s+(?:working on|building|creating|developing)\s+([^.!?]+)'
            ]
            
            for pattern in topic_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    topic = match.strip()
                    if len(topic) > 5 and len(topic) < 100:
                        topics.append(topic)
        
        return list(set(topics))[:10]
    
    def _extract_project_topics(self, text_lower: str) -> List[str]:
        """Extract project-specific topics."""
        project_topics = []
        
        # Look for project-related patterns
        project_patterns = [
            r'project\s+(?:called|named|titled)\s+([^.!?]+)',
            r'building\s+(?:a|an|the)\s+([^.!?]+)',
            r'creating\s+(?:a|an|the)\s+([^.!?]+)',
            r'developing\s+(?:a|an|the)\s+([^.!?]+)',
            r'working on\s+(?:a|an|the)\s+([^.!?]+)'
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                topic = match.strip()
                if len(topic) > 5 and len(topic) < 100:
                    project_topics.append(topic)
        
        # Also check for specific project keywords
        for keyword in self.project_keywords:
            if keyword in text_lower:
                project_topics.append(keyword)
        
        return list(set(project_topics))[:8]
    
    def _extract_problem_solution_topics(self, text: str) -> List[str]:
        """Extract topics related to problems and solutions."""
        topics = []
        
        # Look for problem-solution patterns
        problem_solution_patterns = [
            r'(?:problem|issue|challenge|difficulty)\s+(?:is|was|with)\s+([^.!?]+)',
            r'(?:solution|answer|fix|approach)\s+(?:is|was|for)\s+([^.!?]+)',
            r'(?:trying to|working to|attempting to)\s+([^.!?]+)',
            r'(?:need to|want to|looking for)\s+([^.!?]+)',
            r'(?:help with|assistance with|support for)\s+([^.!?]+)'
        ]
        
        for pattern in problem_solution_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                topic = match.strip()
                if len(topic) > 5 and len(topic) < 100:
                    topics.append(topic)
        
        return list(set(topics))[:8]
    
    def _extract_semantic_topics(self, text: str) -> List[str]:
        """Extract topics using semantic analysis and word relationships."""
        topics = []
        
        # Extract topics based on semantic patterns
        semantic_patterns = [
            r'(?:the main|key|important|primary|central)\s+(?:topic|subject|issue|point|focus|theme)\s+(?:is|was|of|about)\s+([^.!?]+)',
            r'(?:we\'re|i\'m|we are|i am)\s+(?:discussing|talking about|focusing on|working on|exploring)\s+([^.!?]+)',
            r'(?:let\'s|we\'ll|i\'ll)\s+(?:discuss|talk about|focus on|explore|work on|cover)\s+([^.!?]+)',
            r'(?:this is about|this focuses on|this deals with|this covers)\s+([^.!?]+)',
            r'(?:the goal|objective|purpose|aim)\s+(?:is|was|of)\s+([^.!?]+)',
            r'(?:we need to|i need to|we want to|i want to)\s+([^.!?]+)',
            r'(?:the challenge|problem|issue|difficulty)\s+(?:is|was|with)\s+([^.!?]+)',
            r'(?:the solution|answer|approach|method)\s+(?:is|was|for)\s+([^.!?]+)'
        ]
        
        for pattern in semantic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                topic = match.strip()
                if len(topic) > 5 and len(topic) < 150:
                    topics.append(topic)
        
        return list(set(topics))[:10]
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases using frequency and importance analysis."""
        # Extract meaningful phrases (2-4 words)
        words = re.findall(r'\b\w+\b', text.lower())
        phrases = []
        
        # 2-word phrases
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 5 and not any(word in phrase for word in ['the', 'and', 'or', 'but', 'for', 'with', 'from']):
                phrases.append(phrase)
        
        # 3-word phrases
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(phrase) > 8 and not any(word in phrase for word in ['the', 'and', 'or', 'but', 'for', 'with', 'from']):
                phrases.append(phrase)
        
        # 4-word phrases
        for i in range(len(words) - 3):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]} {words[i+3]}"
            if len(phrase) > 12 and not any(word in phrase for word in ['the', 'and', 'or', 'but', 'for', 'with', 'from']):
                phrases.append(phrase)
        
        # Count frequency and rank
        from collections import Counter
        phrase_counts = Counter(phrases)
        
        # Return most frequent meaningful phrases
        return [phrase for phrase, count in phrase_counts.most_common(15) if count > 1]
    
    def _combine_and_rank_topics_enhanced(self, *topic_lists) -> List[str]:
        """Combine and rank all extracted topics with enhanced weighting."""
        all_topics = []
        
        # Collect all topics with weights
        for i, topic_list in enumerate(topic_lists):
            if isinstance(topic_list, dict):
                # Handle domain topics
                for domain, topics in topic_list.items():
                    for topic in topics:
                        # Weight domain topics higher
                        all_topics.extend([topic] * 3)
            elif isinstance(topic_list, list):
                # Weight different types differently
                if i == 0:  # domain_topics
                    for topic in topic_list:
                        all_topics.extend([topic] * 3)
                elif i == 1:  # ngram_topics
                    for topic in topic_list:
                        all_topics.extend([topic] * 2)
                elif i == 2:  # context_topics
                    for topic in topic_list:
                        all_topics.extend([topic] * 4)  # Higher weight
                elif i == 3:  # project_topics
                    for topic in topic_list:
                        all_topics.extend([topic] * 5)  # Highest weight
                elif i == 4:  # problem_solution_topics
                    for topic in topic_list:
                        all_topics.extend([topic] * 4)  # High weight
                elif i == 5:  # semantic_topics
                    for topic in topic_list:
                        all_topics.extend([topic] * 3)
                elif i == 6:  # key_phrases
                    for topic in topic_list:
                        all_topics.extend([topic] * 2)
                elif i == 7:  # technical_concepts
                    for topic in topic_list:
                        all_topics.extend([topic] * 3)
                else:
                    all_topics.extend(topic_list)
        
        # Count frequency and rank
        topic_counts = Counter(all_topics)
        
        # Sort by frequency, then by length (longer topics first), then by position
        ranked_topics = sorted(
            topic_counts.items(),
            key=lambda x: (x[1], len(x[0]), -all_topics.index(x[0])),
            reverse=True
        )
        
        # Return unique topics in order of importance
        seen = set()
        result = []
        for topic, count in ranked_topics:
            if topic not in seen and len(topic) > 3:
                seen.add(topic)
                result.append(topic)
        
        return result[:20]  # Increased from 15 to 20
    
    def extract_conversation_themes(self, conversation_text: str) -> List[str]:
        """Extract high-level themes from the entire conversation."""
        themes = []
        
        # Look for theme indicators
        theme_patterns = [
            r'(?:the main|key|important|primary)\s+(?:theme|focus|goal|objective)\s+(?:is|was)\s+([^.!?]+)',
            r'(?:we\'re|i\'m)\s+(?:focused on|working towards|aiming for)\s+([^.!?]+)',
            r'(?:the goal|objective|purpose)\s+(?:is|was)\s+([^.!?]+)',
            r'(?:this is about|this focuses on|this deals with)\s+([^.!?]+)'
        ]
        
        for pattern in theme_patterns:
            matches = re.findall(pattern, conversation_text, re.IGNORECASE)
            for match in matches:
                theme = match.strip()
                if len(theme) > 10 and len(theme) < 200:
                    themes.append(theme)
        
        return themes[:5]
    
    def extract_technical_concepts(self, text: str) -> List[str]:
        """Extract specific technical concepts and terms."""
        concepts = []
        
        # Look for technical concept patterns
        concept_patterns = [
            r'(?:concept|idea|approach|method|technique|strategy)\s+(?:of|called|named)\s+([^.!?]+)',
            r'(?:using|implementing|applying)\s+([^.!?]+?)\s+(?:for|to|in)',
            r'(?:based on|built on|using)\s+([^.!?]+?)\s+(?:framework|library|tool|technology)',
            r'(?:the|this)\s+([^.!?]+?)\s+(?:framework|library|tool|technology|approach)'
        ]
        
        for pattern in concept_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                concept = match.strip()
                if len(concept) > 5 and len(concept) < 100:
                    concepts.append(concept)
        
        return list(set(concepts))[:10]


def extract_topics_advanced(text: str) -> Dict[str, Any]:
    """Public interface for advanced topic extraction."""
    extractor = AdvancedTopicExtractor()
    return extractor.extract_topics_advanced(text)


def extract_conversation_themes(conversation_text: str) -> List[str]:
    """Public interface for theme extraction."""
    extractor = AdvancedTopicExtractor()
    return extractor.extract_conversation_themes(conversation_text)
