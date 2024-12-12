import json
import sys
from os import system
from click import getchar
from typing import Optional, Dict, List

class ShmooplandGame:
    """Base class for the Shmoopland text adventure game."""

    def __init__(self):
        self.game_data = self.load_game_data("data/game_data.json")
        self.current_location = "start"
        self.inventory: List[str] = []
        self.game_state = {
            "visited_locations": set(["start"]),
            "collected_items": set()
        }

    @classmethod
    def load_game_data(cls, json_file: str) -> Dict:
        """Load game data from JSON file."""
        try:
            with open(json_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f'Game data file "{json_file}" not found.')
            sys.exit(1)

    def look(self) -> None:
        """Display current location description."""
        location = self.game_data['locations'].get(self.current_location, {})
        print("\n" + location.get('description', 'You are in an unknown place.'))

        # Show available exits
        exits = location.get('exits', {})
        if exits:
            print("\nYou can go:", ", ".join(exits.keys()))

        # Show items in the location
        items = [item for item, data in self.game_data['items'].items()
                if data['location'] == self.current_location]
        if items:
            print("\nYou see:")
            for item in items:
                print(f"- {item}: {self.game_data['items'][item]['description']}")

    def inventory_command(self) -> None:
        """Show player's inventory."""
        if not self.inventory:
            print("\nYou are not carrying anything.")
            return
        print("\nYou are carrying:")
        for item in self.inventory:
            print(f"- {item}: {self.game_data['items'][item]['description']}")

    def help_command(self) -> None:
        """Display available commands."""
        print("\nAvailable commands:")
        print("- look: Look around the current location")
        print("- inventory (or 'i'): Check what you're carrying")
        print("- take [item]: Pick up an item")
        print("- drop [item]: Drop an item")
        print("- go [direction] (or just type the direction): Move in a direction")
        print("- examine [item]: Look at an item closely")
        print("- quit: Exit the game")
        print("\nPress any key to continue...")
        getchar()

    def move(self, direction: str) -> None:
        """Move player in the specified direction."""
        location = self.game_data['locations'].get(self.current_location, {})
        exits = location.get('exits', {})

        if direction not in exits:
            print(f"\nYou can't go {direction} from here.")
            return

        self.current_location = exits[direction]
        self.game_state['visited_locations'].add(self.current_location)
        self.look()

    def take(self, item_name: str) -> None:
        """Pick up an item."""
        if not item_name:
            print("\nWhat do you want to take?")
            return

        items = self.game_data['items']
        if item_name not in items:
            print(f"\nThere is no {item_name} here.")
            return

        if items[item_name]['location'] != self.current_location:
            print(f"\nThere is no {item_name} here.")
            return

        self.inventory.append(item_name)
        items[item_name]['location'] = 'inventory'
        self.game_state['collected_items'].add(item_name)
        print(f"\nYou take the {item_name}.")

    def drop(self, item_name: str) -> None:
        """Drop an item."""
        if not item_name:
            print("\nWhat do you want to drop?")
            return

        if item_name not in self.inventory:
            print(f"\nYou don't have a {item_name}.")
            return

        self.inventory.remove(item_name)
        self.game_data['items'][item_name]['location'] = self.current_location
        print(f"\nYou drop the {item_name}.")

    def examine(self, item_name: str) -> None:
        """Examine an item closely."""
        if not item_name:
            print("\nWhat do you want to examine?")
            return

        items = self.game_data['items']
        if item_name not in items:
            print(f"\nYou don't see any {item_name} to examine.")
            return

        if (items[item_name]['location'] != self.current_location and
            items[item_name]['location'] != 'inventory'):
            print(f"\nYou don't see any {item_name} to examine.")
            return

        print(f"\n{items[item_name].get('examine_text', items[item_name]['description'])}")

    def parse_command(self, command: str) -> None:
        """Parse and execute player commands."""
        words = command.lower().split()
        if not words:
            return

        action = words[0]
        args = words[1:] if len(words) > 1 else []

        # Handle movement shortcuts (just typing a direction)
        if action in ['north', 'south', 'east', 'west', 'up', 'down']:
            self.move(action)
            return

        # Handle other commands
        if action == "quit":
            confirm = input("\nAre you sure you want to quit? (y/n) ")
            if confirm.lower() == 'y':
                print("\nThanks for playing Shmoopland!")
                sys.exit(0)
        elif action == "look":
            self.look()
        elif action in ["inventory", "i"]:
            self.inventory_command()
        elif action == "help":
            self.help_command()
        elif action == "go" and args:
            self.move(args[0])
        elif action == "take":
            self.take(" ".join(args))
        elif action == "drop":
            self.drop(" ".join(args))
        elif action == "examine":
            self.examine(" ".join(args))
        else:
            print("\nI don't understand that command. Type 'help' for a list of commands.")
