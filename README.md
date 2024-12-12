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
pip install -r requirements.txt
```

## Running the Game

To start the game:
```bash
python src/shmoopland/game.py
```

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
- `game.py`: Main game entry point
- `game_data.json`: Game world configuration

## License

MIT License
