"""Tests for NPC behavior and memory usage."""
import pytest
from memory_profiler import profile
from shmoopland.npc import NPC
from shmoopland.ai_utils import GameAI

@pytest.fixture
def npc_templates():
    return {
        "merchant": {
            "greetings": [
                "Welcome to my shop!",
                "Looking for something special?"
            ],
            "responses": {
                "positive": [
                    "Excellent choice!",
                    "A wise decision!"
                ],
                "negative": [
                    "Perhaps something else?",
                    "Take your time browsing."
                ]
            }
        }
    }

@pytest.fixture
def merchant(npc_templates):
    return NPC("merchant", npc_templates)

@pytest.fixture
def ai():
    return GameAI()

@profile
def test_memory_usage(merchant, ai):
    """Test NPC memory usage stays within limits."""
    # Generate multiple interactions
    inputs = [
        "hello there",
        "show me your wares",
        "that's too expensive",
        "this looks nice",
        "goodbye",
        "one more thing"  # Should trigger memory cleanup
    ]

    for text in inputs:
        response = merchant.respond_to(text, ai)
        assert response is not None
        assert len(response) > 0

    # Check memory limit
    assert len(merchant.memory) <= merchant.MAX_MEMORY

    # Cleanup
    merchant.cleanup()
    assert len(merchant.memory) == 0

def test_response_generation(merchant, ai):
    """Test NPC response generation."""
    # Test greeting
    response = merchant.respond_to("hello", ai)
    assert response in merchant.templates["merchant"]["greetings"]

    # Test positive response
    response = merchant.respond_to("this is wonderful", ai)
    assert response in merchant.templates["merchant"]["responses"]["positive"]

    # Test negative response
    response = merchant.respond_to("this is terrible", ai)
    assert response in merchant.templates["merchant"]["responses"]["negative"]

def test_greeting(merchant):
    """Test NPC greeting generation."""
    greeting = merchant.get_greeting()
    assert greeting in merchant.templates["merchant"]["greetings"]
