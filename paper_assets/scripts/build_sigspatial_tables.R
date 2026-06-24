#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default) {
  hit <- grep(paste0("^", flag, "="), args, value = TRUE)
  if (length(hit) == 0) return(default)
  sub(paste0("^", flag, "="), "", hit[[1]])
}

input_dir <- normalizePath(get_arg("--input-dir", "aggregate_manifests"), mustWork = FALSE)
out_dir <- normalizePath(get_arg("--out-dir", "outputs/tables"), mustWork = FALSE)
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(file.path(out_dir, "appendix"), recursive = TRUE, showWarnings = FALSE)

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
  library(knitr)
})

read_required <- function(name) {
  path <- file.path(input_dir, name)
  if (!file.exists(path)) stop("Missing required input: ", path, call. = FALSE)
  read_csv(path, show_col_types = FALSE)
}

write_bundle <- function(df, stem, caption, dir = out_dir) {
  dir.create(dir, recursive = TRUE, showWarnings = FALSE)
  write_csv(df, file.path(dir, paste0(stem, ".csv")))
  writeLines(c(paste0("<!-- ", caption, " -->"), "", knitr::kable(df, format = "pipe")),
             file.path(dir, paste0(stem, ".md")), useBytes = TRUE)
  writeLines(knitr::kable(df, format = "latex", booktabs = TRUE, caption = caption),
             file.path(dir, paste0(stem, ".tex")), useBytes = TRUE)
}

split_order <- c("random_record_seed42", "station_year_seed42", "canonical_station_isolated", "year_holdout_2020")
split_names <- c(
  random_record_seed42 = "random-record",
  station_year_seed42 = "station-year",
  canonical_station_isolated = "station-isolated",
  year_holdout_2020 = "seen-station 2020 holdout"
)
targets <- c(
  random_record_seed42 = "record interpolation",
  station_year_seed42 = "same-network generalization",
  canonical_station_isolated = "unseen-location generalization",
  year_holdout_2020 = "future-year at observed stations"
)
interpretations <- c(
  random_record_seed42 = "optimistic / leakage-prone",
  station_year_seed42 = "same-station exposure",
  canonical_station_isolated = "canonical spatial holdout",
  year_holdout_2020 = "temporal, not unseen-location"
)

metric_ci <- read_required("benchmark_metrics_station_year_with_ci.csv")
split_comp <- read_required("split_composition_summary_for_paper.csv") %>%
  filter(split_id %in% split_order) %>%
  mutate(split_id = factor(split_id, levels = split_order),
         split = split_names[as.character(split_id)]) %>%
  arrange(split_id)

table1 <- split_comp %>%
  transmute(
    Split = split,
    `Test stations` = test_stations,
    `Test station-years` = test_station_years,
    `Train-test station overlap` = station_overlap_train_test,
    `Train-test station-year overlap` = station_year_overlap_train_test,
    `Generalization target` = targets[as.character(split_id)]
  )
write_bundle(table1, "Table1_split_composition", "Split composition and generalization targets.")

table2 <- metric_ci %>%
  filter(split_id %in% split_order, metric %in% c("Macro_F1", "Pheno_MAE")) %>%
  mutate(
    split_id = factor(split_id, levels = split_order),
    value_ci = if_else(
      metric == "Macro_F1",
      sprintf("%.3f [%.3f, %.3f]", estimate, ci_low, ci_high),
      sprintf("%.2f [%.2f, %.2f]", estimate, ci_low, ci_high)
    )
  ) %>%
  select(split_id, metric, value_ci) %>%
  pivot_wider(names_from = metric, values_from = value_ci) %>%
  arrange(split_id) %>%
  mutate(
    Split = split_names[as.character(split_id)],
    Recommendation = interpretations[as.character(split_id)]
  ) %>%
  transmute(Split, `Macro-F1 (95% CI)` = Macro_F1,
            `Pheno MAE days (95% CI)` = Pheno_MAE, Recommendation)
write_bundle(table2, "Table2_main_metrics_recommendations", "Main station-year results and interpretation.")

protocol_defs <- tibble::tribble(
  ~`Protocol / metric`, ~Unit, ~`Train-test station overlap`, ~`Generalization target`, ~`Main risk`,
  "random-record", "record", "yes", "record interpolation", "same station-year records can cross train/test",
  "station-year", "station-year", "yes", "same-network generalization", "same-station cross-year exposure",
  "station-isolated", "station", "no", "unseen-location generalization", "strict spatial transfer baseline",
  "seen-station 2020 holdout", "year", "yes", "future-year at observed stations", "not unseen-location testing",
  "instance-level metric", "pixel / record", "n/a", "dense observation accuracy", "dense-buffer weighting bias",
  "station-year metric", "station-year", "n/a", "station-year task accuracy", "preferred primary metric",
  "distance-bin audit", "station distance", "n/a", "spatial distance sensitivity", "bin sample size"
)
write_bundle(protocol_defs, "TableS_protocol_definitions", "Protocol definitions and evaluation risks.",
             file.path(out_dir, "appendix"))

message("Wrote SIGSPATIAL table assets to: ", out_dir)
