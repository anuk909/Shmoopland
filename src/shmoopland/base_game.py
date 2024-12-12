import json
import sys
from os import system
from click import getchar

class ShmooplandGame:
    """Base class for the Shmoopland text adventure game."""

    def __init__(self):
        self.game_data = {}
        self.current_location = "start"
        self.inventory = []

    @classmethod
    def load_game_data(cls, json_file="game_data.json"):
        """Load game data from JSON file."""
        try:
            with open(json_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f'Game data file "{json_file}" not found.')
            sys.exit(1)

    def look(self):
        """Display current location description."""
        location = self.game_data['locations'].get(self.current_location, {})
        print("\n" + location.get('description', 'You are in an unknown place.'))

        # Show items in the location
        items = [item for item in self.game_data['items']
                if self.game_data['items'][item]['location'] == self.current_location]
        for item in items:
            print(f"There is a {item} here.")

    def inventory_command(self):
        """Show player's inventory."""
        if not self.inventory:
            print("\nYou are not carrying anything.")
            return
        print("\nYou are carrying:")
        for item in self.inventory:
            print(f"- {item}")

    def help_command(self):
        """Display available commands."""
        print("\nAvailable commands:")
        print("- look: Look around the current location")
        print("- inventory: Check what you're carrying")
        print("- take [item]: Pick up an item")
        print("- drop [item]: Drop an item")
        print("- go [direction]: Move in a direction (north, south, east, west)")
        print("- quit: Exit the game")
        print("\nPress any key to continue...")
        getchar()

    def parse_command(self, command):
        """Parse and execute player commands."""
        words = command.lower().split()
        if not words:
            return

        action = words[0]
        if action == "quit":
            confirm = input("\nAre you sure you want to quit? (y/n) ")
            if confirm.lower() == 'y':
                print("\nThanks for playing Shmoopland!")
                sys.exit(0)
        elif action == "look":
            self.look()
        elif action == "inventory":
            self.inventory_command()
        elif action == "help":
            self.help_command()

    def run_game(self):
        """Main game loop."""
        system('clear')
        print("Welcome to Shmoopland!")
        print("Type 'help' for a list of commands.")

        while True:
            command = input("\n> ")
            self.parse_command(command)
