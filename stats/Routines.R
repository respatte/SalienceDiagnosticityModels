library(tidyverse)

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
