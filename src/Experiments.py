#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from multiprocessing import Pool

from Subjects import *

class Experiment(object):
	"""Global class for salience-diagnosticity experiments.
	
	Input parameters:
		modality_sizes -- tuple of 4 values for stimulus modality sizes
			Values are given in this order: label_size, tail_size,
			body_size, head_size. They encode the number of units on
			which to encode each dimension of the stimuli.
		overlap_ratio -- overlap ratio value for head and tail in [0, 1]
		n_subjects -- number of subjects to run in total per theory (LaF, CR)
			Is expected to be a multiple of 8, for counterbalancing purposes.
		start_subject -- the subject number for the first subject
			Used if the experiment is ran in multiple bashes.
		pres_time -- maximum number of presentation for each trial
		threshold -- error threshold for model "looking away"
		n_blocks -- number of test blocks
		h_ratio -- ratios from output to hidden layer for networks
	
	Experiment properties:
		pres_time -- max number of presentations at familiarisation
		threshold -- "looking away" threshold at familiarisation
		n_trials -- number of familiarisation trials
		h_ratio -- n_hidden_neurons / n_output_neurons ratio
		lrn_rate -- learning rate for the network
		momentum -- momentum parameter for the network
		l_size, t_size, b_size, h_size -- modality sizes for different features
			In order, modality sizes for label, tail, body, head.
		p_ratio -- overlap ratio for physical values
		p_proto -- physical values for prototypes
		l_stims -- label values for stimuli
		fam_stims -- full stimuli for familiarisation trials
			A tuple of 4 stimuli lists. In order, 
	
	Experiment methods:
		run_experiment -- run a ful experiment, using only class properties
		generate_stims -- generate physical stimuli with overlap
		output_data -- convert results data to a csv file
	
	"""
	
	def __init__(self, modality_sizes, overlap_ratio, lrn_rates,
				 n_subjects, n_fam_pres, test_pres_time, threshold, h_ratio):
		"""Initialise a labeltime experiment.
		
		See class documentation for more details about parameters.
		
		"""
		self.n_fam_pres = n_fam_pres
		self.test_pres_time = test_pres_time
		self.threshold = threshold
		self.h_ratio = h_ratio
		# Learning rates and momentum
		self.lrn_rates = lrn_rates
		self.momentum = .05
		# Get meaningful short variables from input
		# l_ -> label_
		# h_ -> head_
		# t_ -> tail_
		# ol_ -> overlap_
		(self.l_size, self.h_size, self.t_size) = modality_sizes
		self.ol_ratio = overlap_ratio
		self.n_subjects = n_subjects
		# Generate feature prototypes
		t_proto = self.generate_stims(self.t_size, self.ol_ratio)
		h_proto = self.generate_stims(self.h_size, self.ol_ratio)
		# Generate feature (full categories)
		self.t_stims = (self.generate_category(t_proto[0], 8, "continuous"),
						self.generate_category(t_proto[1], 8, "continuous"))
		self.h_stims = (self.generate_category(h_proto[0], 8, "continuous"),
						self.generate_category(h_proto[1], 8, "continuous"))
		# Generate (no_labels, labels) part to add to one or the other stimulus
		# Using two no-labels for ease of automation
		labels = self.generate_stims(self.l_size, 0)
		no_labels = (np.zeros((1, self.l_size)),
					 np.zeros((1, self.l_size)))
		self.l_stims = (no_labels, labels) # index on l_stims is presence of label
		# Generate familiarisation stimuli
		self.fam_stims = []
		for condition in range(2):
			categories = []
			for category in range(2):
				stims = []
				for i in range(6):
					stims.append(np.hstack((self.l_stims[condition][category],
											self.h_stims[(i+category)%2][i],
											self.t_stims[category][i])))
				categories.append(stims)
			self.fam_stims.append(categories)
		# Generate new features for contrast test trials
		self.t_new = self.generate_stims(self.t_size, .1)[0]
		self.h_new = self.generate_stims(self.t_size, .1)[0]
		# Generate two full sets of contrast test stims (for counterbalancing)
		self.contrast_stims = ({"Head":{"Old":np.hstack((self.l_stims[0][0],
														 self.h_stims[0][6],
														 self.t_stims[0][6])),
										"New":np.hstack((self.l_stims[0][0],
														 self.h_new,
														 self.t_stims[1][6]))},
								"Tail":{"Old":np.hstack((self.l_stims[0][0],
														 self.h_stims[0][7],
														 self.t_stims[0][7])),
										"New":np.hstack((self.l_stims[0][0],
														 self.h_stims[1][6],
														 self.t_new))}},
							   {"Head":{"Old":np.hstack((self.l_stims[0][0],
														 self.h_stims[1][7],
														 self.t_stims[0][7])),
										"New":np.hstack((self.l_stims[0][0],
														 self.h_new,
														 self.t_stims[1][6]))},
								"Tail":{"Old":np.hstack((self.l_stims[0][0],
														 self.h_stims[1][6],
														 self.t_stims[1][6])),
										"New":np.hstack((self.l_stims[0][0],
														 self.h_stims[0][7],
														 self.t_new))}})
	
	def generate_stims(self, size, ratio):
		"""Generate two stims of given size with given overlap ratio."""
		# Initialise stims as ones
		stim1 = np.ones((1, size))
		stim2 = np.ones((1, size))
		# Computes number of overlapping units
		n_overlap = int(ratio * size)
		if (size - n_overlap) % 2:
			n_overlap += 1
		n_diff = size - n_overlap
		# Select which indices to change to zero for each explo
		# First create a list of indices
		i_total = np.arange(size)
		# Only keep indices with no overlap
		i_diff = np.random.choice(i_total, size=n_diff, replace=False)
		# Select half of the remaining indices for stim1
		i_stim1 = np.random.choice(i_diff, size=n_diff//2, replace=False)
		# Builds indices for explo2 as indices from i_diff not in i_stim1
		i_stim2 = np.setdiff1d(i_diff, i_stim1, assume_unique=True)
		# Set selected values to zero in stim1 and stim2
		stim1[0, i_stim1] = 0
		stim2[0, i_stim2] = 0
		return (stim1,stim2)
	
	def generate_category(self, prototype, n_exemplars, cat_method,
						  noise=.5, min_dist=1):
		"""Generate a category around a prototype."""
		n = 0
		steps = 0
		exemplars = [prototype] # Initialise exemplars list with prototype
		while n < n_exemplars and steps < 100000:
			steps += 1
			if cat_method == "continuous":
				new_exemplar = prototype + np.random.uniform(-noise, noise,
															 prototype.shape)
			for exemplar in exemplars:
				if np.linalg.norm(exemplar - new_exemplar) < min_dist:
					new_exemplar = None
					break
			if new_exemplar is not None:
				exemplars.append(new_exemplar)
				n += 1
		if steps == 100000:
			raise(NotImplementedError)
		return exemplars[1:] # Return all exemplars but first (prototype)
	
	def run_subject(self, subject_i, method):
		"""Run familiarisation for a single subject."""
		# Code s_type (subject type) on 2 bits:
		# 	- condition (0=no-label, 1=label)
		#	- contrast trial (for counterbalancing)
		s_type = format(subject_i%4,'02b') # type: str
		# Create subject
		s = Subject(self.l_size+self.h_size+self.t_size, self.l_size, self.h_size,
					self.h_ratio, self.lrn_rates, self.momentum)
		# Run familiarisation
		fam_results = s.fam_training(self.fam_stims[int(s_type[0])],
									 self.n_fam_pres, 1)
		# Run contrast test trials
		contrast_results = s.contrast_test(self.contrast_stims[int(s_type[1])],
										   self.test_pres_time, self.threshold)
		# Return results
		return fam_results, contrast_results
		
	def run_experiment(self, method=None):
		"""Run a full experiment.
		
		Return a tuple of results for familiarisation and training. Results
		are recorded in dictionaries, with subject number as key.
		Each subject's familiarisation results is a tuple of results as
		described in SingleObjectSubject class, with an extra value for
		exploration overlap appended to it.
		Each subject's training results is a the subject itself after
		background training. This allows us to find any information we want.
		
		"""
		# Initialise result gatherer as a dictionary (subject number as key)
		results_async = {}
		# Start running subjects
		with Pool() as pool:
			for subject_i in range(self.n_subjects):
				results_async[subject_i] = pool.apply_async(self.run_subject,
															(subject_i, method))
			pool.close()
			pool.join()
		fam_results = {}
		contrast_results = {}
		for subject_i in range(self.n_subjects):
			fam_results[subject_i] = results_async[subject_i].get()[0]
			contrast_results[subject_i] = results_async[subject_i].get()[1]
		return fam_results, contrast_results
	
	def output_fam_data(data, filename):
		"""Write data from familiarisation into a filename.csv file.

		Class-wide (not instance-specific) method.
		
		data is a dictionary structured as follows:
		- keys = subject numbers
			- network error
				- key = block number
			- hidden representations
				- key = block number
		Subject are ordered so that subject%4 in binary codes for
			- first value: condition (0=no-label, 1=label)
			
		Output a filename_errors.csv file and a filename_hidden_reps.csv file.
		"""
		# Network errors
		# Define column labels
		c_labels_LT = ','.join(["subject",
								"condition",
								"block",
								"error"])
		rows_LT = [c_labels_LT]
		# Prepare meaningful coding for parameters
		condition = ("no_label", "label")
		for subject in data:
			# Extract information from subject number
			s_type = format(subject%4,'02b')
			for block in data[subject][0]:
				# Create row for looking time results
				row = [str(subject),
					   condition[int(s_type[0])],
					   str(block),
					   str(data[subject][0][block])
					   ]
				rows_LT.append(','.join(row))
		# Join all rows with line breaks
		data_LT = '\n'.join(rows_LT)
		# Write str results into two files with meaningful extensions
		with open(filename+"_errors.csv", 'w') as f:
			f.write(data_LT + "\n")
	
	def output_contrast_data(data, filename):
		"""Write data from contrast test trials into a filename.csv file.

		Class-wide (not instance-specific) method.
		
		data is a dictionary structured as follows:
		- keys = subject numbers
			- Head/Tail
				-Old/New
					- looking time (number of presentations to learning)
		Subject are ordered so that subject%4 in binary codes for
			- first value: condition (0=no-label, 1=label)
		
		"""
		# Network errors
		# Define column labels
		c_labels_LT = ','.join(["subject",
								"condition",
								"contrast_type",
								"feature",
								"looking_time"])
		rows_LT = [c_labels_LT]
		# Prepare meaningful coding for parameters
		condition = ("no_label", "label")
		for subject in data:
			# Extract information from subject number
			s_type = format(subject%4,'02b')
			for contrast_type in data[subject]:
				for feature in data[subject][contrast_type]:
					# Create row for looking time results
					row = [str(subject),
						   condition[int(s_type[0])],
						   str(contrast_type),
						   str(feature),
						   str(data[subject][contrast_type][feature])
						   ]
				rows_LT.append(','.join(row))
		# Join all rows with line breaks
		data_LT = '\n'.join(rows_LT)
		# Write str results into two files with meaningful extensions
		with open(filename+".csv", 'w') as f:
			f.write(data_LT + "\n")

	def output_train_data(data, filename):
		"""Write data from training into a filename.csv file.

		Class-wide (not instance-specific) method.
		
		data is a dictionary structured as follows:
		- keys = subject numbers
			- hidden representations as returned per CategorySubject.bg_training
		Number of trials is assumed to be fixed.
		Subject are ordered so that subject%4 in binary codes for
			- first value: labbeled item (0=first item, 1=second item)
			- second value: first familiarisation item (1=labelled,0=unlabelled)
		
		"""
		# Create general column labels
		c_labels = ','.join(["subject",
							 "theory",
							 "step",
							 "labelled",
							 "exemplar"])
		# Get list of recorded steps for subject 0
		k = list(data.keys())[0]
		steps = list(data[k].keys())
		# Get dimension of hidden representations for LTM/STM
		dims_LTM = data[0][steps[0]]["LTM"][0][0].size
		dims_STM = data[0][steps[0]]["STM"][0][0].size
		# Create dimension column names
		dims_labels_LTM = ["dim" + str(i) for i in range(dims_LTM)]
		dims_labels_STM = ["dim" + str(i) for i in range(dims_STM)]
		# Create final column labels
		rows_LTM = [','.join([c_labels] + dims_labels_LTM)]
		rows_STM = [','.join([c_labels] + dims_labels_STM)]
		# Prepare meaningful coding for parameters
		theories = ("LaF", "CR")
		labelled = ("label", "no_label")
		for subject in data:
			# Extract information from subject number
			s_type = format(subject%8,'03b')
			theory = int(s_type[2])
			max_step = max(data[subject])
			for step in data[subject]:
				for category in range(2):
					for exemplar in range(4):
						# Create row for hidden representation results
						glob = [str(subject),
								theories[theory],
								str(step * (step<max_step)),
								labelled[category],
								str(exemplar + 4*category),
								]
						LTM = [str(data[subject][step]["LTM"]\
									   [category][exemplar][0,j])
							   for j in range(dims_LTM)]
						STM = [str(data[subject][step]["STM"]\
									   [category][exemplar][0,j])
							   for j in range(dims_STM)]
						rows_LTM.append(','.join(glob + LTM))
						rows_STM.append(','.join(glob + STM))
		# Join all rows with line breaks
		data_LTM = '\n'.join(rows_LTM)
		data_STM = '\n'.join(rows_STM)
		# Write str results into two files with meaningful extensions
		with open(filename+"_hidden_LTM.csv", 'w') as f:
			f.write(data_LTM + "\n")
		with open(filename+"_hidden_STM.csv", 'w') as f:
			f.write(data_STM + "\n")
