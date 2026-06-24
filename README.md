# Support-Aware Evaluation for Station-Guided Earth Observation

Station-guided Earth observation studies often use sparse in-situ observations as labels for dense satellite records. This creates a subtle evaluation problem: one station-year label may supervise many satellite records, so the split unit, label support, record support, aggregation unit, metric population, and deployment claim can refer to different things.

This repository accompanies a study of that problem. The central question is not how to train a stronger crop-phenology model, but how to decide what an evaluation score can legitimately claim when sparse station labels are expanded into dense EO records.

The project shows that random-record evaluation can substantially overstate spatial generalization, and that station holdout is necessary but not sufficient. Reliable unseen-location claims require support-aware reporting: the split design, label support, record support, station-year aggregation, metric population, support exposure, support density, and applicability diagnostics should be reported together.

## Scientific Problem

Sparse station observations and dense EO records live at different supports. When a station-year label is expanded into many satellite records, the training and test masks can separate records while still exposing the same station-year, the same station in other years, or dense local support conditions. A score can therefore look strong while answering a weaker question than unseen-location generalization.

## Why It Matters

Many EO and GeoAI studies report spatial generalization or unseen-location performance. If the split unit, label support, record support, aggregation unit, and metric population are not aligned, the reported score may measure record interpolation or dense-buffer weighting rather than performance at new stations. This affects how model accuracy, deployment claims, and benchmark comparisons should be interpreted.

## Repository Scope

This repository provides a release-safe, reproducible companion workflow for rebuilding the evaluation logic on synthetic examples and prepared aggregate inputs. It does not include source station observations, real station identifiers, coordinates, raw satellite records, or row-level real split files.

## What Is Included

- Sample and preprocessing scripts for station-year record tables.
- Train/validation/test split generation for random-record, station-year, station-isolated, and temporal-holdout masks.
- Station-year aggregation from record-level predictions.
- Metric and diagnostic scripts for Macro-F1, phenology MAE, support-density bins, and applicability summaries.
- Figure/table builders that consume prepared aggregate inputs.
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
docs/                     Data preparation and workflow notes.
paper_assets/             Paper table/figure scripts and input schemas.
```

## Citation

If you use this workflow, cite the associated paper once it is publicly available.
