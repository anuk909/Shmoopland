"""Dynamic content generator for Shmoopland with memory-efficient implementation.

This module handles procedural content generation while maintaining low RAM usage
through efficient template processing and caching.
"""
import random
from typing import Dict, List, Optional
from memory_profiler import profile
from .utils import monitor_memory

@monitor_memory(threshold_mb=50.0)
class ContentGenerator:
    """Generates dynamic content for game locations and items."""

    def __init__(self, templates: Dict):
        self.templates = templates
        self._cache = {}  # Cache for frequently used combinations

    @monitor_memory(threshold_mb=20.0)
    def generate_description(self, location: str, context: Dict) -> Optional[str]:
        """Generate dynamic description for a location.

        Args:
            location: Location identifier
            context: Context variables for template

        Returns:
            Generated description or None if no template exists
        """
        # Create a cache key using only hashable components
        cache_key = f"{location}:{hash(tuple(sorted((k, str(v)) for k, v in context.items())))}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        templates = self.templates.get("description_templates", {})
        location_templates = templates.get(location, [])

        if not location_templates:
            return None

        template = random.choice(location_templates)
        variables = self._get_variables(context)

        try:
            description = template.format(**variables)
            self._cache[cache_key] = description
            return description
        except KeyError:
            return None

    def generate_item_description(self, item: str, context: Dict) -> str:
        """Generate a dynamic description for an item.

        Args:
            item: Item identifier
            context: Variables for template substitution

        Returns:
            Generated item description
        """
        templates = self.templates.get("item_templates", {}).get(item, [])
        if not templates:
            return ""

        template = random.choice(templates)
        return template.format(**self._get_variables(context))

    def _get_variables(self, context: Dict) -> Dict:
        """Get template variables with fallbacks.

        Args:
            context: Current context variables

        Returns:
            Dictionary of variables for template substitution
        """
        variables = {}
        for key, value in context.items():
            if isinstance(value, str):
                variables[key] = value
            elif isinstance(value, list):
                variables[key] = random.choice(value)
            else:
                variables[key] = str(value)
        return variables

    def cleanup(self) -> None:
        """Clear caches to free memory."""
        self._cache.clear()
