"""NPC implementation with memory-efficient AI behavior."""
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from memory_profiler import profile
from .ai_utils import GameAI
from .utils import monitor_memory

@dataclass
class NPCMood:
    happiness: float = 0.5  # Range 0-1
    trust: float = 0.5     # Range 0-1
    energy: float = 0.5    # Range 0-1

    def update(self, player_interaction: Dict) -> None:
        sentiment = player_interaction.get("sentiment", 0)
        self.happiness = max(0, min(1, self.happiness + sentiment * 0.1))
        self.trust = max(0, min(1, self.trust + sentiment * 0.05))
        self.energy = max(0, min(1, self.energy - 0.1))  # Interactions cost energy

@monitor_memory(threshold_mb=5.0)
class NPC:
    """Represents an NPC with AI-powered behavior and personality."""

    def __init__(self, npc_type: str, templates: Dict):
        """Initialize NPC with type and response templates."""
        self.type = npc_type
        self.templates = templates["npcs"][npc_type]  # Fix template access
        self.mood = NPCMood()
        self.memory: List[Dict] = []
        self.MAX_MEMORY = 3  # Reduced for lower RAM usage
        self.personality = self.templates.get("personality_traits", {
            "openness": random.random(),
            "friendliness": random.random()
        })
        self.topics: Dict[str, int] = {}

    @monitor_memory(threshold_mb=2.0)
    def respond_to(self, player_input: str, ai: GameAI) -> Tuple[str, Dict]:
        """Generate response to player input using AI analysis."""
        analysis = ai.analyze_command(player_input)

        self.mood.update(analysis)
        self.memory.append({
            "input": player_input,
            "analysis": analysis,
            "timestamp": "current_time"  # Placeholder for actual timestamp
        })
        if len(self.memory) > self.MAX_MEMORY:
            self.memory.pop(0)

        topic = analysis.get("topic", "general")
        self.topics[topic] = self.topics.get(topic, 0) + 1

        response_type = self._determine_response_type(analysis)
        response_pool = self._get_response_pool(response_type, topic)

        response = random.choice(response_pool)  # Simplified selection for memory efficiency

        return response, {
            "mood": self.mood,
            "trust": self.mood.trust,
            "topics": self.topics
        }

    def _determine_response_type(self, analysis: Dict) -> str:
        """Determine appropriate response type based on AI analysis."""
        sentiment = analysis.get("sentiment", 0)
        intent = analysis.get("intent", "other")

        if intent == "greeting":
            return "greeting"
        elif intent == "question":
            return "informative"
        elif sentiment > 0.3:
            return "positive"
        elif sentiment < -0.3:
            return "negative"
        return "neutral"

    def _get_response_pool(self, response_type: str, topic: str) -> List[str]:
        """Get pool of possible responses based on type and topic."""
        responses = []

        # Check topic-specific responses
        if topic in self.templates.get("topics", {}):
            responses.extend(self.templates["topics"][topic])

        # Add response type specific responses
        if response_type in self.templates["responses"]:
            responses.extend(self.templates["responses"][response_type])

        # Fallback to neutral responses if no others found
        if not responses and "neutral" in self.templates["responses"]:
            responses.extend(self.templates["responses"]["neutral"])

        # Final fallback
        if not responses:
            return ["I'm not sure how to respond to that."]

        return responses

    def get_greeting(self) -> str:
        """Get appropriate greeting based on NPC's mood."""
        if self.mood.happiness > 0.7:
            mood_type = "happy"
        elif self.mood.happiness < 0.3:
            mood_type = "tired"
        else:
            mood_type = "neutral"

        greetings = self.templates.get("greetings", {
            "happy": ["Welcome!", "Hello there!"],
            "neutral": ["Hello.", "Greetings."],
            "tired": ["*yawn* Yes?", "Oh, hello."]
        }).get(mood_type, ["Hello."])
        return random.choice(greetings)

    def cleanup(self) -> None:
        self.memory.clear()
        self.topics.clear()
