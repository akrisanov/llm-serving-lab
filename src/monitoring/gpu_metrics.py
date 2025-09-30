"""GPU metrics collection using NVIDIA ML library."""

import logging
from typing import Any

try:
    from pynvml import (
        NVML_TEMPERATURE_GPU,
        NVMLError,
        nvmlDeviceGetCount,
        nvmlDeviceGetHandleByIndex,
        nvmlDeviceGetMemoryInfo,
        nvmlDeviceGetPowerUsage,
        nvmlDeviceGetTemperature,
        nvmlDeviceGetUtilizationRates,
        nvmlInit,
    )

    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False

logger = logging.getLogger(__name__)


def init_nvidia() -> bool:
    """Initialize NVIDIA ML library.

    Returns:
        bool: True if initialization successful, False otherwise.
    """
    if not NVIDIA_AVAILABLE:
        logger.warning("nvidia-ml-py not available, GPU metrics will not be collected")
        return False

    try:
        nvmlInit()
        logger.info("NVIDIA ML library initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize NVIDIA ML: {e}")
        return False


def get_gpu_metrics() -> dict[str, Any]:
    """Get GPU metrics using nvidia-ml-py.

    Returns:
        Dict[str, Any]: Dictionary containing GPU metrics for all devices.
                       Returns empty dict if NVIDIA not available or on error.
    """
    if not NVIDIA_AVAILABLE:
        return {}

    try:
        device_count = nvmlDeviceGetCount()
        metrics = {}

        for i in range(device_count):
            handle = nvmlDeviceGetHandleByIndex(i)

            # GPU utilization
            util = nvmlDeviceGetUtilizationRates(handle)
            metrics[f"gpu_{i}_utilization"] = util.gpu
            metrics[f"gpu_{i}_memory_utilization"] = util.memory

            # Memory info
            mem_info = nvmlDeviceGetMemoryInfo(handle)
            metrics[f"gpu_{i}_memory_total"] = mem_info.total
            metrics[f"gpu_{i}_memory_used"] = mem_info.used
            metrics[f"gpu_{i}_memory_free"] = mem_info.free

            # Temperature
            temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
            metrics[f"gpu_{i}_temperature"] = temp

            # Power usage
            try:
                power = nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                metrics[f"gpu_{i}_power_draw"] = power
            except NVMLError:
                # Power usage not available on all GPUs
                pass

        logger.debug(f"Collected metrics for {device_count} GPU device(s)")
        return metrics

    except Exception as e:
        logger.error(f"Error collecting GPU metrics: {e}")
        return {}
