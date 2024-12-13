"""Utility functions for memory monitoring and resource management."""

import gc
import os
import psutil
import functools
import logging
from typing import Any, Callable, Optional
from memory_profiler import profile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_process_memory() -> float:
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def monitor_memory(threshold_mb: float = 50.0):
    """Decorator to monitor memory usage of functions.

    Args:
        threshold_mb: Maximum allowed memory usage in MB
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            initial_memory = get_process_memory()

            try:
                result = func(*args, **kwargs)

                final_memory = get_process_memory()
                memory_used = final_memory - initial_memory

                if memory_used > threshold_mb:
                    logger.warning(f"{func.__name__} used {memory_used:.2f}MB of memory "
                                 f"(threshold: {threshold_mb}MB)")
                    gc.collect()  # Force garbage collection

                return result

            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                gc.collect()
                raise

        return wrapper
    return decorator

def cleanup_resources(cls: type) -> type:
    """Class decorator to ensure proper resource cleanup."""
    original_del = cls.__del__ if hasattr(cls, '__del__') else None

    def __del__(self):
        """Enhanced destructor with resource cleanup."""
        try:
            if hasattr(self, 'cleanup'):
                self.cleanup()
            if original_del:
                original_del(self)
        finally:
            gc.collect()

    cls.__del__ = __del__
    return cls

def force_cleanup() -> None:
    """Force cleanup of memory and resources."""
    gc.collect()
    if hasattr(gc, 'garbage'):
        del gc.garbage[:]

def log_memory_usage(func: Optional[Callable] = None, message: str = "") -> Callable:
    """Decorator to log memory usage before and after function execution.

    Can be used as a decorator with or without arguments:
    @log_memory_usage
    def func(): ...

    @log_memory_usage(message="Custom message")
    def func(): ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            initial = get_process_memory()
            logger.info(f"{message or func.__name__} - Initial memory: {initial:.2f}MB")

            result = func(*args, **kwargs)

            final = get_process_memory()
            logger.info(f"{message or func.__name__} - Final memory: {final:.2f}MB "
                      f"(Change: {final - initial:+.2f}MB)")
            return result
        return wrapper

    if func is None:
        return decorator
    return decorator(func)
