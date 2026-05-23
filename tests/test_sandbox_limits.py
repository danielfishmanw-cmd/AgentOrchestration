import pytest
from unittest.mock import patch, MagicMock
import resource
from src.agent.sandbox import ResourceLimits, AgentSandbox

def test_resource_limits_validation():
    # Valid parameters should succeed
    limits = ResourceLimits(cpu_time=10, memory_mb=128, disk_mb=50)
    assert limits.cpu_time == 10
    assert limits.memory_mb == 128
    assert limits.disk_mb == 50

    # Type validation
    with pytest.raises(TypeError, match="cpu_time must be numeric"):
        ResourceLimits(cpu_time="60")
    with pytest.raises(TypeError, match="memory_mb must be numeric"):
        ResourceLimits(memory_mb=True)  # booleans rejected
    with pytest.raises(TypeError, match="disk_mb must be numeric"):
        ResourceLimits(disk_mb=[100])

    # Value validation
    with pytest.raises(ValueError, match="cpu_time must be positive"):
        ResourceLimits(cpu_time=0)
    with pytest.raises(ValueError, match="memory_mb must be positive"):
        ResourceLimits(memory_mb=-10)
    with pytest.raises(ValueError, match="disk_mb must be positive"):
        ResourceLimits(disk_mb=-0.5)

def test_apply_limits_calls_setrlimit():
    sandbox = AgentSandbox()
    limits = ResourceLimits(cpu_time=30, memory_mb=256, disk_mb=20)
    
    with patch("resource.setrlimit") as mock_setrlimit:
        sandbox.apply_limits("test_agent", limits)
        
        # Verify it was called for RLIMIT_CPU, RLIMIT_AS, and RLIMIT_FSIZE
        assert mock_setrlimit.call_count == 3
        
        # RLIMIT_CPU should be cpu_time
        mock_setrlimit.assert_any_call(resource.RLIMIT_CPU, (30, 30))
        
        # RLIMIT_AS should be memory_mb in bytes
        mock_setrlimit.assert_any_call(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
        
        # RLIMIT_FSIZE should be disk_mb in bytes
        mock_setrlimit.assert_any_call(resource.RLIMIT_FSIZE, (20 * 1024 * 1024, 20 * 1024 * 1024))
