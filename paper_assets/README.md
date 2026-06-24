# Paper Asset Scripts

This directory contains scripts and input schemas for rebuilding the paper figures and tables from prepared aggregate inputs.

The repository does not include source data. Users should prepare their own station-year records, split masks, model predictions, distance-bin summaries, and optional map layers according to `INPUT_SCHEMA.md`, then run the scripts.

## Scripts

- `scripts/build_sigspatial_tables.R`: builds paper-ready CSV/Markdown/LaTeX tables from aggregate metric and split-composition inputs.
- `scripts/plot_sigspatial_figures.R`: rebuilds the paper figure set from prepared figure inputs.

## Minimal Workflow

```bash
Rscript paper_assets/scripts/build_sigspatial_tables.R --input-dir path/to/prepared_inputs --out-dir outputs/tables
Rscript paper_assets/scripts/plot_sigspatial_figures.R --input-dir path/to/prepared_inputs --out-dir outputs/figures
```

The Python scripts in the repository root can produce the core split, aggregation, metric, and diagnostic tables. The paper-asset scripts are the publication formatting layer.
