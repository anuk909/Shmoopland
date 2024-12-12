"""NPC implementation with memory-efficient AI behavior."""
import random
from typing import Dict, List, Optional
from memory_profiler import profile
from .ai_utils import GameAI
from .utils import monitor_memory

@monitor_memory(threshold_mb=50.0)
class NPC:
    """Represents an NPC with basic AI-powered behavior."""

    def __init__(self, npc_type: str, templates: Dict):
        """Initialize NPC with type and response templates.

        Args:
            npc_type: Type of NPC (merchant, wizard, etc.)
            templates: Dictionary of response templates
        """
        self.type = npc_type
        self.templates = templates
        self.memory: List[Dict] = []  # Limited conversation history
        self.MAX_MEMORY = 5  # Keep memory usage low

    @monitor_memory(threshold_mb=20.0)
    def respond_to(self, player_input: str, ai: GameAI) -> str:
        """Generate AI-enhanced response to player input.

        Args:
            player_input: Player's input text
            ai: GameAI instance for analysis

        Returns:
            NPC's response string
        """
        # Analyze input with AI
        analysis = ai.analyze_command(player_input)

        # Update memory with limited size
        self.memory.append({
            "input": player_input,
            "analysis": analysis
        })
        if len(self.memory) > self.MAX_MEMORY:
            self.memory.pop(0)  # Remove oldest memory

        # Select response based on analysis
        sentiment = analysis.get("sentiment", 0)
        intent = analysis.get("intent", "other")

        # Choose response type
        if intent == "greeting":
            return random.choice(self.templates[self.type]["greetings"])

        response_type = "positive" if sentiment > 0 else "negative"
        responses = self.templates[self.type]["responses"][response_type]

        return random.choice(responses)

    def get_greeting(self) -> str:
        """Get a random greeting from NPC's templates."""
        return random.choice(self.templates[self.type]["greetings"])

    def cleanup(self) -> None:
        """Clear NPC's memory to free resources."""
        self.memory.clear()
