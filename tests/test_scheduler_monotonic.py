import pytest
import time
import asyncio
from unittest.mock import patch
from src.orchestrator.scheduler import TaskScheduler

@pytest.mark.anyio
async def test_scheduler_monotonic_delay():
    scheduler = TaskScheduler()
    task = {"type": "delayed_job"}

    # Use patch to mock time.monotonic and control the scheduling clock
    with patch("time.monotonic") as mock_monotonic:
        # Initial time is 1000.0
        mock_monotonic.return_value = 1000.0
        
        # Schedule with 5.0 seconds delay
        task_id = scheduler.schedule(task, delay=5.0, queue="default", priority=5)
        
        # At 1000.0, the task shouldn't be ready yet
        result = await scheduler.dequeue(queue="default")
        assert result is None
        
        # Advance the clock to 1004.9, still not ready
        mock_monotonic.return_value = 1004.9
        result = await scheduler.dequeue(queue="default")
        assert result is None
        
        # Advance clock to exactly 1005.0, task should now be expired and enqueued/dequeued
        mock_monotonic.return_value = 1005.0
        result = await scheduler.dequeue(queue="default")
        assert result is not None
        assert result["type"] == "delayed_job"
        assert result["priority"] == 5
