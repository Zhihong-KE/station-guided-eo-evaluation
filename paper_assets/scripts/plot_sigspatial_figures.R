#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(flag, default) {
  hit <- grep(paste0("^", flag, "="), args, value = TRUE)
  if (length(hit) == 0) return(default)
  sub(paste0("^", flag, "="), "", hit[[1]])
}

input_dir <- normalizePath(get_arg("--input-dir", "aggregate_manifests"), mustWork = FALSE)
out_dir <- normalizePath(get_arg("--out-dir", "outputs/figures"), mustWork = FALSE)
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(patchwork)
})

read_required <- function(name) {
  path <- file.path(input_dir, name)
  if (!file.exists(path)) stop("Missing required input: ", path, call. = FALSE)
  read_csv(path, show_col_types = FALSE)
}

read_optional <- function(name) {
  path <- file.path(input_dir, name)
  if (!file.exists(path)) return(NULL)
  read_csv(path, show_col_types = FALSE)
}

save_all <- function(plot, stem, width = 7.2, height = 4.5) {
  ggsave(file.path(out_dir, paste0(stem, ".pdf")), plot, width = width, height = height, bg = "white")
  ggsave(file.path(out_dir, paste0(stem, ".svg")), plot, width = width, height = height, bg = "white")
  ggsave(file.path(out_dir, paste0(stem, ".png")), plot, width = width, height = height, dpi = 420, bg = "white")
}

theme_metric <- function() {
  theme_classic(base_size = 10) +
    theme(
      text = element_text(family = "sans", colour = "#202020"),
      plot.title = element_text(face = "bold", size = 12),
      axis.title = element_text(face = "bold", size = 11),
      axis.text = element_text(colour = "#303030", size = 10),
      strip.background = element_rect(fill = "#F4F1EB", colour = NA),
      strip.text = element_text(face = "bold", size = 12),
      legend.position = "bottom",
      legend.title = element_blank()
    )
}

split_order <- c("random_record_seed42", "station_year_seed42", "canonical_station_isolated", "year_holdout_2020")
split_labels <- c(
  random_record_seed42 = "Random\nrecord",
  station_year_seed42 = "Station-\nyear",
  canonical_station_isolated = "Station-\nisolated",
  year_holdout_2020 = "Seen-station\n2020 holdout"
)
split_cols <- c(
  random_record_seed42 = "#C86B3C",
  station_year_seed42 = "#D4A33D",
  canonical_station_isolated = "#315F85",
  year_holdout_2020 = "#6F7F56"
)

metric_ci <- read_required("benchmark_metrics_station_year_with_ci.csv")
inst_ci <- read_required("benchmark_metrics_instance_clusterboot_with_ci.csv")
dist_ci <- read_required("distance_binned_metrics_quantile_with_ci.csv")

metric_plot_df <- metric_ci %>%
  filter(split_id %in% split_order, metric %in% c("Macro_F1", "Pheno_MAE")) %>%
  mutate(
    split_id = factor(split_id, levels = split_order),
    split_label = factor(split_labels[as.character(split_id)], levels = split_labels[split_order]),
    metric_label = recode(metric, Macro_F1 = "Macro-F1", Pheno_MAE = "Phenology MAE (days)")
  )

p_split <- ggplot(metric_plot_df, aes(split_label, estimate, colour = split_id)) +
  geom_errorbar(aes(ymin = ci_low, ymax = ci_high), width = 0.12, linewidth = 0.75) +
  geom_point(size = 3.1) +
  facet_wrap(~metric_label, scales = "free_y", nrow = 1) +
  scale_colour_manual(values = split_cols) +
  labs(title = "Split protocol benchmark", x = NULL, y = "Station-year metric") +
  theme_metric() +
  theme(legend.position = "none")

unit_df <- inst_ci %>%
  filter(metric %in% c("Macro_F1", "Pheno_MAE")) %>%
  mutate(
    unit = recode(eval_unit, instance = "Instance-level", station_year = "Station-year"),
    unit = factor(unit, levels = c("Instance-level", "Station-year")),
    metric_label = recode(metric, Macro_F1 = "Macro-F1", Pheno_MAE = "Phenology MAE (days)")
  )

p_unit <- ggplot(unit_df, aes(unit, estimate, colour = unit)) +
  geom_errorbar(aes(ymin = ci_low, ymax = ci_high), width = 0.10, linewidth = 0.75) +
  geom_point(size = 3.1) +
  facet_wrap(~metric_label, scales = "free_y", nrow = 1) +
  scale_colour_manual(values = c("Instance-level" = "#9A6B31", "Station-year" = "#315F85")) +
  labs(title = "Evaluation-unit audit", x = NULL, y = "Metric value") +
  theme_metric() +
  theme(legend.position = "none", axis.text.x = element_text(face = "bold"))

save_all(p_split / p_unit, "Fig_protocol_and_evaluation_unit_audit", 7.25, 5.0)

dist_plot_df <- dist_ci %>%
  filter(metric %in% c("Macro_F1", "Pheno_MAE")) %>%
  mutate(
    distance_bin = factor(distance_bin, levels = unique(distance_bin)),
    distance_label = paste0(as.character(distance_bin), "\nmed ",
                            round(median_nearest_train_station_km), " km\nn=", n_station_years),
    metric_label = recode(metric, Macro_F1 = "Macro-F1", Pheno_MAE = "Phenology MAE (days)")
  )

p_distance <- ggplot(dist_plot_df, aes(distance_label, estimate, group = metric_label)) +
  geom_errorbar(aes(ymin = ci_low, ymax = ci_high), width = 0.12, linewidth = 0.75, colour = "#315F85") +
  geom_point(size = 3.1, colour = "#315F85") +
  facet_wrap(~metric_label, scales = "free_y", nrow = 1) +
  labs(title = "Distance-binned spatial audit", x = "Nearest training support distance bin", y = "Metric value") +
  theme_metric()

map_points <- read_optional("station_map_points.csv")
boundary_lines <- read_optional("boundary_lines.csv")
nearest_links <- read_optional("nearest_links.csv")

if (!is.null(map_points)) {
  p_map <- ggplot() +
    {if (!is.null(boundary_lines)) geom_path(data = boundary_lines, aes(x, y, group = part_id),
                                            colour = "#D8D8D8", linewidth = 0.15, alpha = 0.75)} +
    {if (!is.null(nearest_links)) geom_segment(data = nearest_links, aes(x = x, y = y, xend = xend, yend = yend),
                                              colour = "#8C8C8C", linewidth = 0.25, alpha = 0.75)} +
    geom_point(data = map_points, aes(x, y, fill = distance_bin), shape = 21,
               colour = "#202020", size = 1.8, stroke = 0.25) +
    coord_equal() +
    labs(title = "Station-support map", x = NULL, y = NULL) +
    theme_void(base_size = 10) +
    theme(plot.title = element_text(face = "bold", size = 12), legend.position = "bottom")
  save_all(p_map | p_distance, "Fig_distance_binned_spatial_generalization_audit", 7.25, 3.8)
} else {
  save_all(p_distance, "Fig_distance_binned_spatial_generalization_audit", 7.25, 3.2)
}

message("Wrote SIGSPATIAL figure assets to: ", out_dir)
