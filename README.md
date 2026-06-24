# Station-Guided EO Protocol Audit

Release-safe workflow code for the station-guided Earth observation evaluation protocol described in the ACM SIGSPATIAL 2026 submission.

This repository contains scripts, schemas, synthetic examples, aggregate manifests, and figure/table builders for rebuilding the protocol logic. Source data are not included; users prepare inputs according to the schemas.

## What Is Included

- Sample and preprocessing scripts for station-year record tables.
- Train/validation/test split generation for random-record, station-year, station-isolated, and temporal-holdout masks.
- Station-year aggregation from record-level predictions.
- Metric and diagnostic scripts for Macro-F1, phenology MAE, support-density bins, and applicability summaries.
- Figure/table builders that consume aggregate manifests.
- A synthetic toy dataset that follows the public schema.

The included examples use invented `SYN_*` identifiers and synthetic grid coordinates. They are for executable schema demonstration only.

## Quick Start

```bash
python scripts/generate_synthetic_dataset.py --out-dir examples/synthetic_toy_dataset
python scripts/build_protocol_splits.py --records examples/synthetic_toy_dataset/record_predictions.csv --out-dir examples/synthetic_toy_dataset/splits
python scripts/aggregate_station_year_predictions.py --records examples/synthetic_toy_dataset/record_predictions.csv --splits examples/synthetic_toy_dataset/splits/protocol_station_isolated_seed42.csv --out aggregate_manifests/synthetic_station_year_predictions.csv
python scripts/compute_metrics.py --station-year-predictions aggregate_manifests/synthetic_station_year_predictions.csv --out aggregate_manifests/synthetic_metrics.csv
python scripts/build_diagnostics.py --records examples/synthetic_toy_dataset/record_predictions.csv --splits examples/synthetic_toy_dataset/splits/protocol_station_isolated_seed42.csv --station-year-predictions aggregate_manifests/synthetic_station_year_predictions.csv --out aggregate_manifests/synthetic_diagnostics.csv
python scripts/build_aggregate_manifest.py --metrics aggregate_manifests/synthetic_metrics.csv --diagnostics aggregate_manifests/synthetic_diagnostics.csv --out aggregate_manifests/synthetic_manifest.json
python scripts/build_figures.py --metrics aggregate_manifests/synthetic_metrics.csv --diagnostics aggregate_manifests/synthetic_diagnostics.csv --out-dir aggregate_manifests/figures
```

Or run the complete toy workflow:

```bash
python scripts/run_synthetic_demo.py
```

## Release-Safety Boundary

Scripts may be run on restricted data in a controlled local environment. Outputs should be reviewed before public release. In general, only aggregate tables at the split, model, metric, and diagnostic-bin level should be published.

Before pushing any update, run:

```bash
python scripts/release_safety_audit.py .
pytest
```

The audit checks for common accidental packaging problems such as local absolute paths, raw data folders, and non-synthetic row-level split files.

## Repository Layout

```text
configs/                  Protocol defaults for the toy workflow.
schemas/                  Public input/output schemas.
examples/                 Synthetic executable example data only.
scripts/                  Protocol, metric, diagnostic, and figure/table scripts.
aggregate_manifests/      Synthetic aggregate outputs for demonstration.
tests/                    Unit tests for split, aggregation, and safety checks.
docs/                     Data release policy and workflow notes.
paper_assets/             Paper table/figure scripts and input schemas.
```

## Citation

If you use this workflow, cite the associated ACM SIGSPATIAL paper once it is publicly available.
