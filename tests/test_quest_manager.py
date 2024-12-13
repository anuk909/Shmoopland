"""Tests for the quest management system."""
import pytest
from shmoopland.quest_manager import QuestManager, Quest, QuestObjective, QuestRewards

def test_quest_initialization():
    """Test quest manager initialization."""
    manager = QuestManager()
    assert len(manager.active_quests) == 0
    assert len(manager.completed_quests) == 0

def test_start_quest():
    """Test starting a new quest."""
    manager = QuestManager()
    quest = manager.start_quest("welcome_to_shmoopland")
    assert quest is not None
    assert quest.title == "Welcome to Shmoopland"
    assert len(quest.objectives) > 0

def test_quest_progress():
    """Test updating quest progress."""
    manager = QuestManager()
    manager.start_quest("welcome_to_shmoopland")
    completed = manager.update_quest_progress("visit_location", "town_square")
    assert len(completed) == 1
    assert "welcome_to_shmoopland" in completed

def test_quest_completion():
    """Test quest completion and rewards."""
    manager = QuestManager()
    manager.start_quest("welcome_to_shmoopland")
    manager.update_quest_progress("visit_location", "town_square")
    rewards = manager.complete_quest("welcome_to_shmoopland")
    assert rewards is not None
    assert "magic_coin" in rewards.items
    assert rewards.experience == 10

def test_quest_prerequisites():
    """Test quest prerequisite system."""
    manager = QuestManager()
    available = manager.get_available_quests({})
    assert "welcome_to_shmoopland" in available
    assert "wizard_apprentice" not in available

    manager.start_quest("welcome_to_shmoopland")
    manager.update_quest_progress("visit_location", "town_square")
    manager.complete_quest("welcome_to_shmoopland")

    available = manager.get_available_quests({})
    assert "market_magic" in available
