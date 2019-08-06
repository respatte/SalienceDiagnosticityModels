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
    A <- which(df$tail_type == "A")
    pca_dims <- prcomp(~ dim0 + dim1 + dim2 + dim3 + dim4 + dim5,
                     data = df, rank. = 2)$x
    # Signs are random in PCAs, setting the average A item to both positives
    # This way, if there's a structure across participants, it will be seen
    if(mean(pca_dims[A,1]) < 0){pca_dims[,1] <- -pca_dims[,1]}
    if(mean(pca_dims[A,2]) < 0){pca_dims[,2] <- -pca_dims[,2]}
    return(bind_cols(df, as_tibble(pca_dims)))
  }) %>%
  bind_rows()

hidden_reps.pca.first.plot <- hidden_reps.pca %>%
  subset(block == "first") %>%
  ggplot(aes(x = PC1,
             y = PC2,
             colour = tail_type)) +
  theme(legend.position = "top") +
  facet_wrap(~salience_ratio+condition, ncol = 6) +
  geom_point(alpha = .5) +
  scale_colour_brewer(palette = "Dark2")

hidden_reps.pca.last.plot <- hidden_reps.pca %>%
  subset(block == "last") %>%
  ggplot(aes(x = PC1,
             y = PC2,
             colour = tail_type)) +
  theme(legend.position = "top") +
  facet_wrap(~salience_ratio+condition, ncol = 6) +
  geom_point(alpha = .5) +
  scale_colour_brewer(palette = "Dark2")

# DISTANCES ========================================================================================
hidden_reps.distances <- hidden_reps %>%
  group_by(subject, condition, block, tail_type, salience_ratio) %>%
  summarise(absolute_dist = dist.hidden_reps(list(dim0,dim1,dim2,dim3,dim4,dim5)),
            mu_dim0 = mean(dim0),
            mu_dim1 = mean(dim1),
            mu_dim2 = mean(dim2),
            mu_dim3 = mean(dim3),
            mu_dim4 = mean(dim4),
            mu_dim5 = mean(dim5)) %>%
  group_by(subject, condition, block, salience_ratio) %>%
  mutate(between_dist = dist.hidden_reps(list(mu_dim0,mu_dim1,mu_dim2,mu_dim3,mu_dim4,mu_dim5))) %>%
  select(-c(mu_dim0,mu_dim1,mu_dim2,mu_dim3,mu_dim4,mu_dim5)) %>%
  ungroup() %>%
  mutate(relative_dist = absolute_dist/between_dist)
