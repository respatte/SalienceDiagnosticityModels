#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy as cp
import numpy as np

import BackPropNetworks as bpn

class Subject(object):
	"""Global subject class with methods common to all subject types.
	
	Input parameters:
		stims -- tuple of two prototypes of same size
			All object-specific information is encoded into the stimuli.
			This includes any overlap in visual/physical properties of
			the two stimuli.
			This also includes a label for one of the two stimuli (the
			absence of a label being coded as zeros). The label and its
			size in encoding are set beforehands, as it is not subject-
			specific. 
		l_size -- label size
		h_ratio -- ratio of hidden neurons compared to input neurons
		lrn_rates -- learning rates of the backpropagation network
		momentum -- influence of inertial term in [0, 1], or function
	
	Subject properties:
		stims -- tuple of two prototype stimuli of same size
			Those stimuli include both the input stimuli (object-specific)
			and the exploration of the stimuli (subject-specific).
			When implementing a CR model, the label part is cut off.
		net -- backpropagation network used for learning
	
	Subject methods:
		fam_training -- performs familiarisation trials as in SalienceDiagnosticityEmpirical
		contrast_test -- performs contrast test trials as in SalienceDiagnosticityEmpirical
		word_learning_test -- performs word learning test trials as in SalienceDiagnosticityEmpirical
	
	"""
	
	def __init__(self, stim_size, n_label, n_salient, h_ratio, lrn_rates, momentum=None):
		"""Initialise a simple subject from SalienceDiagnosticityEmpirical.
		
		See class documentation for more details about parameters.
		
		"""
		# Create backpropagation network
		n_input = stim_size
		n_output = stim_size
		n_hidden = int(n_output * h_ratio)
		if momentum:
			self.net = bpn.BackPropNetwork([n_input, n_hidden, n_output],
										   n_label, n_salient, lrn_rates, momentum)
		else:
			self.net = bpn.BackPropNetwork([n_input, n_hidden, n_output],
										   n_label, n_salient, lrn_rates)
	
	def fam_training(self, stims, n_steps, rec_epoch):
		"""Compute the familiarisation phase for SalienceDiagnosticityEmpirical.
		
		Return network errors and hidden representations at specified epochs.
		
		"""
		# Initialise outputs
		h_reps = {}
		errors = {}
		# Indices for errors for groups of units
		i_label = self.net.n_label
		i_salient = self.net.n_label + self.net.n_salient
		# Get number of stimuli
		n_stims = len(stims[0])
		# Shuffle stims indices from each category
		stims_i = [np.arange(n_stims), np.arange(n_stims)]
		np.random.shuffle(stims_i[0])
		np.random.shuffle(stims_i[1])
		for step in range(n_steps):
			block_h_reps = {}
			label_errors = []
			salient_errors = []
			non_salient_errors = []
			for stim in range(n_stims):
				for cat in range(2):
					# Train the network on an exemplar from each category
					self.net.run(stims[cat][stims_i[cat][stim]])
					if not (1+step) % rec_epoch or step==n_steps-1 or step == 0:
						# Save hidden representation and stim type
						stim_type = str(cat) + str(stims_i[cat][stim])
						block_h_reps[stim_type] = self.net.neurons[1]
						# Save error
						label_errors.append(np.linalg.norm(self.net.error[0, :i_label]))
						salient_errors.append(np.linalg.norm(self.net.error[0, i_label:i_salient]))
						non_salient_errors.append(np.linalg.norm(self.net.error[0, i_salient:]))
			if not (1+step) % rec_epoch or step==n_steps-1 or step == 0:
				# Save hidden representations and errors
				h_reps[1+step] = block_h_reps
				errors[1+step] = [np.mean(label_errors),
								  np.mean(salient_errors),
								  np.mean(non_salient_errors)]
		return errors, h_reps
	
	def contrast_test(self, contrast_stims, pres_time, threshold):
		"""Compute head and tail contrast test trials from SalienceDianosticityEmpirical."""
		# Initialise outputs
		looking_times = {"Head":{"Old":None, "New":None},
						 "Tail":{"Old":None, "New":None}}
		for feature in ("Head", "Tail"):
			for old_new in ("Old", "New"):
				net = cp.deepcopy(self.net)
				time_left = pres_time
				error = 1
				while time_left > 0 and error > threshold:
					# Goal specification necessarry for CR models
					self.net.run(contrast_stims[feature][old_new])
					error = np.linalg.norm(self.net.error)
					time_left -= 1
				looking_times[feature][old_new] = pres_time - time_left
		return looking_times
