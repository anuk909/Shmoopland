import json
import sys
import gc
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from .content_generator import ContentGenerator
from .ai_utils import GameAI
from .npc import NPC
from .quest_manager import QuestManager
from .crafting import CraftingSystem
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
        self.quest_manager = None
        self.crafting_system = None
        self.game_data = {}
        self._loaded_data_types: Set[str] = set()

        # Set initial game state with minimal data
        self.current_location = "start"
        self.inventory: List[str] = []
        self.game_state = {
            "visited_locations": set([self.current_location]),
            "collected_items": set(),
            "time_of_day": "morning",
            "activity_level": "moderate",
            "experience": 0,
            "currency": 0
        }

        # Load initial data with memory optimization
        self._load_game_data(["locations", "items"])  # Load only necessary initial data
        self._initialize_components()

    def _initialize_components(self):
        """Initialize game components with lazy loading."""
        if self.content_generator is None:
            self.content_generator = ContentGenerator(self.game_data)

        if self.ai is None:
            self.ai = GameAI()

        if self.npcs is None:
            self.npcs = self._initialize_npcs()

        if self.quest_manager is None:
            self.quest_manager = QuestManager()
            # Start initial quest if available
            available_quests = self.quest_manager.get_available_quests(self.game_state)
            if "welcome_to_shmoopland" in available_quests:
                self.quest_manager.start_quest("welcome_to_shmoopland")

        if self.crafting_system is None:
            self.crafting_system = CraftingSystem()

        gc.collect()  # Clean up any temporary objects

    def _needs_data_type(self, data_type: str) -> bool:
        """Check if a data type needs to be loaded."""
        if data_type in self._loaded_data_types:
            return False

        # Always need locations for current location
        if data_type == "locations":
            return True

        # Need items for current location
        if data_type == "items":
            return True

        # Need NPCs for interaction
        if data_type == "npcs" and self.current_location in self.game_data.get('locations', {}):
            return True

        # Need templates for description generation
        if data_type == "templates" and self.content_generator is not None:
            return True

        # Need variables for content generation
        if data_type == "variables" and self.content_generator is not None:
            return True

        return False

    def _load_game_data(self, required_types: Optional[List[str]] = None):
        """Load only necessary game data components."""
        try:
            data_types = required_types or ['locations', 'items', 'npcs', 'quests', 'templates', 'variables']

            for data_type in data_types:
                if self._needs_data_type(data_type):
                    file_path = f"data/game/{data_type}.json"
                    try:
                        with open(file_path, 'r') as file:
                            data = json.load(file)
                            if data_type == 'locations':
                                # Only load current location
                                self.game_data['locations'] = {
                                    self.current_location: data['locations'][self.current_location]
                                }
                            elif data_type == 'items':
                                # Only load items in current location
                                self.game_data['items'] = {
                                    k: v for k, v in data['items'].items()
                                    if v['location'] == self.current_location
                                }
                            else:
                                self.game_data[data_type] = data.get(data_type, {})

                            self._loaded_data_types.add(data_type)
                    except FileNotFoundError:
                        print(f'Game data file "{file_path}" not found.')
                        continue

            gc.collect()  # Force garbage collection after loading
        except Exception as e:
            print(f'Error loading game data: {str(e)}')
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

        # Show available recipes
        available_recipes = self.crafting_system.get_available_recipes(self.inventory, self.current_location)
        if available_recipes:
            print("\nYou can craft:")
            for recipe in available_recipes:
                print(f"- {recipe.name}: {recipe.description}")

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
        print("- quests: View your active quests")
        print("- quest <quest_id>: View details of a specific quest")
        print("- quit: Exit the game")

    def move(self, direction: str) -> None:
        """Move to a new location."""
        location = self.game_data['locations'].get(self.current_location, {})
        exits = location.get('exits', {})

        if direction in exits:
            new_location = exits[direction]
            self.current_location = new_location
            self.game_state['visited_locations'].add(new_location)

            # Clear old data and load new location data
            self.game_data.clear()
            self._loaded_data_types.clear()
            gc.collect()

            # Load necessary data for new location
            self._load_game_data(["locations", "items", "npcs"])

            # Update quest progress for visiting new location
            self._update_quest_progress("visit_location", new_location)

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
        elif action == "quests":
            self.show_quests()
        elif action == "quest" and args:
            self.show_quest_details(" ".join(args))
        else:
            print("\nI don't understand that command. Type 'help' for a list of commands.")

    def cleanup(self):
        """Clean up resources and free memory."""
        if self.content_generator:
            self.content_generator.cleanup()
        if self.ai:
            self.ai.cleanup()

        # Clear caches and references
        self.game_data.clear()
        self._loaded_data_types.clear()
        self.content_generator = None
        self.ai = None
        self.npcs = None
        gc.collect()  # Force garbage collection
