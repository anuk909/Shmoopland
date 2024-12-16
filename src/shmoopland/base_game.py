"""Shmoopland game core implementation with AI-enhanced features."""

import sys
import gc
import json
import random
from typing import Dict, List, Optional, Set
from .utils import monitor_memory
from .content_generator import ContentGenerator
from .ai_utils import GameAI
from .npc import NPC
from .quest_manager import QuestManager
from .crafting import CraftingSystem
from .skills import SkillSystem

@monitor_memory(threshold_mb=100.0)
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
            try:
                import spacy
                try:
                    self.nlp = spacy.load('en_core_web_sm')
                    self.ai = GameAI(nlp_model=self.nlp)
                except OSError:
                    print("\nWarning: spaCy model not found. Using fallback mode.")
                    self.nlp = None
                    self.ai = GameAI(nlp_model=None)
            except ImportError:
                print("\nWarning: spaCy package not found. Using fallback mode.")
                self.nlp = None
                self.ai = GameAI(nlp_model=None)

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



    def look(self) -> str:
        """Look around the current location with AI-enhanced descriptions."""
        locations = self.game_data['locations']
        if self.current_location not in locations:
            return "You are in a mysterious void. Something has gone wrong!"

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
        result = [enhanced_desc]

        # List items in location
        items_here = [
            name for name, data in self.game_data['items'].items()
            if data['location'] == self.current_location
        ]
        if items_here:
            result.append(f"\nYou see: {', '.join(items_here)}")

        # List NPCs in location
        npcs_here = [
            npc for npc, data in self.game_data.get('npcs', {}).items()
            if data.get('location') == self.current_location
        ]
        if npcs_here:
            result.append(f"\nCharacters here: {', '.join(npcs_here)}")

        # Show available exits
        exits = location.get('exits', {})
        if exits:
            result.append(f"\nExits: {', '.join(exits.keys())}")

        return "\n".join(result)

    def inventory_command(self) -> str:
        """Show player's inventory."""
        if not self.inventory:
            return "Your inventory is empty."
        return "You are carrying: " + ", ".join(self.inventory)

    def help_command(self) -> str:
        """Show available commands."""
        commands = [
            "look - Look around the current location",
            "inventory - Check your inventory",
            "go <direction> - Move in a direction (north, south, east, west, up, down)",
            "take <item> - Pick up an item",
            "drop <item> - Drop an item from your inventory",
            "examine <item/npc> - Look at something more closely",
            "talk <npc> - Talk to a character",
            "quit/exit - Exit the game"
        ]
        return "\nAvailable commands:\n" + "\n".join(commands)

    def move(self, direction: str) -> str:
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

            return self.look()
        else:
            return "You can't go that way."

    def take(self, item_name: str) -> str:
        """Pick up an item."""
        if not item_name:
            return "What do you want to take?"

        items = self.game_data['items']
        if item_name not in items:
            return f"There is no {item_name} here."

        if items[item_name]['location'] != self.current_location:
            return f"There is no {item_name} here."

        self.inventory.append(item_name)
        items[item_name]['location'] = 'inventory'
        self.game_state['collected_items'].add(item_name)
        return f"You take the {item_name}."

    def drop(self, item_name: str) -> str:
        """Drop an item."""
        if not item_name:
            return "What do you want to drop?"

        if item_name not in self.inventory:
            return f"You don't have a {item_name}."

        self.inventory.remove(item_name)
        self.game_data['items'][item_name]['location'] = self.current_location
        return f"You drop the {item_name}."

    def examine(self, item_name: str) -> str:
        """Examine an item or NPC with AI-enhanced description."""
        if not item_name:
            return "What do you want to examine?"

        # Check inventory items
        if item_name in self.inventory:
            item = self.game_data['items'][item_name]
            enhanced_desc = self.ai.generate_description(
                item['description'],
                {"context": "detailed_examination"}
            )
            return f"\n{enhanced_desc}"

        # Check location items
        items = self.game_data['items']
        if (item_name in items and
            items[item_name]['location'] == self.current_location):
            item = items[item_name]
            enhanced_desc = self.ai.generate_description(
                item['description'],
                {"context": "detailed_examination"}
            )
            return f"\n{enhanced_desc}"

        # Check NPCs
        npcs = self.game_data.get('npcs', {})
        if (item_name in npcs and
            npcs[item_name].get('location') == self.current_location):
            npc = npcs[item_name]
            enhanced_desc = self.ai.generate_description(
                npc['description'],
                {"context": "character_examination"}
            )
            return f"\n{enhanced_desc}"

        return f"You don't see any {item_name} here."

    def talk(self, npc_name: str) -> str:
        """Talk to an NPC with context-aware responses."""
        if not npc_name:
            return "Who do you want to talk to?"

        npcs = self.game_data.get('npcs', {})
        if npc_name not in npcs:
            return f"There is no {npc_name} here."

        npc = npcs[npc_name]
        if npc.get('location') != self.current_location:
            return f"There is no {npc_name} here."

        # Generate context-aware dialogue
        context = {
            "npc_mood": npc.get('mood', 'neutral'),
            "time_of_day": self.game_state["time_of_day"],
            "player_inventory": self.inventory,
            "location": self.current_location
        }

        response = self.ai.generate_dialogue(npc, context)
        return f"\n{npc_name} says: {response}"

    def show_skills(self) -> str:
        """Show player's skills and levels."""
        if not self.game_state.get('skills'):
            return "You haven't learned any skills yet."

        skills = []
        for skill, data in self.game_state['skills'].items():
            skills.append(f"{skill}: Level {data['level']} ({data['exp']}/{data['next_level']} XP)")
        return "\nYour Skills:\n" + "\n".join(skills)

    def show_skill_details(self, skill_name: str) -> str:
        """Show details of a specific skill."""
        if not skill_name:
            return "Which skill do you want to know about?"

        skills = self.game_state.get('skills', {})
        if skill_name not in skills:
            return f"You haven't learned {skill_name} yet."

        skill = skills[skill_name]
        return f"\n{skill_name} - Level {skill['level']}\nExperience: {skill['exp']}/{skill['next_level']}\n{skill.get('description', '')}"

    def train_skill(self, skill_name: str) -> str:
        """Train a skill to gain experience."""
        return self.perform_skill_check(skill_name, "training")

    def perform_skill_check(self, skill_name: str, context: str) -> str:
        """Perform a skill check with the given context."""
        if skill_name not in self.game_state.get('skills', {}):
            return f"You don't have the {skill_name} skill."

        skill = self.game_state['skills'][skill_name]
        success = random.random() < (skill['level'] * 0.1 + 0.5)
        message = self.ai.generate_skill_result(skill_name, context, success)
        if success:
            skill['exp'] += random.randint(10, 20)
            if skill['exp'] >= skill['next_level']:
                skill['level'] += 1
                skill['next_level'] *= 2
                return f"{message}\nCongratulations! Your {skill_name} skill has increased to level {skill['level']}!"
        return message

    def cleanup(self):
        """Clean up resources."""
        if self.ai:
            self.ai.cleanup()
        if self.content_generator:
            self.content_generator.cleanup()
        if self.quest_manager:
            self.quest_manager.cleanup()
        if self.crafting_system:
            self.crafting_system.cleanup()
        if self.skills:
            self.skills.cleanup()
        gc.collect()

    def parse_command(self, command: str) -> str:
        """Parse and execute game command."""
        command = command.lower().strip()

        # Basic commands that don't need AI processing
        if command in ['quit', 'exit']:
            self.cleanup()
            return "Thanks for playing Shmoopland!"
        elif command == 'look':
            return self.look()
        elif command == 'inventory':
            return self.inventory_command()
        elif command == 'help':
            return self.help_command()

        # Movement commands
        if command.startswith('go '):
            direction = command[3:].strip()
            return self.move(direction)

        # Item interaction commands
        if command.startswith('take '):
            item = command[5:].strip()
            return self.take(item)
        elif command.startswith('drop '):
            item = command[5:].strip()
            return self.drop(item)
        elif command.startswith('examine '):
            target = command[8:].strip()
            return self.examine(target)

        # NPC interaction
        if command.startswith('talk '):
            npc = command[5:].strip()
            return self.talk(npc)

        # Skill commands
        if command == 'skills':
            return self.show_skills()
        elif command.startswith('train '):
            skill = command[6:].strip()
            return self.train_skill(skill)

        return "I don't understand that command. Type 'help' for a list of commands."
