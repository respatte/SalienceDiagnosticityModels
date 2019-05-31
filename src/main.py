#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import warnings
from multiprocessing import Pool

from Experiments import *

def run_subjects(n_subjects, experiment, bash_i=0, explo_ratio=None,
				 verbose=False):
	if verbose:
		t = time.time()
		print("=" * 40)
		if explo_ratio is not None:
			print("Starting runs for explo_ratio =", explo_ratio)
		else:
			print("Starting runs for CategoryExperiment")
	if experiment == "SingleObject":
		condition = SingleObjectExperiment((5,10,8), (.1,explo_ratio),
										   n_subjects, n_subjects*bash_i)
	elif experiment == "Category":
		condition = CategoryExperiment((5,10,0), (.1, 0),
									   n_subjects, n_subjects*bash_i)
	noise = "np.random.uniform(.1, .3, (m,n)) * "
	noise += "(2 * np.random.binomial(1, .5, (m,n)) - 1)"
	reinit = None
	results = condition.run_experiment(method=noise)
	if verbose:
		t = time.gmtime(time.time() - t)
		print("Runs finished in", time.strftime("%H:%M:%S",t))
	return results

def main():
	total = time.time()
	warnings.filterwarnings("ignore")
	# Run Category experiment
	e = Experiment((8,10,10), .1, (.1,.12,.08), 48, 1000, 100, 1e-3, 19/24)
	results = e.run_experiment()
	Experiment.output_fam_data(results[0], "../results/familiarisation")
	Experiment.output_contrast_data(results[1], "../results/contrast_test_trials")
	total = time.gmtime(time.time() - total)
	print("="*27,
		  "Total run time:",
		  time.strftime("%H:%M:%S",total),
		  "="*27)
	return results

if __name__ == "__main__":
	fam_results, contrast_results = main()
