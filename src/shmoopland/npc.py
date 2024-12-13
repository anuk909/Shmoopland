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
        self.type = npc_type
        self.templates = templates
        self.mood = NPCMood()
        self.memory: List[Dict] = []
        self.MAX_MEMORY = 3  # Reduced for lower RAM usage
        self.personality = {
            "openness": random.random(),
            "friendliness": random.random()
        }
        self.topics: Dict[str, int] = {}  # Track discussion topics

    @monitor_memory(threshold_mb=2.0)
    def respond_to(self, player_input: str, ai: GameAI) -> Tuple[str, Dict]:
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

        weights = [
            1 + (self.personality["friendliness"] if "friendly" in r else 0) +
            (self.mood.happiness if "happy" in r else 0)
            for r in response_pool
        ]

        response = random.choices(response_pool, weights=weights, k=1)[0]

        return response, {
            "mood": self.mood,
            "trust": self.mood.trust,
            "topics": self.topics
        }

    def _determine_response_type(self, analysis: Dict) -> str:
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
        responses = []

        if topic in self.templates[self.type].get("topics", {}):
            responses.extend(self.templates[self.type]["topics"][topic])

        if response_type in self.templates[self.type]["responses"]:
            responses.extend(self.templates[self.type]["responses"][response_type])

        if not responses:
            responses = self.templates[self.type]["responses"]["neutral"]

        return responses

    def get_greeting(self) -> str:
        greetings = self.templates[self.type]["greetings"]
        if self.mood.happiness > 0.7:
            return random.choice(greetings["happy"])
        elif self.mood.happiness < 0.3:
            return random.choice(greetings["tired"])
        return random.choice(greetings["neutral"])

    def cleanup(self) -> None:
        self.memory.clear()
        self.topics.clear()
