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
fam_errors <- read.fam_errors()

# FAMILIARISATION ERRORS ===========================================================================
save_path <- "../results/FamErrors/"

# Prepare data
fam_errors.visual <- fam_errors %>%
  subset(error_type != "label") %>%
  droplevels()

# Run models
run_models <- T
if(run_models){
  ## Run STB model
  fam_errors.visual.lmer <- lmer(error ~ z.block*condition*error_type*salience_ratio +
                                       (z.block*error_type | subject),
                                     data = fam_errors.visual,
                                     control = lmerControl(optCtrl = list(maxfun=100000)))
  fam_errors.visual.anova <- anova(fam_errors.visual.lmer, type = "I")
  ## Save results
  saveRDS(fam_errors.visual.lmer, paste0(save_path, "VisualFeatures_lmer.rds"))
  saveRDS(fam_errors.visual.anova, paste0(save_path, "VisualFeatures_anova.rds"))
}else{
  ## Read results
  fam_errors.visual.lmer <- readRDS(paste0(save_path, "VisualFeatures_lmer.rds"))
  fam_errors.visual.anova <- readRDS(paste0(save_path, "VisualFeatures_anova.rds"))
}

# Plot
generate_plots <- T
if(generate_plots){
  ## Prepare labeller
  error_type_labels <- c(non_salient = "Tail (diagnostic)", salient = "Head (salient)")
  ## Plot for small/medium/high salience difference ratios by condition and error_type
  fam_errors.visual.plot <- fam_errors.visual %>%
    mutate_at("salience_ratio", as.character) %>%
    mutate_at("salience_ratio", parse_factor) %>%
    subset(salience_ratio %in% c("0.2", "0.5", "0.8")) %>%
    droplevels() %>%
    ggplot(aes(x = block,
               y = error,
               colour = condition,
               fill = condition)) +
    xlab('Block') + ylab("Network error") + theme_bw() +
    theme(legend.position = "top",
          axis.text.x = element_text(angle=45, vjust=1, hjust = 1)) +
    facet_grid(rows = vars(error_type),
               cols = vars(salience_ratio),
               labeller = labeller(error_type = error_type_labels)) +
    scale_x_continuous(trans = log10_trans()) +
    scale_y_continuous(trans = log10_trans()) +
    stat_summary(fun.y='mean', geom='line', linetype = '61') +
    stat_summary(fun.data=mean_se, geom='ribbon', alpha= .25, colour=NA) +
    scale_colour_brewer(palette = "Dark2",
                        name = "Condition",
                        labels = c("no-label", "label")) +
    scale_fill_brewer(palette = "Dark2",
                      name = "Condition",
                      labels = c("no-label", "label"))
  ggsave(paste0(save_path, "VisualFeatures_data.pdf"),
         fam_errors.visual.plot,
         width = 5, height = 3.5,
         dpi = 600)
  ## Plot marginal effects per condition:error_type:salience_ratio
  ### Prepare data
  fam_errors.visual.marginal_effects <- fam_errors.visual.lmer %>%
    ggpredict(terms = c("z.block",
                        "condition",
                        "error_type",
                        "salience_ratio [.2, .5, .8]"),
              type = "fe") %>%
    rename(z.block = x,
           condition = group,
           error_type = facet,
           salience_ratio = panel)
  ### Plot data
  fam_errors.visual.marginal_effects.plot <- fam_errors.visual.marginal_effects %>%
    ggplot(aes(x = z.block,
               y = predicted,
               ymin = conf.low,
               ymax = conf.high,
               colour = condition,
               fill = condition)) +
    ylab("Network Error") + xlab("Scaled Block") + theme_bw() +
    facet_grid(rows = vars(error_type),
               cols = vars(salience_ratio),
               labeller = labeller(error_type = error_type_labels),
               scales = "free_y") +
    theme(legend.position = "top",
          axis.ticks.x = element_blank(),
          axis.text.x = element_blank()) +
    geom_line(size = .3) +
    geom_ribbon(alpha = .5, colour = NA) +
    scale_colour_brewer(palette = "Dark2",
                        name = "Condition",
                        labels = c("no-label", "label")) +
    scale_fill_brewer(palette = "Dark2",
                      name = "Condition",
                      labels = c("no-label", "label"))
  ggsave(paste0(save_path, "VisualFeatures_MarginalEffects.pdf"),
         fam_errors.visual.marginal_effects.plot,
         width = 5, height = 3.5,
         dpi = 600)
}
