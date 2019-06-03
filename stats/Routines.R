library(tidyverse)

read.fam_errors <- function(){
  single.file.import <- function(filename, i){
    tmp <- read_csv(filename) %>%
      mutate(subject = subject + (i-1)*48,
             salience_diff = strsplit(filename, "_")[[1]][2])
  }
  res.repo <- "../results/data/"
  filenames <- list.files(path=res.repo, pattern="errors.csv")
  df <- lapply(seq_along(filenames),
               function(i){
                 tmp <- read_csv(paste0(res.repo, filenames[i])) %>%
                   mutate(subject = subject + (i-1)*48,
                          salience_diff = strsplit(filenames[i], "_")[[1]][2])
                 return(tmp)
               }) %>%
    bind_rows()
  return(df)
}