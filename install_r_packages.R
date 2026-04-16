required_cran <- c(
  "pak",
  "jsonlite",
  "yaml",
  "arrow",
  "dplyr",
  "readr",
  "tidyr",
  "stringr",
  "purrr",
  "ggplot2",
  "survival",
  "gt",
  "gtsummary",
  "targets",
  "reticulate",
  "rmarkdown"
)

install_if_missing <- function(pkgs) {
  missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]
  if (length(missing) > 0) install.packages(missing, repos = "https://cloud.r-project.org")
}

install_if_missing(required_cran)

if (!requireNamespace("pak", quietly = TRUE)) {
  install.packages("pak", repos = "https://cloud.r-project.org")
}

# Prefer GitHub for the thin hybrid standards layer because package availability can vary.
github_pkgs <- c(
  "pharmaverse/admiral",
  "pharmaverse/sdtm.oak",
  "atorus-research/metacore",
  "atorus-research/xportr"
)

try({
  pak::pkg_install(github_pkgs)
}, silent = TRUE)

message("R package setup attempted. Review any package-specific install messages.")
