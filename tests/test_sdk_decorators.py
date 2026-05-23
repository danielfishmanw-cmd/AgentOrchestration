import pytest
from src.sdk.decorators import task

def test_task_decorator_metadata():
    @task(name="test_my_task", retries=5, timeout=120)
    async def sample_task():
        return 42

    # Verify wrapper function has the __task_config__ attribute
    assert hasattr(sample_task, "__task_config__")
    config = sample_task.__task_config__
    assert config["name"] == "test_my_task"
    assert config["retries"] == 5
    assert config["timeout"] == 120

def test_task_decorator_defaults():
    @task()
    async def default_task():
        pass

    assert hasattr(default_task, "__task_config__")
    config = default_task.__task_config__
    assert config["name"] == "default_task"
    assert config["retries"] == 0
    assert config["timeout"] == 300
