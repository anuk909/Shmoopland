"""Flask server implementation for Shmoopland web interface."""
import logging
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from shmoopland.web_interface import WebInterface
from shmoopland.base_game import ShmooplandGame

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize game interface
try:
    game_interface = WebInterface()
except Exception as e:
    logger.error(f"Failed to initialize game interface: {e}")
    sys.exit(1)

@app.route('/api/command', methods=['POST'])
def process_command():
    """Process game commands from the web interface."""
    try:
        command = request.json.get('command', '')
        if command.lower() in ['quit', 'exit']:
            game_interface.cleanup()
            return jsonify({'message': 'Thanks for playing Shmoopland!', 'gameOver': True})

        result = game_interface.process_command(command)
        return jsonify({'message': result, 'gameOver': False})
    except Exception as e:
        logger.error(f"Error processing command: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current game state."""
    try:
        state = game_interface.get_state()
        return jsonify(state)
    except Exception as e:
        logger.error(f"Error getting game state: {e}")
        return jsonify({'error': str(e)}), 500

def main():
    """Run the Flask server."""
    try:
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
