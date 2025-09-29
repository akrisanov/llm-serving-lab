"""System metrics collection using psutil."""

import logging
from typing import Any

import psutil

logger = logging.getLogger(__name__)


def get_system_metrics() -> dict[str, Any]:
    """Get system metrics including CPU, memory, disk, and load average.

    Returns:
        Dict[str, Any]: Dictionary containing system metrics.
    """
    metrics = {}

    try:
        # CPU metrics
        metrics["cpu_percent"] = psutil.cpu_percent()
        metrics["cpu_count"] = psutil.cpu_count()

        # Memory metrics
        mem = psutil.virtual_memory()
        metrics["memory_total"] = mem.total
        metrics["memory_available"] = mem.available
        metrics["memory_percent"] = mem.percent

        # Disk metrics for root filesystem
        disk = psutil.disk_usage("/")
        metrics["disk_total"] = disk.total
        metrics["disk_used"] = disk.used
        metrics["disk_percent"] = (disk.used / disk.total) * 100

        # Load average
        load = psutil.getloadavg()
        metrics["load_1min"] = load[0]
        metrics["load_5min"] = load[1]
        metrics["load_15min"] = load[2]

        logger.debug(f"Collected {len(metrics)} system metrics")
        return metrics

    except Exception as e:
        logger.error(f"Error collecting system metrics: {e}")
        return {}
