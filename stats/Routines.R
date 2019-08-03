library(tidyverse)
library(sjstats)
library(future.apply)

read.fam_errors <- function(){
  res.repo <- "../results/data/"
  filenames <- list.files(path=res.repo, pattern="errors.csv")
  df <- lapply(seq_along(filenames),
               function(i){
                 s_ratio <- strsplit(filenames[i], "_")[[1]][2] %>%
                   as.numeric()/10
                 tmp <- read_csv(paste0(res.repo, filenames[i])) %>%
                   mutate(subject = subject + (i-1)*48,
                          salience_ratio = s_ratio)
                 return(tmp)
               }) %>%
    bind_rows()
  return(df)
}

read.fam_hidden_reps <- function(){
  plan(multiprocess)
  res.repo <- "../results/data/"
  filenames <- list.files(path=res.repo, pattern="hidden_reps.csv")
  df <- future_lapply(seq_along(filenames),
               function(i){
                 s_ratio <- strsplit(filenames[i], "_")[[1]][2] %>%
                   as.numeric()/10
                 tmp <- read_csv(paste0(res.repo, filenames[i])) %>%
                   mutate(subject = as.character(subject + (i-1)*48),
                          salience_ratio = s_ratio)
                 return(tmp)
               })
    bind_rows() %>%
    mutate_at(c("subject", "condition", "stim_type"), parse_factor, levels = NULL) %>%
    mutate_at("stim_type", fct_relevel, "A1", "A2", "B1", "B2")
  return(df)
}

read.contrast_trials <- function(){
  res.repo <- "../results/data/"
  filenames <- list.files(path=res.repo, pattern="contrast_")
  df <- lapply(seq_along(filenames),
               function(i){
                 s_ratio <- strsplit(filenames[i], "_")[[1]][4] %>%
                   as.numeric()/10
                 tmp <- read_csv(paste0(res.repo, filenames[i])) %>%
                   mutate(subject = subject + (i-1)*48,
                          salience_ratio = s_ratio)
                 return(tmp)
               }) %>%
    bind_rows()
  return(df)
}
