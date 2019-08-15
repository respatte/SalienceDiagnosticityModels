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
library(scales)

source("Routines.R")
source("geom_flat_violin.R")

# GATHER DATA ======================================================================================
fam_errors <- read.fam_errors()
contrast_trials <- read.contrast_trials()

# FAMILIARISATION ERRORS ===========================================================================
save_path <- "../results/FamErrors/"

# Prepare data
fam_errors.visual <- fam_errors %>%
  subset(error_type != "label") %>%
  droplevels()

# Run models
run_models <- F
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
generate_plots <- F
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
    facet_grid(error_type~salience_ratio,
               labeller = labeller(error_type = error_type_labels)) +
    scale_x_continuous(trans = log10_trans()) +
    scale_y_continuous(trans = log10_trans()) +
    stat_summary(fun.y='mean', geom='line', linetype = '61') +
    stat_summary(fun.data=mean_se, geom='ribbon', alpha= .25, colour=NA) +
    scale_colour_brewer(palette = "Dark2") +
    scale_fill_brewer(palette = "Dark2")
  ggsave(paste0(save_path, "VisualFeatures_data.pdf"),
         fam_errors.visual.plot,
         width = 5, height = 3.5,
         dpi = 600)
  ## Plot Intercept and Slope per condition:error_type:salience_ratio
  ### Prepare data
  fam_errors.visual.facet_estimates <- fam_errors.visual %>%
    select(-c(error)) %>%
    subset(salience_ratio %in% c(.2, .5, .8)) %>%
    mutate(error_pred = predict(fam_errors.visual.lmer,
                                newdata = .),
           salience_ratio = as_factor(salience_ratio)) %>%
    split(list(.$condition, .$error_type, .$salience_ratio)) %>%
    future_lapply(function(df){
      m <- lm(error_pred ~ z.block, data = df)
      t <- m %>%
        confint() %>%
        as_tibble(rownames = "parameter") %>%
        mutate(estimate = m$coefficients,
               condition = first(df$condition),
               error_type = first(df$error_type),
               salience_ratio = first(df$salience_ratio)) %>%
        return()
    }) %>%
    bind_rows()
  ### Plot data
  ### TODO: find out how ggeffects computes marginal effects per facet
  fam_errors.visual.facet_estimates.plot <- fam_errors.visual.facet_estimates %>%
    ggplot(aes(x = error_type,
               y = estimate,
               ymin = `2.5 %`,
               ymax = `97.5 %`,
               colour = condition,
               fill = condition)) +
    ylab("Parameter Estimate") + theme_bw() + coord_flip() +
    facet_grid(rows = vars(salience_ratio),
               cols = vars(parameter),
               scales = "free") +
    theme(legend.position = "top",
          axis.title.y = element_blank()) +
    #geom_pointrange(fatten = 1, position = position_dodge(width = .3)) +
    geom_errorbar(width = .1, size = .5, position = position_dodge(width = .3)) +
    geom_point(shape = 4, position = position_dodge(width = .3)) +
    scale_x_discrete(breaks = c("salient", "non_salient"),
                     labels = c("Head (salient)", "Tail (diagnostic)")) +
    scale_colour_brewer(palette = "Dark2")
  ggsave(paste0(save_path, "VisualFeatures_parameters.pdf"),
         fam_errors.visual.facet_estimates.plot,
         width = 5, height = 5,
         dpi = 600)
}

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
