library(tidyverse)
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
                      }) %>%
    bind_rows() %>%
    separate(stim_type, c("tail_type", "head_type"), 1) %>%
    mutate_at(c("subject", "condition", "tail_type", "head_type"), parse_factor, levels = NULL)
  return(df)
}

dist.hidden_reps <- function(items){
  # items must be a list of dimensions from the hidden_reps dataframe
  # Take each item as a row in a matrix, compute the distances between items, take the mean
  return(simplify2array(items) %>% dist() %>% mean())
}
