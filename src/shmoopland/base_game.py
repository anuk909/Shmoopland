"""Shmoopland game core implementation with AI-enhanced features."""

import sys
import gc
import json
from typing import Dict, List, Optional, Set
from .utils import monitor_memory
from .content_generator import ContentGenerator
from .ai_utils import GameAI
from .npc import NPC
from .quest_manager import QuestManager
from .crafting import CraftingSystem
from .skills import SkillSystem

@monitor_memory(threshold_mb=50.0)
class ShmooplandGame:

    def __init__(self):
        """Initialize game with lazy loading and minimal memory footprint."""
        # Initialize attributes that will be lazy loaded
        self.content_generator = None
        self.ai = None
        self.npcs = None
        self.quest_manager = None
        self.crafting_system = None
        self.skills = None
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
            "currency": 0,
            "skill_points": 0
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

        if self.skills is None:
            self.skills = SkillSystem()

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



    def look(self) -> None:
        """Look around the current location with AI-enhanced descriptions."""
        locations = self.game_data['locations']
        if self.current_location not in locations:
            print("\nYou are in a mysterious void. Something has gone wrong!")
            return

        location = locations[self.current_location]

        # Generate AI-enhanced description based on context
        context = {
            "time_of_day": self.game_state["time_of_day"],
            "activity_level": self.game_state["activity_level"],
            **self.game_data.get("location_variables", {})
        }

        # Get base description
        description = location.get('description', '')

        # Enhance with AI-generated content
        enhanced_desc = self.ai.generate_description(description, context)
        print(f"\n{enhanced_desc}")

        # List items in location
        items_here = [
            name for name, data in self.game_data['items'].items()
            if data['location'] == self.current_location
        ]
        if items_here:
            print("\nYou see:", ", ".join(items_here))

        # List NPCs in location
        npcs_here = [
            npc for npc, data in self.game_data.get('npcs', {}).items()
            if data.get('location') == self.current_location
        ]
        if npcs_here:
            print("\nCharacters here:", ", ".join(npcs_here))

        # Show available exits
        exits = location.get('exits', {})
        if exits:
            print("\nExits:", ", ".join(exits.keys()))

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
        print("- skills: View your skills and levels")
        print("- skill <skill_name>: View details of a specific skill")
        print("- train <skill_name>: Practice a skill to gain experience")
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
        """Examine an item with AI-enhanced description."""
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
            "skill_level": self.skills.get_skill_level("lore"),
            **self.game_data.get("item_variables", {})
        }

        base_desc = items[item_name].get('examine_text', items[item_name]['description'])
        description = self.ai.generate_description(base_desc, context)
        print(f"\n{description}")

    def talk(self, npc_type: str) -> None:
        """Talk to an NPC with AI-enhanced interactions."""
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

        # Get AI-enhanced greeting based on NPC mood and context
        context = {
            "time_of_day": self.game_state["time_of_day"],
            "activity_level": self.game_state["activity_level"],
            "previous_interactions": self.game_state["npc_interactions"].get(npc_type, 0)
        }

        greeting = self.ai.generate_description(npc.get_greeting(), context)
        print(f"\n{npc_type.title()}: {greeting}")

        while True:
            try:
                response = input("\nWhat do you say? (or 'bye' to end conversation) ")
                if response.lower() in ['bye', 'goodbye', 'farewell']:
                    farewell = self.ai.generate_description(
                        "{npc} bids you farewell.",
                        {"npc": npc_type.title()}
                    )
                    print(f"\n{farewell}")
                    break

                # Use AI to analyze player's response and generate appropriate NPC reaction
                analysis = self.ai.analyze_command(response)
                npc_response = npc.respond_to(response, self.ai)
                print(f"\n{npc_type.title()}: {npc_response}")

                # Track interaction for future context
                self.game_state["npc_interactions"][npc_type] = \
                    self.game_state["npc_interactions"].get(npc_type, 0) + 1

            except KeyboardInterrupt:
                print("\nConversation ended abruptly.")
                break

    def show_skills(self) -> None:
        """Display all skills and their levels."""
        skills = self.skills.get_all_skills()
        print("\nYour Skills:")
        for name, info in skills.items():
            print(f"\n- {name.title()} (Level {info['level']})")
            print(f"  {info['description']}")
            print(f"  Experience: {info['experience']}/{info['next_level']}")

    def show_skill_details(self, skill_name: str) -> None:
        """Display detailed information about a specific skill."""
        desc = self.skills.get_skill_description(skill_name)
        if not desc:
            print(f"\nNo skill found with name: {skill_name}")
            return

        level = self.skills.get_skill_level(skill_name)
        print(f"\n{skill_name.title()} - Level {level}")
        print(f"Description: {desc}")

    def train_skill(self, skill_name: str) -> None:
        """Train a skill to gain experience."""
        success, message = self.skills.add_experience(skill_name, 10)
        print(f"\n{message}")

    def perform_skill_check(self, skill_name: str, difficulty: int) -> bool:
        """Perform a skill check and return success."""
        success, message = self.skills.check_skill(skill_name, difficulty)
        print(f"\n{message}")
        return success

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
        elif action == "skills":
            self.show_skills()
        elif action == "skill" and args:
            self.show_skill_details(" ".join(args))
        elif action == "train" and args:
            self.train_skill(" ".join(args))
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
        self.quest_manager = None
        self.crafting_system = None
        self.skills = None
        gc.collect()  # Force garbage collection
