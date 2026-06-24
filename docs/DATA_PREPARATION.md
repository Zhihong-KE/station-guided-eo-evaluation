# Data Preparation

Prepare station-year labels, record-level predictions, protocol split masks, and aggregate diagnostic tables according to the schemas in `schemas/` and `paper_assets/INPUT_SCHEMA.md`.

The scripts are organized in two layers:

- Core protocol layer: Python scripts under `scripts/` build split masks, aggregate record predictions to station-year support, compute metrics, and build diagnostics.
- Paper asset layer: R scripts under `paper_assets/scripts/` format prepared aggregate inputs into paper tables and figures.

The synthetic toy dataset under `examples/` is only a schema and smoke-test example.
