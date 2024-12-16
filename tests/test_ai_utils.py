"""Tests for AI utilities ensuring low memory usage and correct functionality."""
import pytest
from memory_profiler import profile
from shmoopland.ai_utils import GameAI

@pytest.fixture
def game_ai():
    return GameAI()

def test_lazy_loading(game_ai):
    """Test that NLP model is only loaded when needed."""
    assert game_ai._nlp is None
    game_ai.analyze_command("look at the crystal")
    assert game_ai._nlp is not None

@profile
def test_memory_usage(game_ai):
    """Test memory usage stays within acceptable limits."""
    # Initial analysis
    result1 = game_ai.analyze_command("take the magic potion")
    assert "intent" in result1
    assert "entities" in result1
    assert "sentiment" in result1

    # Cached response
    result2 = game_ai.analyze_command("take the magic potion")
    assert result1 == result2  # Should use cached result

    # Cleanup
    game_ai.cleanup()
    assert game_ai._nlp is None
    assert len(game_ai._response_cache) == 0

def test_intent_detection(game_ai):
    """Test basic intent detection."""
    assert game_ai.analyze_command("go north")["intent"] == "movement"
    assert game_ai.analyze_command("take potion")["intent"] == "interaction"
    assert game_ai.analyze_command("hello")["intent"] == "other"

def test_description_generation(game_ai):
    """Test template-based description generation."""
    template = "The {time} sky shows {num} twinkling {object}."
    context = {"time": "night", "num": "thousand", "object": "stars"}
    result = game_ai.generate_description(template, context)
    assert result == "The night sky shows thousand twinkling stars."
