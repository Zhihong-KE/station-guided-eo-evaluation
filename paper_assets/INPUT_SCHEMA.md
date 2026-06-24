# Paper Asset Input Schema

The figure and table scripts expect prepared aggregate inputs. File names below are defaults and can be overridden by editing the script arguments.

## Required Tables

### `benchmark_metrics_station_year_with_ci.csv`

One row per split and metric.

Required columns:

- `split_id`
- `metric`: `Macro_F1` or `Pheno_MAE`
- `estimate`
- `ci_low`
- `ci_high`

### `benchmark_metrics_instance_clusterboot_with_ci.csv`

One row per evaluation unit and metric.

Required columns:

- `eval_unit`: `instance` or `station_year`
- `metric`: `Macro_F1` or `Pheno_MAE`
- `estimate`
- `ci_low`
- `ci_high`

### `distance_binned_metrics_quantile_with_ci.csv`

One row per distance bin and metric.

Required columns:

- `distance_bin`
- `median_nearest_train_station_km`
- `n_station_years`
- `metric`: `Macro_F1` or `Pheno_MAE`
- `estimate`
- `ci_low`
- `ci_high`

### `split_composition_summary_for_paper.csv`

One row per split.

Required columns:

- `split_id`
- `test_stations`
- `test_station_years`
- `station_overlap_train_test`
- `station_year_overlap_train_test`
- `test_years`

## Optional Figure Inputs

### `station_map_points.csv`

Used only when rebuilding map panels.

Required columns:

- `x`
- `y`
- `role`: `all`, `train`, or `test`
- `distance_bin`

### `nearest_links.csv`

Optional links between test and nearest training supports.

Required columns:

- `x`
- `y`
- `xend`
- `yend`
- `distance_bin`

### `boundary_lines.csv`

Optional map boundary layer.

Required columns:

- `layer`
- `part_id`
- `x`
- `y`

## Split IDs

Default script labels expect:

- `random_record_seed42`
- `station_year_seed42`
- `canonical_station_isolated`
- `year_holdout_2020`

Different names are allowed if the label dictionary in the plotting script is updated.
