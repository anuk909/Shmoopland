"""Utility functions and decorators for Shmoopland game."""
import functools
import logging
from typing import Callable, Any
from memory_profiler import profile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_memory(threshold_mb: float = 50.0) -> Callable:
    """Decorator to monitor memory usage of functions.

    Args:
        threshold_mb: Maximum allowed memory usage in MB

    Returns:
        Decorated function that monitors memory usage
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        @profile
        def wrapper(*args, **kwargs) -> Any:
            """Wrapper function that monitors memory usage."""
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator

def cleanup_resources(func: Callable) -> Callable:
    """Decorator to ensure proper cleanup of resources.

    Returns:
        Decorated function that handles cleanup
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        """Wrapper function that ensures cleanup."""
        try:
            return func(*args, **kwargs)
        finally:
            # Get instance (self) from args if it exists
            if args and hasattr(args[0], 'cleanup'):
                args[0].cleanup()
    return wrapper
