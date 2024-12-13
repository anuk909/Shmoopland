"""Web interface for Shmoopland game."""
from typing import Dict, Any
from memory_profiler import profile
from .base_game import ShmooplandGame

class WebInterface:
    """Web interface wrapper for Shmoopland game."""

    def __init__(self, game: ShmooplandGame = None):
        """Initialize web interface with optional game instance."""
        self.game = game or ShmooplandGame()
        self._last_response = None

    @profile
    def process_command(self, command: str) -> Dict[str, Any]:
        """Process game command and return formatted response."""
        try:
            result = self.game.parse_command(command)
            self._last_response = {
                "message": result,
                "status": "success",
                "location": self.game.current_location,
                "inventory": self.game.inventory
            }
        except Exception as e:
            self._last_response = {
                "message": str(e),
                "status": "error",
                "location": self.game.current_location,
                "inventory": self.game.inventory
            }
        return self._last_response

    def cleanup(self):
        """Clean up resources."""
        if self.game:
            self.game.cleanup()
