"""Skills system implementation with memory-efficient design."""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
from memory_profiler import profile
from .utils import monitor_memory, cleanup_resources

@dataclass
class SkillLevel:
    """Represents a skill level with minimal memory footprint."""
    level: int = 1
    experience: int = 0
    next_level_exp: int = 100

    def add_exp(self, amount: int) -> Tuple[bool, int]:
        """Add experience and return if leveled up and new level."""
        self.experience += amount
        if self.experience >= self.next_level_exp:
            self.level += 1
            self.experience -= self.next_level_exp
            self.next_level_exp = int(self.next_level_exp * 1.5)
            return True, self.level
        return False, self.level

@monitor_memory(threshold_mb=5.0)
class SkillSystem:
    """Manages character skills with memory optimization."""

    def __init__(self):
        """Initialize skill system with minimal memory footprint."""
        self.skills: Dict[str, SkillLevel] = defaultdict(SkillLevel)
        self._skill_descriptions = {
            "magic": "Ability to understand and use magical items",
            "negotiation": "Effectiveness in bartering and conversations",
            "exploration": "Skill at finding hidden paths and secrets",
            "crafting": "Ability to create and enhance magical items",
            "lore": "Knowledge of Shmoopland's history and mysteries"
        }

    @monitor_memory(threshold_mb=2.0)
    def add_experience(self, skill_name: str, amount: int) -> Tuple[bool, str]:
        """Add experience to a skill and return level up message if applicable."""
        if skill_name not in self._skill_descriptions:
            return False, f"Unknown skill: {skill_name}"

        leveled_up, new_level = self.skills[skill_name].add_exp(amount)
        if leveled_up:
            return True, f"Level Up! Your {skill_name} is now level {new_level}!"
        return False, f"Gained {amount} experience in {skill_name}."

    def get_skill_level(self, skill_name: str) -> int:
        """Get the current level of a skill."""
        return self.skills[skill_name].level if skill_name in self._skill_descriptions else 0

    def get_skill_description(self, skill_name: str) -> Optional[str]:
        """Get the description of a skill."""
        return self._skill_descriptions.get(skill_name)

    def get_all_skills(self) -> Dict[str, Dict]:
        """Get all skills and their current levels."""
        return {
            name: {
                "level": self.skills[name].level,
                "description": desc,
                "experience": self.skills[name].experience,
                "next_level": self.skills[name].next_level_exp
            }
            for name, desc in self._skill_descriptions.items()
        }

    @monitor_memory(threshold_mb=1.0)
    def check_skill(self, skill_name: str, difficulty: int) -> Tuple[bool, str]:
        """Check if a skill check passes and return result message."""
        if skill_name not in self._skill_descriptions:
            return False, f"Cannot perform check for unknown skill: {skill_name}"

        skill_level = self.get_skill_level(skill_name)
        success_chance = min(0.95, max(0.05, (skill_level / difficulty) * 0.8))

        import random
        success = random.random() < success_chance

        if success:
            self.add_experience(skill_name, max(1, difficulty - skill_level))
            return True, f"Success! Your {skill_name} skill served you well."
        return False, f"Failed. Perhaps with more practice in {skill_name}..."

    def cleanup(self) -> None:
        """Clear skill system resources."""
        self.skills.clear()
