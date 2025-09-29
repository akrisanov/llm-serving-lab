"""
GPU and system metrics exporter for OpenTelemetry.
Sends metrics to OBS stack via OTLP.
"""

import logging
import os
import time
from typing import Any

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from .gpu_metrics import get_gpu_metrics, init_nvidia
from .system_metrics import get_system_metrics
from .vllm_metrics import get_vllm_metrics

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsExporter:
    """Main metrics exporter class."""

    def __init__(
        self,
        obs_otlp_endpoint: str,
        vllm_port: int = 8000,
        collect_interval: int = 30,
        gpu_type: str = "unknown",
    ):
        """Initialize metrics exporter.

        Args:
            obs_otlp_endpoint: OBS OTLP endpoint URL
            vllm_port: vLLM server port
            collect_interval: Collection interval in seconds
            gpu_type: GPU type identifier
        """
        self.obs_otlp_endpoint = obs_otlp_endpoint
        self.vllm_port = vllm_port
        self.collect_interval = collect_interval
        self.gpu_type = gpu_type

        # Initialize components
        self.meter = self._setup_otel()
        self.nvidia_available = init_nvidia()
        self.gauges = {}

        logger.info("Metrics exporter initialized")
        logger.info(f"OBS endpoint: {obs_otlp_endpoint}")
        logger.info(f"vLLM port: {vllm_port}")
        logger.info(f"Collection interval: {collect_interval}s")
        logger.info(
            f"NVIDIA GPU support: {'available' if self.nvidia_available else 'not available'}"
        )

    def _setup_otel(self):
        """Setup OpenTelemetry metrics."""
        resource = Resource.create(
            {
                "service.name": "gpu-vm-metrics",
                "service.version": "1.0.0",
                "host.name": os.uname().nodename,
                "gpu.type": self.gpu_type,
            }
        )

        exporter = OTLPMetricExporter(
            endpoint=f"http://{self.obs_otlp_endpoint}", insecure=True
        )

        reader = PeriodicExportingMetricReader(
            exporter=exporter, export_interval_millis=self.collect_interval * 1000
        )

        provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(provider)

        return metrics.get_meter("gpu-vm-metrics")

    def collect_metrics(self) -> dict[str, Any]:
        """Collect all metrics from different sources.

        Returns:
            Dict[str, Any]: Combined metrics from all sources.
        """
        all_metrics = {}

        # System metrics
        all_metrics.update(get_system_metrics())

        # GPU metrics (if available)
        if self.nvidia_available:
            all_metrics.update(get_gpu_metrics())

        # vLLM metrics
        all_metrics.update(get_vllm_metrics(self.vllm_port))

        return all_metrics

    def export_metrics(self, metrics_data: dict[str, Any]):
        """Export metrics to OpenTelemetry.

        Args:
            metrics_data: Dictionary of metric name -> value pairs.
        """
        for metric_name, value in metrics_data.items():
            if metric_name not in self.gauges:
                self.gauges[metric_name] = self.meter.create_gauge(
                    name=metric_name, description=f"Metric {metric_name}", unit="1"
                )
            self.gauges[metric_name].set(value)

    def run(self):
        """Main metrics collection loop."""
        logger.info("Starting metrics collection loop")

        while True:
            try:
                # Collect metrics
                metrics_data = self.collect_metrics()

                # Export metrics
                self.export_metrics(metrics_data)

                logger.debug(f"Exported {len(metrics_data)} metrics")

            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")

            time.sleep(self.collect_interval)


def create_exporter_from_env() -> MetricsExporter:
    """Create metrics exporter from environment variables.

    Returns:
        MetricsExporter: Configured exporter instance.
    """
    obs_otlp_endpoint = os.getenv("OBS_OTLP_ENDPOINT")
    if not obs_otlp_endpoint:
        raise ValueError("OBS_OTLP_ENDPOINT environment variable is required")

    vllm_port = int(os.getenv("VLLM_PORT", "8000"))
    collect_interval = int(os.getenv("METRICS_INTERVAL", "30"))
    gpu_type = os.getenv("GPU_TYPE", "unknown")

    return MetricsExporter(
        obs_otlp_endpoint=obs_otlp_endpoint,
        vllm_port=vllm_port,
        collect_interval=collect_interval,
        gpu_type=gpu_type,
    )


def main():
    """Main entry point."""
    try:
        exporter = create_exporter_from_env()
        exporter.run()
    except KeyboardInterrupt:
        logger.info("Metrics exporter stopped by user")
    except Exception as e:
        logger.error(f"Failed to start metrics exporter: {e}")
        raise


if __name__ == "__main__":
    main()
