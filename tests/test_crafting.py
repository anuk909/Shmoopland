"""Tests for the crafting system."""
import pytest
from shmoopland.crafting import CraftingSystem, Recipe

def test_crafting_initialization():
    """Test crafting system initialization."""
    system = CraftingSystem()
    assert len(system.recipes) == 0
    assert len(system.materials) == 0

def test_recipe_loading():
    """Test recipe loading from items.json."""
    system = CraftingSystem()
    system._load_recipes()
    assert len(system.recipes) > 0
    assert len(system.materials) > 0

def test_available_recipes():
    """Test getting available recipes."""
    system = CraftingSystem()
    inventory = ["crystal_prism", "singing_flower"]
    location = "wizard_tower"
    recipes = system.get_available_recipes(inventory, location)
    assert len(recipes) > 0
    assert all(isinstance(recipe, Recipe) for recipe in recipes)

def test_crafting_item():
    """Test crafting an item."""
    system = CraftingSystem()
    inventory = ["crystal_prism", "singing_flower"]
    location = "wizard_tower"
    success, message, item = system.craft_item("magic_charm", inventory, location)
    assert success
    assert item == "enchanted_charm"
    assert "crystal_prism" not in inventory
    assert "singing_flower" not in inventory

def test_invalid_crafting():
    """Test crafting with invalid conditions."""
    system = CraftingSystem()
    inventory = ["crystal_prism"]
    location = "market"
    success, message, item = system.craft_item("magic_charm", inventory, location)
    assert not success
    assert item is None
    assert "crystal_prism" in inventory

def test_recipe_details():
    """Test getting recipe details."""
    system = CraftingSystem()
    details = system.get_recipe_details("magic_charm")
    assert details is not None
    assert "Recipe:" in details
    assert "Ingredients:" in details
