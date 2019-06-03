#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import warnings
from multiprocessing import Pool

from Experiments import *

def run_subjects(lrn_rates, verbose=True):
	if verbose:
		t = time.time()
		print("=" * 50)
		print("Starting run for lrn_rates =", lrn_rates)
	e = Experiment((8,10,10), .1, lrn_rates, 48, 2000, 200, 1e-3, 10/28)
	results = e.run_experiment()
	Experiment.output_fam_data(results[0],
							   "../results/familiarisation_" +\
							   str(round(lrn_rates[1]-lrn_rates[2],3)))
	Experiment.output_contrast_data(results[1],
									"../results/contrast_test_trials_" +\
									str(round(lrn_rates[1]-lrn_rates[2],3)))
	if verbose:
		t = time.gmtime(time.time() - t)
		print("Run finished in", time.strftime("%H:%M:%S",t))

def main():
	total = time.time()
	warnings.filterwarnings("ignore")
	# Run experiment
	results = {}
	for low_salience_rate in range(5, 50, 5):
		results[low_salience_rate] = run_subjects((.05, .05, low_salience_rate/1000))
	total = time.gmtime(time.time() - total)
	print("="*27,
		  "Total run time:",
		  time.strftime("%H:%M:%S",total),
		  "="*27)

if __name__ == "__main__":
	main()
