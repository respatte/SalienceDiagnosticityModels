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

source("Routines.R")
source("geom_flat_violin.R")

# GATHER DATA ======================================================================================
fam_errors <- read.fam_errors()
contrast_trials <- read.contrast_trials()

# FAMILIARISATION ERRORS ===========================================================================
save_path <- "../results/FamErrors/"

fam_errors.plot <- ggplot(fam_errors,
                          aes(x = block,
                              y = error,
                              colour = condition,
                              fill = condition)) +
  xlab('Block') + ylab("Network error") + theme_bw() + theme(legend.position = "top") +
  facet_wrap(~salience_diff) + coord_trans(y="log") +
  stat_summary(fun.y='mean', geom='line', linetype = '61') +
  stat_summary(fun.data=mean_se, geom='ribbon', alpha= .25, colour=NA) +
  scale_color_brewer(palette = "Dark2") +
  scale_fill_brewer(palette = "Dark2")
ggsave(paste0(save_path, "Global_data.pdf"),
       fam_errors.plot,
       width = 7, height = 7.5,
       dpi = 600)

# CONTRAST TRIALS ==================================================================================
save_path <- "../results/ContrastTrials/"

contrast_trials <- contrast_trials %>%
  spread(feature, looking_time) %>%
  mutate(novelty_pref = New / (Old + New))

contrast_trials.plots <- contrast_trials %>%
  split(.$salience_diff) %>%
  lapply(function(df){
    p <- ggplot(df,
                aes(x = condition,
                    y = novelty_pref,
                    colour = condition,
                    fill = condition)) +
      theme_bw() +
      ylab(paste0("Prop Looking to New Feature, salience difference: ", first(df$salience_diff))) +
      ylim(0,1) +
      geom_hline(yintercept = .5, colour = "black", linetype = 2) +
      theme(legend.position = "none",
            axis.title.y = element_blank(),
            axis.ticks.y = element_blank(),
            axis.text.y = element_blank()) +
      coord_flip() + facet_grid(.~contrast_type) +
      geom_flat_violin(position = position_nudge(x = .2),
                       colour = "black", alpha = .5, width = .7) +
      geom_point(position = position_jitter(width = .15, height = .005),
                 size = 1, alpha = .6,
                 show.legend = F) +
      geom_boxplot(width = .1, alpha = .3, outlier.shape = NA, colour = "black",
                   show.legend = F) +
      scale_color_brewer(palette = "Dark2") +
      scale_fill_brewer(palette = "Dark2")
    ggsave(paste0(save_path, "SalienceDiff", first(df$salience_diff),"_data.pdf"), p,
           width = 5.5, height = 2.5, dpi = 600)
    return(p)
  })
