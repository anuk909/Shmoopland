"""Web interface for Shmoopland game."""
import logging
from typing import Dict, Any, Optional
from memory_profiler import profile
from .base_game import ShmooplandGame
from .ai_utils import GameAI
from .utils import monitor_memory

logger = logging.getLogger(__name__)

@monitor_memory(threshold_mb=100.0)
class WebInterface:
    """Web interface wrapper for Shmoopland game."""

    def __init__(self):
        """Initialize web interface with game instance."""
        try:
            self.game = ShmooplandGame()
            self._last_response = None
        except Exception as e:
            logger.error(f"Failed to initialize game: {e}")
            raise

    @profile
    def process_command(self, command: str) -> Dict[str, Any]:
        """Process game command and return formatted response."""
        try:
            if command.lower() in ['quit', 'exit']:
                self.cleanup()
                return {
                    "message": "Thanks for playing Shmoopland!",
                    "status": "success",
                    "gameOver": True
                }

            result = self.game.parse_command(command)
            self._last_response = {
                "message": result,
                "status": "success",
                "location": self.game.current_location,
                "inventory": self.game.inventory,
                "gameOver": False
            }
            return self._last_response
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self._last_response = {
                "message": str(e),
                "status": "error",
                "gameOver": False
            }
            return self._last_response

    def get_state(self) -> Dict[str, Any]:
        """Get current game state."""
        try:
            return {
                "location": self.game.current_location,
                "inventory": self.game.inventory,
                "message": self.game.look(),
                "gameOver": False
            }
        except Exception as e:
            logger.error(f"Error getting game state: {e}")
            return {
                "message": str(e),
                "status": "error",
                "gameOver": False
            }

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'game'):
            self.game.cleanup()
