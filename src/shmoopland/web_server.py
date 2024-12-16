"""Flask server implementation for Shmoopland web interface."""
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from .web_interface import WebInterface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
game_interface = WebInterface()

@app.route('/api/command', methods=['POST'])
def process_command():
    """Process game commands from web interface."""
    command = request.json.get('command')
    if not command:
        logger.warning("Received request with no command")
        return jsonify({
            "status": "error",
            "message": "No command provided",
            "location": game_interface.game.current_location,
            "inventory": game_interface.game.inventory
        }), 400

    logger.info(f"Processing command: {command}")
    response = game_interface.process_command(command)
    logger.info(f"Command response: {response}")
    return jsonify(response)

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current game state."""
    logger.info("Getting game state")
    current_location = game_interface.game.current_location
    inventory = game_interface.game.inventory
    look_result = game_interface.game.look()

    response = {
        "status": "success",
        "location": current_location,
        "inventory": inventory,
        "message": look_result if look_result else "You look around...",
        "location_description": game_interface.game.get_location_description()
    }
    logger.info(f"Current game state: {response}")
    return jsonify(response)

if __name__ == '__main__':
    logger.info("Starting Shmoopland web server on port 5000")
    app.run(port=5000)
