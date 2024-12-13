"""Test suite for the skills system."""
import pytest
from src.shmoopland.skills import SkillSystem, SkillLevel

def test_skill_level_initialization():
    """Test skill level initialization."""
    skill = SkillLevel()
    assert skill.level == 1
    assert skill.experience == 0
    assert skill.next_level_exp == 100

def test_skill_experience_gain():
    """Test adding experience to skills."""
    system = SkillSystem()
    leveled_up, message = system.add_experience("magic", 50)
    assert not leveled_up
    assert "Gained 50 experience in magic" in message
    assert system.get_skill_level("magic") == 1

def test_skill_level_up():
    """Test skill leveling up."""
    system = SkillSystem()
    leveled_up, message = system.add_experience("magic", 150)
    assert leveled_up
    assert "Level Up" in message
    assert system.get_skill_level("magic") == 2

def test_skill_check():
    """Test skill check mechanics."""
    system = SkillSystem()
    # Set a seed for consistent testing
    import random
    random.seed(42)

    # Level up magic skill
    system.add_experience("magic", 200)
    success, message = system.check_skill("magic", 1)
    assert success
    assert "Success" in message

def test_get_all_skills():
    """Test retrieving all skills."""
    system = SkillSystem()
    skills = system.get_all_skills()
    assert "magic" in skills
    assert "negotiation" in skills
    assert "exploration" in skills
    assert isinstance(skills["magic"]["level"], int)

def test_memory_cleanup():
    """Test memory cleanup."""
    system = SkillSystem()
    system.add_experience("magic", 100)
    system.cleanup()
    assert system.get_skill_level("magic") == 0
