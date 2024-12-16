"""Quest management system for Shmoopland with memory optimization."""
import json
from typing import Dict, Set, List, Optional
from dataclasses import dataclass, field
from .utils import monitor_memory, cleanup_resources

@dataclass
class QuestObjective:
    """Represents a single quest objective."""
    type: str
    target: str
    description: str
    completed: bool = False

@dataclass
class QuestRewards:
    """Represents rewards for completing a quest."""
    items: List[str] = field(default_factory=list)
    experience: int = 0

@dataclass
class Quest:
    """Represents a quest with memory-efficient storage."""
    title: str
    description: str
    objectives: List[QuestObjective]
    rewards: QuestRewards
    prerequisites: List[str] = field(default_factory=list)
    next_quest: Optional[str] = None
    completed: bool = False

@monitor_memory(threshold_mb=10.0)
@cleanup_resources
class QuestManager:
    """Manages quests with lazy loading and memory optimization."""

    def __init__(self):
        """Initialize quest manager with minimal memory footprint."""
        self.active_quests: Dict[str, Quest] = {}
        self.completed_quests: Set[str] = set()
        self._available_quests: Dict[str, Dict] = {}
        self._loaded = False

    def _load_quests(self) -> None:
        """Lazy load quest data."""
        if not self._loaded:
            try:
                with open("data/game/quests.json", 'r') as file:
                    data = json.load(file)
                    self._available_quests = data.get('quests', {})
                self._loaded = True
            except FileNotFoundError:
                print("Warning: Quest data file not found.")
                self._available_quests = {}

    def get_available_quests(self, game_state: Dict) -> List[str]:
        """Get quests available based on prerequisites."""
        self._load_quests()
        available = []

        for quest_id, quest_data in self._available_quests.items():
            if quest_id not in self.active_quests and quest_id not in self.completed_quests:
                prerequisites = quest_data.get('prerequisites', [])
                if all(pre in self.completed_quests for pre in prerequisites):
                    available.append(quest_id)

        return available

    def start_quest(self, quest_id: str) -> Optional[Quest]:
        """Start a new quest if available."""
        self._load_quests()

        if quest_id not in self._available_quests:
            return None

        quest_data = self._available_quests[quest_id]
        objectives = [
            QuestObjective(
                type=obj['type'],
                target=obj['target'],
                description=obj['description'],
                completed=False
            )
            for obj in quest_data['objectives']
        ]

        rewards = QuestRewards(
            items=quest_data['rewards'].get('items', []),
            experience=quest_data['rewards'].get('experience', 0)
        )

        quest = Quest(
            title=quest_data['title'],
            description=quest_data['description'],
            objectives=objectives,
            rewards=rewards,
            prerequisites=quest_data.get('prerequisites', []),
            next_quest=quest_data.get('next_quest')
        )

        self.active_quests[quest_id] = quest
        return quest

    def update_quest_progress(self, event_type: str, target: str) -> List[str]:
        """Update quest progress based on player actions."""
        completed_quests = []

        for quest_id, quest in self.active_quests.items():
            updated = False
            for objective in quest.objectives:
                if not objective.completed and objective.type == event_type and objective.target == target:
                    objective.completed = True
                    updated = True

            if updated and all(obj.completed for obj in quest.objectives):
                quest.completed = True
                completed_quests.append(quest_id)

        for quest_id in completed_quests:
            self.complete_quest(quest_id)

        return completed_quests

    def complete_quest(self, quest_id: str) -> Optional[QuestRewards]:
        """Complete a quest and return its rewards."""
        if quest_id not in self.active_quests:
            return None

        quest = self.active_quests[quest_id]
        if not quest.completed:
            return None

        rewards = quest.rewards
        self.completed_quests.add(quest_id)
        del self.active_quests[quest_id]

        return rewards

    def get_quest_status(self, quest_id: str) -> Optional[Quest]:
        """Get the current status of a quest."""
        return self.active_quests.get(quest_id)

    def cleanup(self) -> None:
        """Clean up resources."""
        self.active_quests.clear()
        self._available_quests.clear()
        self.completed_quests.clear()
        self._loaded = False
