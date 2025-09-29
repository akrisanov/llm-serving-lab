#!/usr/bin/env python3
"""
CLI script for local development and testing of the metrics exporter.
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path for local development
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def main():
    parser = argparse.ArgumentParser(description="LLM Serving Lab Metrics Exporter")
    parser.add_argument(
        "--obs-endpoint",
        help="OBS OTLP endpoint (default: from OBS_OTLP_ENDPOINT env var)",
    )
    parser.add_argument(
        "--vllm-port", type=int, default=8000, help="vLLM server port (default: 8000)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Collection interval in seconds (default: 30)",
    )
    parser.add_argument(
        "--gpu-type",
        default="development",
        help="GPU type identifier (default: development)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Collect metrics once and print, don't start continuous export",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Setup logging
    import logging

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Configure environment
    if args.obs_endpoint:
        os.environ["OBS_OTLP_ENDPOINT"] = args.obs_endpoint
    os.environ["VLLM_PORT"] = str(args.vllm_port)
    os.environ["METRICS_INTERVAL"] = str(args.interval)
    os.environ["GPU_TYPE"] = args.gpu_type

    try:
        # Import here to avoid issues with sys.path manipulation
        from monitoring.metrics_exporter import create_exporter_from_env

        if args.dry_run:
            # Dry run mode - collect metrics once and print
            print("=== Dry run mode - collecting metrics once ===")

            if not args.obs_endpoint and not os.getenv("OBS_OTLP_ENDPOINT"):
                # For dry run, we can use a dummy endpoint
                os.environ["OBS_OTLP_ENDPOINT"] = "dummy:4317"

            exporter = create_exporter_from_env()
            metrics = exporter.collect_metrics()

            print(f"\nCollected {len(metrics)} metrics:")
            for name, value in sorted(metrics.items()):
                print(f"  {name}: {value}")

            print("\n=== Dry run completed ===")
        else:
            # Normal mode - continuous export
            if not args.obs_endpoint and not os.getenv("OBS_OTLP_ENDPOINT"):
                print("Error: OBS_OTLP_ENDPOINT is required for normal mode")
                print(
                    "Use --obs-endpoint or set OBS_OTLP_ENDPOINT environment variable"
                )
                sys.exit(1)

            exporter = create_exporter_from_env()
            exporter.run()

    except KeyboardInterrupt:
        print("\nMetrics exporter stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
