"""vLLM metrics collection via HTTP API."""

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


def get_vllm_metrics(port: int = 8000) -> dict[str, Any]:
    """Get vLLM metrics via HTTP API.

    Args:
        port (int): vLLM server port. Defaults to 8000.

    Returns:
        Dict[str, Any]: Dictionary containing vLLM metrics.
                       Returns empty dict on error or if server unavailable.
    """
    metrics = {}

    try:
        response = requests.get(f"http://localhost:{port}/metrics", timeout=5)
        if response.status_code == 200:
            # Parse Prometheus-style metrics
            lines = response.text.split("\n")
            for line in lines:
                if line.startswith("#") or not line.strip():
                    continue
                if " " in line:
                    metric_name, value = line.split(" ", 1)
                    try:
                        metrics[f"vllm_{metric_name}"] = float(value)
                    except ValueError:
                        # Skip non-numeric values
                        pass

            logger.debug(f"Collected {len(metrics)} vLLM metrics from port {port}")
        else:
            logger.warning(
                f"vLLM metrics endpoint returned status {response.status_code}"
            )

    except requests.exceptions.RequestException as e:
        logger.debug(f"Could not connect to vLLM metrics endpoint on port {port}: {e}")
    except Exception as e:
        logger.error(f"Error collecting vLLM metrics: {e}")

    return metrics
