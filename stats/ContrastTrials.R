# LIBRARY IMPORTS ==================================================================================
library(lme4)
library(lmerTest)
library(emmeans)
library(brms)
library(coda)
library(modeest)
library(tidyverse)
library(ggeffects)
library(sjPlot)
library(RColorBrewer)
library(scales)

source("Routines.R")
source("geom_flat_violin.R")

# GATHER DATA ======================================================================================
contrast_trials <- read.contrast_trials()

# CONTRAST TRIALS ==================================================================================
save_path <- "../results/ContrastTrials/"

# Prepare data
chance <- asin(sqrt(.5))
contrast_trials.old_new <- contrast_trials %>%
  spread(feature, looking_time) %>%
  mutate(novelty_pref = (New / (Old + New)) %>% sqrt() %>% asin() - chance)

# Run models
run_models <- F
if(run_models){
  ## Run STB model
  contrast_trials.old_new.lmer <- lmer(novelty_pref ~ salience_ratio*contrast_type*condition +
                                         (1 | subject),
                                       data = contrast_trials.old_new)
  contrast_trials.old_new.anova <- anova(contrast_trials.old_new.lmer, type = "I")
  contrast_trials.old_new.emmeans <- ggpredict(contrast_trials.old_new.lmer,
                                               terms = c("condition",
                                                         "contrast_type",
                                                         "salience_ratio [all]"),
                                               type = "fe",
                                               x.as.factor = T) %>%
    rename(condition = x,
           contrast_type = group,
           salience_ratio = facet) %>%
    mutate(salience_ratio = as.numeric(as.character(salience_ratio)))
  ## Save results
  saveRDS(contrast_trials.old_new.lmer, paste0(save_path, "OldNew_lmer.rds"))
  saveRDS(contrast_trials.old_new.anova, paste0(save_path, "OldNew_anova.rds"))
  saveRDS(contrast_trials.old_new.emmeans, paste0(save_path, "OldNew_emmeans.rds"))
}else{
  ## Read results
  contrast_trials.old_new.lmer <- readRDS(paste0(save_path, "OldNew_lmer.rds"))
  contrast_trials.old_new.anova <- readRDS(paste0(save_path, "OldNew_anova.rds"))
  contrast_trials.old_new.emmeans <- readRDS(paste0(save_path, "OldNew_emmeans.rds"))
}

# Plot
generate_plots <- F
if(generate_plots){
  ## Prepare labeller
  contrast_type_labels <- c(Tail = "Tail (diagnostic)", Head = "Head (salient)")
  ## Plot for small/medium/high salience difference ratios by condition and contrast_type
  contrast_trials.old_new.plot <- contrast_trials.old_new %>%
    subset(salience_ratio %in% c(.2, .5, .8)) %>%
    mutate(salience_ratio = as_factor(salience_ratio)) %>%
    ggplot(aes(x = condition,
               y = sin(novelty_pref)^2,
               colour = condition,
               fill = condition)) +
    theme_bw() +
    ylab("Prop Looking to New Feature") + #ylim(0,1) +
    geom_hline(yintercept = 0, colour = "black", linetype = 2) +
    theme(legend.position = "top",
          axis.title.y = element_blank(),
          axis.ticks.y = element_blank(),
          axis.text.y = element_blank(),
          axis.text.x = element_text(angle=45, vjust=1, hjust=1)) +
    coord_flip() +
    facet_grid(rows = vars(contrast_type),
               cols = vars(salience_ratio),
               labeller = labeller(contrast_type = contrast_type_labels)) +
    geom_flat_violin(position = position_nudge(x = .2),
                     colour = "black", alpha = .5, width = .7) +
    geom_point(position = position_jitter(width = .15, height = .005),
               size = 1, alpha = .6,
               show.legend = F) +
    geom_boxplot(width = .1, alpha = .3, outlier.shape = NA, colour = "black",
                 show.legend = F) +
    scale_y_continuous(breaks = c(0.50,0.51)) +
    scale_color_brewer(palette = "Dark2",
                       name = "Condition",
                       labels = c("no-label", "label")) +
    scale_fill_brewer(palette = "Dark2",
                      name = "Condition",
                      labels = c("no-label", "label"))
  ggsave(paste0(save_path, "OldNew_data.pdf"),
         contrast_trials.old_new.plot,
         width = 5, height = 4, dpi = 600)
  ## Plot marginal means with CIs
  contrast_trials.old_new.emmeans.plot <- contrast_trials.old_new.emmeans %>%
    ggplot(aes(x = salience_ratio,
               y = predicted,
               ymin = conf.low,
               ymax = conf.high,
               colour = condition,
               fill = condition)) +
    theme_bw() + ylab("Prop Looking to New Feature") + xlab("Salience Ratio") +
    theme(legend.position = "top") +
    facet_wrap(vars(contrast_type),
               labeller = labeller(contrast_type = contrast_type_labels)) +
    geom_ribbon(alpha = .6, colour = NA) +
    geom_line() +
    geom_hline(yintercept = 0, colour = "black", linetype = 2, alpha = .5) +
    scale_colour_brewer(palette = "Dark2",
                        name = "Condition",
                        labels = c("no-label", "label")) +
    scale_fill_brewer(palette = "Dark2",
                      name = "Condition",
                      labels = c("no-label", "label")) +
    scale_x_continuous(breaks = c(.2, .5, .8),
                       minor_breaks = c(.1, .3, .4, .6, .7, .9))
  ggsave(paste0(save_path, "OldNew_emmeans.pdf"),
                contrast_trials.old_new.emmeans.plot,
                width = 5, height = 3, dpi = 600)
}
