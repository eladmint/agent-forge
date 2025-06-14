# Metrics and Monitoring

This directory contains configuration files and data related to monitoring and metrics for the TokenHunter project.

## Directory Structure

- `configs/`: Contains configuration files for monitoring alerts and baselines
  - `high_error_rate_alert.json`: Configuration for high error rate alert
  - `high_latency_alert.json`: Configuration for high latency alert
  - `low_traffic_alert.json`: Configuration for low traffic alert
  - `request_latency_baseline.json`: Baseline configuration for request latency

- `metrics_data_20250524/`: Contains metrics data exported on May 24, 2025

## Alert Configurations

The alert configurations can be applied using the Google Cloud Monitoring API or through the Google Cloud Console.

## Documentation

For more details on monitoring and metrics, see:
- `memory-bank/monitoring_implementation.md`
- `memory-bank/adrs/ADR-018-Monitoring-Observability-Implementation.md`
- `memory-bank/adrs/ADR-021-Monitoring-Fine-Tuning.md` 