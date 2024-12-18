"""AI utilities for Shmoopland game with memory-efficient implementation."""

import gc
from typing import Dict, Optional, Any
import spacy
from textblob import TextBlob
from .utils import monitor_memory, cleanup_resources

@cleanup_resources
class GameAI:
    """Memory-efficient AI system for game interactions."""

    def __init__(self, nlp_model: Optional[str] = 'en_core_web_sm'):
        """Initialize with lazy loading of models.

        Args:
            nlp_model: Name of spaCy model to use, defaults to 'en_core_web_sm'
        """
        self._nlp = None
        self._nlp_model = nlp_model
        self._response_cache = {}
        self._context = {}

    @property
    @monitor_memory(threshold_mb=20.0)
    def nlp(self):
        """Lazy load spaCy model."""
        if self._nlp is None and self._nlp_model:
            try:
                self._nlp = spacy.load(self._nlp_model)
            except OSError:
                self._nlp = None
        return self._nlp

    def cleanup(self):
        """Clean up resources."""
        self._nlp = None
        self._response_cache.clear()
        self._context.clear()
        gc.collect()

    @monitor_memory(threshold_mb=5.0)
    def analyze_command(self, command: str) -> Dict[str, Any]:
        """Analyze user command with memory-efficient NLP."""
        cache_key = f"cmd_{command}"
        if cache_key in self._response_cache:
            return self._response_cache[cache_key]

        # Fallback implementation when NLP is not available
        if self.nlp is None:
            words = command.lower().split()
            analysis = {
                'intent': 'unknown',
                'objects': words[1:] if len(words) > 1 else [],
                'action': words[0] if words else None,
                'sentiment': 0.0,
                'entities': [],
                'topic': 'general'
            }
            self._response_cache[cache_key] = analysis
            return analysis

        doc = self.nlp(command.lower())
        blob = TextBlob(command)  # For sentiment analysis

        analysis = {
            'intent': self._extract_intent(doc),
            'objects': [token.text for token in doc if token.dep_ in ('dobj', 'pobj')],
            'action': next((token.text for token in doc if token.pos_ == 'VERB'), None),
            'sentiment': blob.sentiment.polarity,
            'entities': [ent.text for ent in doc.ents],
            'topic': self._extract_topic(doc)
        }

        self._response_cache[cache_key] = analysis
        return analysis

    @monitor_memory(threshold_mb=10.0)
    def generate_description(self, base_text: str, context: Dict[str, Any]) -> str:
        """Generate enhanced description with context awareness."""
        cache_key = f"desc_{base_text}_{hash(frozenset(context.items()))}"
        if cache_key in self._response_cache:
            return self._response_cache[cache_key]

        # Fallback implementation when NLP is not available
        if self.nlp is None:
            enhanced = base_text
            if context.get('time_of_day') == 'night':
                enhanced = enhanced.replace('bright', 'dim').replace('sunny', 'moonlit')
            self._response_cache[cache_key] = enhanced
            return enhanced

        # Use TextBlob for simple sentiment analysis
        blob = TextBlob(base_text)
        sentiment = blob.sentiment.polarity

        # Adjust description based on context and sentiment
        enhanced = base_text
        if context.get('time_of_day') == 'night':
            enhanced = enhanced.replace('bright', 'dim').replace('sunny', 'moonlit')
        if sentiment > 0:
            enhanced = enhanced.replace('mysterious', 'intriguing').replace('strange', 'fascinating')
        elif sentiment < 0:
            enhanced = enhanced.replace('peaceful', 'eerie').replace('quiet', 'unsettling')

        self._response_cache[cache_key] = enhanced
        if len(self._response_cache) > 100:  # Prevent cache from growing too large
            self._response_cache.clear()

        return enhanced

    def _extract_intent(self, doc) -> str:
        """Extract user intent from spaCy doc."""
        verbs = [token.lemma_ for token in doc if token.pos_ == 'VERB']
        if not verbs:
            return 'unknown'

        intent_mapping = {
            'look': 'examine',
            'go': 'move',
            'take': 'acquire',
            'drop': 'discard',
            'talk': 'interact',
            'help': 'assist'
        }

        return intent_mapping.get(verbs[0], verbs[0])

    def _extract_topic(self, doc) -> str:
        """Extract main topic from command."""
        # Look for specific game-related topics
        topics = {
            'magic': ['magic', 'spell', 'enchant', 'potion'],
            'items': ['item', 'object', 'thing', 'artifact'],
            'trade': ['buy', 'sell', 'trade', 'price'],
            'quest': ['quest', 'mission', 'task', 'help'],
            'combat': ['fight', 'attack', 'defend', 'battle']
        }

        text = doc.text.lower()
        for topic, keywords in topics.items():
            if any(keyword in text for keyword in keywords):
                return topic

        return 'general'
