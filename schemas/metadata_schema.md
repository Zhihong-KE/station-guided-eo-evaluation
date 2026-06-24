# Public Schema

The public schema uses generic station-year support keys. Public example files must use synthetic identifiers only.

## `station_year_labels.csv`

| column | type | description |
|---|---|---|
| `station_id` | string | Synthetic or local-private station support key. Public examples use `SYN_ST###`. |
| `station_year_id` | string | Synthetic or local-private station-year support key. |
| `year` | integer | Observation year. |
| `crop_label` | string | Crop class label. |
| `sowing_doy` | integer | Day-of-year sowing target. |
| `maturity_doy` | integer | Day-of-year maturity target. |
| `synthetic_x` | float | Synthetic grid coordinate for public examples. Do not use longitude. |
| `synthetic_y` | float | Synthetic grid coordinate for public examples. Do not use latitude. |

## `record_predictions.csv`

| column | type | description |
|---|---|---|
| `record_id` | string | Record-level support key. Public examples use `SYN_REC####`. |
| `station_id` | string | Station support key. |
| `station_year_id` | string | Station-year support key. |
| `year` | integer | Observation year. |
| `crop_label` | string | Ground-truth crop label for local evaluation. Do not publish real row-level labels. |
| `sowing_doy` | integer | Ground-truth sowing target. Do not publish real row-level labels. |
| `maturity_doy` | integer | Ground-truth maturity target. Do not publish real row-level labels. |
| `crop_pred` | string | Record-level predicted crop class. |
| `sowing_pred` | float | Record-level predicted sowing DOY. |
| `maturity_pred` | float | Record-level predicted maturity DOY. |
| `synthetic_x` | float | Synthetic grid coordinate for public examples. |
| `synthetic_y` | float | Synthetic grid coordinate for public examples. |

## `protocol_*.csv`

| column | type | description |
|---|---|---|
| `record_id` | string | Record key. |
| `station_id` | string | Station support key. |
| `station_year_id` | string | Station-year support key. |
| `year` | integer | Observation year. |
| `split` | string | One of `train`, `validation`, or `test`. |
| `protocol` | string | Split mask name. |

Real split files are private because they can reveal station identities or deployment partitions.
