library(tidyverse)
library(future.apply)

read.fam_errors <- function(){
  res.repo <- "../results/data/"
  filenames <- list.files(path=res.repo, pattern="errors.csv")
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
    mutate(subject = parse_factor(subject),
           condition = parse_factor(condition, levels = c("no_label", "label")),
           error_type = parse_factor(error_type, levels = c("label", "salient", "non_salient")),
           z.block = scale(block, center = F))
  return(df)
}

read.contrast_trials <- function(){
  res.repo <- "../results/data/"
  filenames <- list.files(path=res.repo, pattern="contrast_")
  df <- future_lapply(seq_along(filenames),
               function(i){
                 s_ratio <- strsplit(filenames[i], "[_\\.]")[[1]][4] %>%
                   as.numeric()/10
                 tmp <- read_csv(paste0(res.repo, filenames[i])) %>%
                   mutate(subject = subject + (i-1)*48,
                          salience_ratio = s_ratio)
                 return(tmp)
               }) %>%
    bind_rows() %>%
    mutate(subject = as_factor(subject),
           condition = parse_factor(condition, levels = c("no_label", "label")),
           contrast_type = parse_factor(contrast_type, levels = c("Head", "Tail")),
           feature = as_factor(feature))
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
