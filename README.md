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

3. Install dependencies:
```bash
pip install -e .
python -m spacy download en_core_web_sm  # Required for AI features
```

Note: The game requires Python 3.8+ and approximately 50MB RAM for AI features.

## Running the Game

### Terminal Mode
To start the game in terminal mode:
```bash
python src/shmoopland/game.py
```

### Web Interface
To start the web server:
```bash
python src/shmoopland/web_server.py
```
Then open http://localhost:5000 in your browser.

The web interface provides:
- Text-based adventure interface with command history
- Real-time game state updates
- Clickable command suggestions
- Mobile-friendly layout

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
