"""Tests for utility functions and decorators."""
import pytest
from memory_profiler import profile
from shmoopland.utils import monitor_memory, cleanup_resources

class DummyGame:
    """Dummy game class for testing decorators."""

    def __init__(self):
        self.cleaned_up = False
        self.data = []

    @monitor_memory(threshold_mb=50.0)
    def process_data(self, size: int = 1000) -> list:
        """Test function that allocates memory."""
        self.data = [i for i in range(size)]
        return self.data

    def cleanup(self):
        """Cleanup resources."""
        self.cleaned_up = True
        self.data = []

@pytest.fixture
def game():
    return DummyGame()

@profile
def test_memory_monitoring(game):
    """Test memory usage monitoring."""
    # Process small amount of data (should be under threshold)
    result = game.process_data(1000)
    assert len(result) == 1000

    # Process larger amount of data (still under threshold)
    result = game.process_data(10000)
    assert len(result) == 10000

def test_cleanup_decorator(game):
    """Test cleanup decorator."""
    @cleanup_resources
    def test_func(game_instance):
        return game_instance.process_data(1000)

    result = test_func(game)
    assert len(result) == 1000
    assert game.cleaned_up
    assert len(game.data) == 0
