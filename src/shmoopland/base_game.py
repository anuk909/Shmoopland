import json
import sys
import gc
from typing import Dict, List, Any, Optional
from .content_generator import ContentGenerator
from .ai_utils import GameAI
from .npc import NPC
from .utils import monitor_memory, cleanup_resources

@cleanup_resources
class ShmooplandGame:
    """Base class for the Shmoopland text adventure game."""

    def __init__(self):
        """Initialize game with lazy loading and minimal memory footprint."""
        # Initialize attributes that will be lazy loaded
        self.content_generator = None
        self.ai = None
        self.npcs = None
        self.game_data = None

        # Set initial game state with minimal data
        self.current_location = "start"  # Changed back to match tests
        self.inventory: List[str] = []
        self.game_state = {
            "visited_locations": set([self.current_location]),
            "collected_items": set(),
            "time_of_day": "morning",
            "activity_level": "moderate"
        }

        # Load initial data with memory optimization
        self._load_game_data()  # Load only necessary data
        self._initialize_components()  # Initialize essential components

    def _initialize_components(self):
        """Initialize game components with lazy loading."""
        if self.content_generator is None:
            from .content_generator import ContentGenerator
            self.content_generator = ContentGenerator(self.game_data)

        if self.ai is None:
            from .ai_utils import GameAI
            self.ai = GameAI()

        if self.npcs is None:
            self.npcs = self._initialize_npcs()

    def _load_game_data(self):
        """Load only necessary game data components."""
        try:
            # Clear any existing data to free memory
            if self.game_data:
                self.game_data.clear()
                gc.collect()

            with open("data/game_data.json", 'r') as file:
                data = json.load(file)
                # Only load essential data initially
                self.game_data = {
                    'locations': {
                        self.current_location: data['locations'][self.current_location]
                    },
                    'items': {
                        k: v for k, v in data['items'].items()
                        if v['location'] == self.current_location
                    },
                    'description_variables': {
                        k: v for k, v in data.get('description_variables', {}).items()
                        if k in ['time_periods', 'activity_levels']  # Only load essential variables
                    }
                }

                # Store file path for lazy loading other locations
                self._data_file = "data/game_data.json"
                gc.collect()  # Force garbage collection after loading
        except FileNotFoundError:
            print(f'Game data file "data/game_data.json" not found.')
            sys.exit(1)

    def _initialize_npcs(self) -> Dict[str, NPC]:
        """Initialize NPCs with their templates."""
        return {
            npc_type: NPC(npc_type, templates)
            for npc_type, templates in self.game_data.get('npcs', {}).items()
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
        """Display the current location and its contents."""
        self._initialize_components()  # Ensure components are initialized

        # Get location description
        location = self.game_data['locations'].get(self.current_location, {})
        context = {
            "time_of_day": self.game_state["time_of_day"],
            "activity_level": self.game_state["activity_level"]
        }

        description = self.content_generator.generate_description(
            self.current_location,
            context
        ) or location.get('description', 'You are in an undefined location.')

        print(f"\n{description}\n")

        # Show available exits
        exits = location.get('exits', {})
        if exits:
            print("You can go:", ", ".join(exits.keys()))
            print()

        # Show NPCs
        npcs_here = {npc_type: npc for npc_type, npc in self.npcs.items()
                    if npc.location == self.current_location}
        if npcs_here:
            print("You see some characters:")
            for npc_type, npc in npcs_here.items():
                print(f"- {npc_type.title()}: {npc.get_greeting()}")

        # Show items with dynamic descriptions
        items = [item for item, data in self.game_data['items'].items()
                if data['location'] == self.current_location]
        if items:
            print("\nYou also see:")
            for item in items:
                item_data = self.game_data['items'][item]
                # Try template first, then static description, then default
                item_desc = (
                    self.content_generator.generate_item_description(item, context) or
                    item_data.get('description', f"a mysterious {item}")
                )
                print(f"- {item}: {item_desc}")

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
        print("- inventory: Check your inventory")
        print("- go <direction>: Move in a direction (north, south, east, west, up, down)")
        print("- take <item>: Pick up an item")
        print("- drop <item>: Drop an item from your inventory")
        print("- examine <item>: Look at an item more closely")
        print("- talk <character>: Talk to an NPC")
        print("- quit: Exit the game")

    def move(self, direction: str) -> None:
        """Move to a new location."""
        location = self.game_data['locations'].get(self.current_location, {})
        exits = location.get('exits', {})

        if direction in exits:
            new_location = exits[direction]
            self.current_location = new_location

            # Load new location data
            with open(self._data_file, 'r') as file:
                data = json.load(file)
                # Update only necessary data for new location
                self.game_data['locations'] = {
                    self.current_location: data['locations'][self.current_location]
                }
                self.game_data['items'] = {
                    k: v for k, v in data['items'].items()
                    if v['location'] == self.current_location
                }
                gc.collect()  # Clean up old location data

            self.look()
        else:
            print("\nYou can't go that way.")

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
        """Examine an item closely with dynamic description."""
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

        context = {
            "time_of_day": self.game_state["time_of_day"],
            "activity_level": self.game_state["activity_level"],
            **self.game_data.get("item_variables", {})
        }

        description = self.content_generator.generate_item_description(
            item_name,
            context
        ) or items[item_name].get('examine_text', items[item_name]['description'])

        print(f"\n{description}")

    def talk(self, npc_type: str) -> None:
        """Talk to an NPC."""
        if not npc_type:
            print("\nWho do you want to talk to?")
            return

        npc_type = npc_type.lower()
        if npc_type not in self.npcs:
            print(f"\nThere's no {npc_type} here to talk to.")
            return

        npc = self.npcs[npc_type]
        if npc_type not in [n for n, data in self.game_data.get('npcs', {}).items()
                           if data.get('location') == self.current_location]:
            print(f"\nThere's no {npc_type} here to talk to.")
            return

        print(f"\n{npc_type.title()}: {npc.get_greeting()}")
        while True:
            try:
                response = input("\nWhat do you say? (or 'bye' to end conversation) ")
                if response.lower() in ['bye', 'goodbye', 'farewell']:
                    print(f"\n{npc_type.title()}: Safe travels!")
                    break
                print(f"\n{npc_type.title()}: {npc.respond_to(response, self.ai)}")
            except KeyboardInterrupt:
                print("\nConversation ended.")
                break

    def parse_command(self, command: str) -> None:
        """Parse and execute player commands with AI-enhanced understanding."""
        if not command:
            return

        # Analyze command using AI
        analysis = self.ai.analyze_command(command)
        words = command.lower().split()
        action = words[0]
        args = words[1:] if len(words) > 1 else []

        # Use AI analysis for enhanced command understanding
        if analysis["intent"] == "movement" and args:
            self.move(args[0])
            return
        elif analysis["intent"] == "interaction":
            if action == "examine" and args:
                self.examine(" ".join(args))
                return
            elif action == "talk" and args:
                self.talk(" ".join(args))
                return

        # Handle standard commands
        if action == "quit":
            confirm = input("\nAre you sure you want to quit? (y/n) ")
            if confirm.lower() == 'y':
                self.cleanup()
                print("\nThanks for playing Shmoopland!")
                sys.exit(0)
        elif action == "look":
            self.look()
        elif action == "inventory":
            self.inventory_command()
        elif action == "help":
            self.help_command()
        elif action == "take" and args:
            self.take(" ".join(args))
        elif action == "drop" and args:
            self.drop(" ".join(args))
        else:
            print("\nI don't understand that command. Type 'help' for a list of commands.")

    def cleanup(self):
        """Clean up resources and free memory."""
        if self.content_generator:
            self.content_generator.cleanup()
        if self.ai:
            self.ai.cleanup()

        # Clear caches and references
        self.game_data = None
        self.content_generator = None
        self.ai = None
        self.npcs = None
        gc.collect()  # Force garbage collection
