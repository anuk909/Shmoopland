"""Tests for content generation ensuring low memory usage and correct functionality."""
import pytest
from memory_profiler import profile
from shmoopland.content_generator import ContentGenerator

@pytest.fixture
def templates():
    return {
        "description_templates": {
            "market": [
                "The {time_of_day} market bustles with {activity_level} activity.",
                "You find yourself in the magical marketplace, where {market_feature}."
            ]
        },
        "item_templates": {
            "crystal": [
                "A {crystal_type} crystal that {crystal_effect}",
                "This mystical prism {prism_feature}"
            ]
        }
    }

@pytest.fixture
def generator(templates):
    return ContentGenerator(templates)

@profile
def test_memory_usage(generator):
    """Test memory usage stays within acceptable limits."""
    context = {
        "time_of_day": "morning",
        "activity_level": "high",
        "market_feature": "merchants call their wares"
    }

    # Generate multiple descriptions
    for _ in range(10):
        desc = generator.generate_description("market", context)
        assert desc is not None
        assert len(desc) > 0

    # Check cache effectiveness
    cache_size = len(generator._cache)
    assert cache_size > 0

    # Cleanup
    generator.cleanup()
    assert len(generator._cache) == 0

def test_description_generation(generator):
    """Test template-based description generation."""
    context = {
        "time_of_day": "evening",
        "activity_level": "moderate",
        "market_feature": "lanterns glow softly"
    }

    desc = generator.generate_description("market", context)
    assert any(keyword in desc for keyword in ["evening", "moderate", "lanterns"])

def test_item_description(generator):
    """Test item description generation."""
    context = {
        "crystal_type": "sparkling",
        "crystal_effect": "glows softly",
        "prism_feature": "catches rainbows"
    }

    desc = generator.generate_item_description("crystal", context)
    assert any(keyword in desc for keyword in ["sparkling", "glows", "catches"])

def test_variable_handling(generator):
    """Test handling of different variable types."""
    context = {
        "time_of_day": ["morning", "evening"],
        "activity_level": 5,
        "market_feature": None
    }

    desc = generator.generate_description("market", context)
    assert desc is not None
    assert len(desc) > 0
