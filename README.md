# Shmoopland

A magical text-based adventure game where players explore the whimsical realm of Shmoopland.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/anuk909/Shmoopland.git
cd Shmoopland
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the game and dependencies:
```bash
# Install the game package and dependencies
pip install -e .

# Install required spaCy model for AI features
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; spacy.load('en_core_web_sm'); import shmoopland"
```

Note: If spaCy model installation fails, try:
```bash
pip install -U spacy
python -m spacy download en_core_web_sm
```

The game requires:
- Python 3.8 or higher
- Approximately 100MB RAM for AI features
- Internet connection for initial spaCy model download

## Running the Game

### Terminal Mode
To start the game in terminal mode:
```bash
python src/shmoopland/game.py
```

### Web Interface
To start the web server:
```bash
# Install required packages (if not already installed via pip install -e .)
pip install flask flask-cors

# Start the server
python src/shmoopland/web_server.py
```

The web interface will be available at http://localhost:5000

Features:
- Text-based adventure interface with command history
- Real-time game state updates
- Clickable command suggestions
- Mobile-friendly layout
- Same gameplay experience as terminal mode

Common Issues:
- If port 5000 is in use, try: `lsof -i :5000` to find and kill the process
- If Flask is not found, ensure you've run `pip install -e .`
- If the page doesn't load, check that the server is running without errors
- For connection issues, ensure you're using http://localhost:5000

You can use all the same commands as in terminal mode. The interface will display the game output and maintain a history of your actions.

## Commands

- `look`: Look around the current location
- `inventory`: Check what you're carrying
- `take [item]`: Pick up an item
- `drop [item]`: Drop an item
- `go [direction]`: Move in a direction (north, south, east, west)
- `quit`: Exit the game
- `help`: Show available commands

## Development

The game is structured with:
- `base_game.py`: Core game mechanics and classes
- `game.py`: Main game entry point and terminal interface
- `web_server.py`: Web interface server
- Individual JSON files in `data/game/` for game content:
  - `locations.json`: Game world locations
  - `items.json`: Items and their properties
  - `npcs.json`: Non-player characters
  - `quests.json`: Game quests and objectives
  - `templates.json`: Text templates
  - `variables.json`: Game variables

## License

MIT License
