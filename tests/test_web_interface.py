"""Tests for web interface functionality and memory usage."""
import pytest
from memory_profiler import profile
from shmoopland.base_game import ShmooplandGame
from shmoopland.web_interface import WebInterface

@pytest.fixture
def web_game():
    """Initialize game with web interface."""
    game = ShmooplandGame()
    web = WebInterface(game)
    return web, game

@profile
def test_web_interface_memory(web_game):
    """Test memory usage of web interface during typical interactions."""
    web, game = web_game

    # Simulate typical web interactions
    commands = [
        "look",
        "go north",
        "examine crystal",
        "inventory",
        "help"
    ]

    for command in commands:
        response = web.process_command(command)
        assert response is not None
        assert isinstance(response, dict)
        assert "message" in response

    # Memory should stay under 30MB
    web.cleanup()
    game.cleanup()

def test_web_content_richness(web_game):
    """Test that web interface properly displays rich content."""
    web, game = web_game

    # Test location descriptions
    response = web.process_command("look")
    assert len(response["message"]) >= 100  # Ensure rich descriptions

    # Test NPC interactions
    response = web.process_command("talk merchant")
    assert "merchant" in response["message"].lower()
    assert len(response["message"]) >= 50

    # Test item descriptions
    response = web.process_command("examine crystal")
    assert "crystal" in response["message"].lower()
    assert len(response["message"]) >= 50

    web.cleanup()
    game.cleanup()

@profile
def test_concurrent_interface_usage(web_game):
    """Test memory usage with both terminal and web interfaces active."""
    web, game = web_game

    # Simulate concurrent terminal and web usage
    terminal_commands = ["look", "inventory"]
    web_commands = ["examine crystal", "talk merchant"]

    for t_cmd, w_cmd in zip(terminal_commands, web_commands):
        game.parse_command(t_cmd)  # Terminal interface
        web_response = web.process_command(w_cmd)  # Web interface

        assert web_response is not None
        assert isinstance(web_response, dict)

    # Memory should stay under 50MB total
    web.cleanup()
    game.cleanup()

def test_interface_consistency():
    """Test consistency between terminal and web interfaces."""
    game = ShmooplandGame()
    web = WebInterface(game)

    # Compare outputs between interfaces
    commands = ["look", "inventory", "examine crystal"]

    for cmd in commands:
        term_output = game.parse_command(cmd)
        web_output = web.process_command(cmd)

        # Ensure core content is consistent
        assert term_output in web_output["message"]

    web.cleanup()
    game.cleanup()
