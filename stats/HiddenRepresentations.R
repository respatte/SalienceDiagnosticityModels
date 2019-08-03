# LIBRARY IMPORTS ==================================================================================
library(lme4)
library(lmerTest)
library(emmeans)
library(brms)
library(coda)
library(modeest)
library(tidyverse)
library(sjPlot)
library(RColorBrewer)
library(future.apply)
plan(multiprocess)

source("Routines.R")
source("geom_flat_violin.R")

# GATHER DATA ======================================================================================
hidden_reps <- read.fam_hidden_reps()

# PLOT: PCA ========================================================================================
hidden_reps.pca <- hidden_reps %>%
  subset(block == 1 | block == 20000) %>%
  mutate(block = parse_factor(ifelse(block == 1, "first", "last"))) %>%
  split(list(.$subject,.$block)) %>%
  future_lapply(function(df){
    A1 <- which(df$stim_type == "A1")
    pca_dims <- prcomp(~ dim0 + dim1 + dim2 + dim3 + dim4 + dim5,
                     data = df, rank. = 2)$x
    # Signs are random in PCAs, setting the average A1 item to both positives
    # This way, if there's a structure across participants, it will be seen
    if(mean(pca_dims[A1,1]) < 0){pca_dims[,1] <- -pca_dims[,1]}
    if(mean(pca_dims[A1,2]) < 0){pca_dims[,2] <- -pca_dims[,2]}
    return(bind_cols(df, as_tibble(pca_dims)))
  }) %>%
  bind_rows()

hidden_reps.pca.first.plot <- hidden_reps.pca %>%
  subset(block == "first") %>%
  ggplot(aes(x = PC1,
             y = PC2,
             colour = stim_type)) +
  facet_wrap(~salience_ratio) +
  geom_point(alpha = .5) +
  scale_colour_brewer(palette = "Dark2")

hidden_reps.pca.last.plot <- hidden_reps.pca %>%
  subset(block == "last") %>%
  ggplot(aes(x = PC1,
             y = PC2,
             colour = stim_type)) +
  facet_wrap(~salience_ratio) +
  geom_point(alpha = .5) +
  scale_colour_brewer(palette = "Dark2")
