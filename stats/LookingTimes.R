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
