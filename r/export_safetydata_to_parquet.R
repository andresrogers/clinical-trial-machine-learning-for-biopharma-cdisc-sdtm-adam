args <- commandArgs(trailingOnly = TRUE)
input_dir <- args[[1]]
output_dir <- args[[2]]

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
dir.create("artifacts/qc", recursive = TRUE, showWarnings = FALSE)

library(reticulate)

pd <- import("pandas")

files <- list.files(input_dir, pattern = "\\.rda$", full.names = TRUE)

log_rows <- list()

sanitize_temporal_columns <- function(df) {
  out <- df
  for (col_name in names(out)) {
    col <- out[[col_name]]
    if (inherits(col, "Date") || inherits(col, "POSIXct") || inherits(col, "POSIXlt")) {
      out[[col_name]] <- as.character(col)
    }
  }
  out
}

for (file in files) {
  env <- new.env(parent = emptyenv())
  load(file, envir = env)
  object_names <- ls(env)

  for (obj_name in object_names) {
    status <- "exported"
    error_message <- ""
    n_rows <- NA_integer_
    out_file <- file.path(output_dir, paste0(tolower(obj_name), ".parquet"))

    tryCatch({
      obj <- get(obj_name, envir = env)
      if (!is.data.frame(obj)) {
        obj <- as.data.frame(obj)
      }

      obj <- sanitize_temporal_columns(obj)
      n_rows <- nrow(obj)

      py_df <- r_to_py(obj)
      py_df$to_parquet(out_file, index = FALSE)
    }, error = function(e) {
      status <<- "failed"
      error_message <<- conditionMessage(e)
    })

    log_rows[[length(log_rows) + 1]] <- data.frame(
      source_file = basename(file),
      object_name = obj_name,
      output_file = basename(out_file),
      n_rows = n_rows,
      status = status,
      error_message = error_message,
      stringsAsFactors = FALSE
    )
  }
}

if (length(log_rows) > 0) {
  export_log <- do.call(rbind, log_rows)
  write.csv(export_log, "artifacts/qc/safetydata_rda_export_log.csv", row.names = FALSE)

  successful <- sum(export_log$status == "exported")
  if (successful == 0) {
    stop("No safetydata .rda objects were successfully exported to parquet")
  }
}
