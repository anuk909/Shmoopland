"""Tests for memory monitoring and management."""

import pytest
from memory_profiler import profile
from shmoopland.utils import (
    get_process_memory,
    monitor_memory,
    cleanup_resources,
    log_memory_usage
)

def test_get_process_memory():
    """Test memory usage measurement."""
    memory = get_process_memory()
    assert isinstance(memory, float)
    assert memory > 0

@profile
def test_monitor_memory_decorator():
    """Test memory monitoring decorator."""
    @monitor_memory(threshold_mb=1.0)
    def memory_intensive_function():
        # Create some memory usage
        large_list = [i for i in range(100000)]
        return len(large_list)

    result = memory_intensive_function()
    assert result == 100000

@cleanup_resources
class DummyResource:
    def __init__(self):
        self.data = [i for i in range(1000)]

    def cleanup(self):
        self.data = None

def test_cleanup_resources():
    """Test resource cleanup decorator."""
    resource = DummyResource()
    assert resource.data is not None
    del resource
    # Memory should be freed

@log_memory_usage
def test_memory_intensive_operation():
    """Test memory profiling of intensive operations."""
    data = []
    for i in range(10000):
        data.append(str(i) * 100)
    assert len(data) == 10000
