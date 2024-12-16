"""Crafting system for Shmoopland with memory-efficient design."""
import json
from typing import Dict, Set, List, Optional, Tuple
from dataclasses import dataclass
from .utils import monitor_memory, cleanup_resources

@dataclass
class Recipe:
    """Represents a crafting recipe with minimal memory footprint."""
    name: str
    ingredients: List[str]
    result: str
    description: str
    required_location: Optional[str] = None

@monitor_memory(threshold_mb=5.0)
@cleanup_resources
class CraftingSystem:
    """Memory-efficient crafting system."""

    def __init__(self):
        """Initialize with minimal memory footprint."""
        self.recipes: Dict[str, Recipe] = {}
        self.materials: Set[str] = set()
        self._loaded = False

    def _load_recipes(self) -> None:
        """Lazy load recipes from items.json."""
        if not self._loaded:
            try:
                with open("data/game/items.json", 'r') as file:
                    data = json.load(file)
                    recipes_data = data.get('recipes', {})

                    for recipe_id, recipe_data in recipes_data.items():
                        recipe = Recipe(
                            name=recipe_data['name'],
                            ingredients=recipe_data['ingredients'],
                            result=recipe_data['result'],
                            description=recipe_data['description'],
                            required_location=recipe_data.get('required_location')
                        )
                        self.recipes[recipe_id] = recipe
                        self.materials.update(recipe.ingredients)

                    self._loaded = True
            except FileNotFoundError:
                print("Warning: Items data file not found.")
                self._loaded = True

    def get_available_recipes(self, inventory: List[str], location: str) -> List[Recipe]:
        """Get recipes available with current inventory and location."""
        self._load_recipes()
        available = []

        inventory_set = set(inventory)
        for recipe in self.recipes.values():
            if (not recipe.required_location or recipe.required_location == location) and \
               all(ingredient in inventory_set for ingredient in recipe.ingredients):
                available.append(recipe)

        return available

    def craft_item(self, recipe_id: str, inventory: List[str], location: str) -> Tuple[bool, str, Optional[str]]:
        """
        Attempt to craft an item.
        Returns: (success, message, crafted_item)
        """
        self._load_recipes()

        if recipe_id not in self.recipes:
            return False, "Recipe not found.", None

        recipe = self.recipes[recipe_id]
        if recipe.required_location and recipe.required_location != location:
            return False, f"You must be at the {recipe.required_location} to craft this.", None

        inventory_set = set(inventory)
        if not all(ingredient in inventory_set for ingredient in recipe.ingredients):
            return False, "You don't have all required ingredients.", None

        # Remove ingredients from inventory
        for ingredient in recipe.ingredients:
            inventory.remove(ingredient)

        return True, f"Successfully crafted {recipe.result}!", recipe.result

    def get_recipe_details(self, recipe_id: str) -> Optional[str]:
        """Get detailed description of a recipe."""
        self._load_recipes()

        if recipe_id not in self.recipes:
            return None

        recipe = self.recipes[recipe_id]
        return (f"Recipe: {recipe.name}\n"
                f"Description: {recipe.description}\n"
                f"Ingredients: {', '.join(recipe.ingredients)}\n"
                f"Creates: {recipe.result}" +
                (f"\nRequired Location: {recipe.required_location}"
                 if recipe.required_location else ""))

    def cleanup(self) -> None:
        """Clean up resources."""
        self.recipes.clear()
        self.materials.clear()
        self._loaded = False
