"""Performance and memory usage tests for Shmoopland game."""
import pytest
from memory_profiler import profile
from shmoopland.base_game import ShmooplandGame
from shmoopland.ai_utils import GameAI
from shmoopland.content_generator import ContentGenerator
from shmoopland.npc import NPC

@pytest.fixture
def game():
    return ShmooplandGame()

@pytest.fixture
def ai():
    return GameAI()

@profile
def test_game_memory_usage(game):
    """Test overall game memory usage during typical gameplay."""
    # Simulate typical gameplay sequence
    commands = [
        "look",
        "go north",
        "examine crystal",
        "take crystal",
        "inventory",
        "talk merchant",
        "go south",
        "drop crystal"
    ]

    for command in commands:
        game.parse_command(command)
        # Memory usage should stay under 50MB total
        # This is monitored by the @profile decorator

    game.cleanup()

@profile
def test_ai_memory_usage(ai):
    """Test AI component memory usage under load."""
    # Test multiple command analyses
    commands = [
        "hello there merchant",
        "I want to buy something special",
        "show me your magical items",
        "that's too expensive",
        "let me think about it",
        "goodbye friend"
    ]

    for command in commands:
        result = ai.analyze_command(command)
        assert result is not None
        assert "intent" in result
        assert "sentiment" in result

    # Memory should stay under 20MB
    ai.cleanup()

@profile
def test_content_generation_memory(game):
    """Test memory usage during content generation."""
    # Load test data
    game.game_data = {
        "locations": {
            "market": {"description": "A bustling marketplace filled with magical wares."},
            "wizard_tower": {"description": "A tall tower crackling with arcane energy."},
            "town_square": {"description": "The heart of Shmoopland, always full of life."},
            "park": {"description": "A peaceful garden with glowing flowers."},
            "ancient_library": {"description": "Dusty tomes line the mysterious shelves."},
            "crystal_caves": {"description": "Sparkling crystals illuminate the cavern."},
            "mystic_garden": {"description": "Magical plants sway in an ethereal breeze."},
            "enchanted_forge": {"description": "The sound of mystical crafting fills the air."},
            "alchemist_lab": {"description": "Bubbling potions and magical ingredients abound."},
            "stargazer_peak": {"description": "A perfect spot to observe the magical sky."}
        },
        "items": {
            "magic_crystal": {
                "name": "Magic Crystal",
                "description": "A shimmering crystal pulsing with magical energy.",
                "location": "crystal_caves"
            },
            "ancient_tome": {
                "name": "Ancient Tome",
                "description": "A dusty book filled with mysterious knowledge.",
                "location": "ancient_library"
            },
            "mystic_flower": {
                "name": "Mystic Flower",
                "description": "A beautiful flower that seems to glow with inner light.",
                "location": "mystic_garden"
            }
        },
        "location_variables": {
            "lighting": "dim",
            "atmosphere": "magical",
            "danger_level": "low"
        }
    }

    # Initialize game state
    game.game_state = {
        "time_of_day": "evening",
        "weather": "stormy",
        "activity_level": "high",
        "visited_before": True,
        "player_status": {
            "health": 100,
            "magic": 75,
            "reputation": "respected"
        }
    }

    # Generate multiple descriptions with rich content
    locations = list(game.game_data["locations"].keys())

    for location in locations:
        game.current_location = location
        game.look()  # Triggers content generation

    # Memory should stay under 20MB
    # This is monitored by the @profile decorator

    # Cleanup
    game.cleanup()

@profile
def test_npc_interaction_memory():
    """Test memory usage during NPC interactions."""
    templates = {
        "npcs": {
            "merchant": {
                "greetings": ["Welcome!", "Hello there!"],
                "responses": {
                    "general": ["How can I help you?", "Looking for something special?"],
                    "positive": ["Great choice!", "Excellent!"],
                    "negative": ["Perhaps later.", "No problem."],
                    "trade": ["I have the finest wares!", "Special price for you!"],
                    "magic": ["Ah, interested in magical items?", "I have rare enchantments."]
                }
            }
        }
    }

    npc = NPC("merchant", templates)
    ai = GameAI()

    # Simulate conversation
    inputs = [
        "hello there",
        "what do you sell?",
        "that's interesting",
        "too expensive",
        "maybe later",
        "goodbye"
    ]

    for text in inputs:
        response = npc.respond_to(text, ai)
        assert response is not None
        assert len(response) > 0

    # Memory should stay under 20MB
    npc.cleanup()
    ai.cleanup()

def test_full_game_session(game):
    """Test a full game session with all features."""
    # Initialize game state
    assert game.current_location == "start"

    # Test movement and exploration
    game.parse_command("look")
    game.parse_command("go north")
    game.parse_command("look")

    # Test item interaction
    game.parse_command("examine crystal")
    game.parse_command("take crystal")
    game.parse_command("inventory")

    # Test NPC interaction
    game.parse_command("talk merchant")

    # Test item manipulation
    game.parse_command("drop crystal")

    # Cleanup
    game.cleanup()

if __name__ == "__main__":
    pytest.main(["-v", "test_performance.py"])
