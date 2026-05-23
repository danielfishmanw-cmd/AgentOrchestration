import pytest
import time
from src.agent.registry import AgentRegistry, AgentStatus

def test_heartbeat_lifecycle():
    registry = AgentRegistry()
    agent_id = registry.register("active-agent", "worker.processor")
    
    # Active heartbeat should succeed on a fresh agent (status PENDING)
    assert registry.record_heartbeat(agent_id) is True
    
    # Status updated to RUNNING: heartbeat should still succeed
    registry.update_status(agent_id, AgentStatus.RUNNING)
    assert registry.record_heartbeat(agent_id) is True
    
    # Status updated to PAUSED: heartbeat should still succeed
    registry.update_status(agent_id, AgentStatus.PAUSED)
    assert registry.record_heartbeat(agent_id) is True

    # Heartbeat on non-existent agent should return False
    assert registry.record_heartbeat("non-existent-agent-id") is False

def test_heartbeat_rejects_terminal_statuses():
    registry = AgentRegistry()
    
    # Terminal state: STOPPED
    stopped_id = registry.register("stopped-agent", "worker.processor")
    registry.update_status(stopped_id, AgentStatus.STOPPED)
    with pytest.raises(ValueError, match="Cannot record heartbeat for agent .* in terminal status 'stopped'"):
        registry.record_heartbeat(stopped_id)

    # Terminal state: FAILED
    failed_id = registry.register("failed-agent", "worker.processor")
    registry.update_status(failed_id, AgentStatus.FAILED)
    with pytest.raises(ValueError, match="Cannot record heartbeat for agent .* in terminal status 'failed'"):
        registry.record_heartbeat(failed_id)

    # Terminal state: TERMINATED
    terminated_id = registry.register("terminated-agent", "worker.processor")
    registry.update_status(terminated_id, AgentStatus.TERMINATED)
    with pytest.raises(ValueError, match="Cannot record heartbeat for agent .* in terminal status 'terminated'"):
        registry.record_heartbeat(terminated_id)
