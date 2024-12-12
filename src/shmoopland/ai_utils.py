"""AI utilities for Shmoopland game with focus on low memory usage.

This module provides AI-enhanced features while maintaining minimal RAM footprint
through lazy loading and efficient model usage.
"""
import spacy
from textblob import TextBlob
import markovify
from typing import Dict, List, Optional
from memory_profiler import profile
from .utils import monitor_memory, cleanup_resources

@monitor_memory(threshold_mb=50.0)
class GameAI:
    """Handles AI-enhanced features for the game with memory-efficient implementation."""

    def __init__(self):
        self._nlp = None  # Lazy loading
        self._dialogue_model = None
        self._response_cache = {}  # Cache common responses

    @monitor_memory(threshold_mb=10.0)
    def load_nlp(self) -> None:
        """Lazy load the spaCy model only when needed."""
        if not self._nlp:
            self._nlp = spacy.load("en_core_web_sm")

    @monitor_memory(threshold_mb=20.0)
    def analyze_command(self, text: str) -> Dict:
        """Analyze user command with minimal memory usage.

        Args:
            text: The user's command text

        Returns:
            Dict containing intent, entities, and sentiment analysis
        """
        # Check cache first
        if text in self._response_cache:
            return self._response_cache[text]

        self.load_nlp()
        doc = self._nlp(text)

        result = {
            "intent": self._get_intent(doc),
            "entities": [(ent.text, ent.label_) for ent in doc.ents],
            "sentiment": TextBlob(text).sentiment.polarity
        }

        # Cache the result for future use
        self._response_cache[text] = result
        return result

    @monitor_memory(threshold_mb=10.0)
    def _get_intent(self, doc) -> str:
        """Extract basic intent from spaCy doc using rule-based approach."""
        # Simple rule-based intent detection
        verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
        if not verbs:
            return "unknown"

        # Common game command intents
        movement_verbs = {"go", "move", "walk", "run", "climb"}
        interaction_verbs = {"take", "drop", "examine", "look", "inspect"}

        main_verb = verbs[0]
        if main_verb in movement_verbs:
            return "movement"
        elif main_verb in interaction_verbs:
            return "interaction"
        return "other"

    @monitor_memory(threshold_mb=10.0)
    def generate_description(self, template: str, context: Dict) -> str:
        """Generate dynamic description using templates and context.

        Args:
            template: Base template string with placeholders
            context: Dictionary of context variables

        Returns:
            Generated description string
        """
        try:
            return template.format(**context)
        except KeyError:
            return template  # Fallback to original template if context missing

    def cleanup(self) -> None:
        """Free memory by clearing caches and releasing models."""
        self._response_cache.clear()
        self._nlp = None
        self._dialogue_model = None
