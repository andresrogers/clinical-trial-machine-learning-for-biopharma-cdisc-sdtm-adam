local_lib <- file.path(getwd(), ".r_libs")
dir.create(local_lib, recursive = TRUE, showWarnings = FALSE)
local_lib <- normalizePath(local_lib, winslash = "/", mustWork = TRUE)

.libPaths(c(local_lib, .libPaths()))
Sys.setenv(R_LIBS_USER = local_lib)

message("Using local R library: ", local_lib)

required_cran <- c(
  "arrow",
  "jsonlite",
  "yaml",
  "dplyr",
  "readr",
  "tidyr",
  "stringr",
  "purrr",
  "ggplot2",
  "survival",
  "reticulate"
)

is_installed_in_lib <- function(pkg, lib) {
  suppressWarnings(requireNamespace(pkg, quietly = TRUE, lib.loc = lib))
}

install_if_missing <- function(pkgs, lib = local_lib) {
  missing <- pkgs[!vapply(pkgs, is_installed_in_lib, logical(1), lib = lib)]
  if (length(missing) > 0) {
    install.packages(
      missing,
      repos = "https://cloud.r-project.org",
      lib = lib,
      dependencies = c("Depends", "Imports")
    )
  }
}

install_if_missing(required_cran, lib = local_lib)

message("Minimal local R package setup completed.")
