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
	
	def __init__(self, stim_size, n_salient, h_ratio, lrn_rates, momentum=None):
		"""Initialise a simple labeltime subject for K&W2017.
		
		See class documentation for more details about parameters.
		
		"""
		# Create backpropagation network
		n_input = stim_size
		n_output = stim_size
		n_hidden = int(n_output * h_ratio)
		if momentum:
			self.net = bpn.BackPropNetwork([n_input, n_hidden, n_output],
										   n_salient, lrn_rates, momentum)
		else:
			self.net = bpn.BackPropNetwork([n_input, n_hidden, n_output],
										   n_salient, lrn_rates)
	
	def fam_training(self, stims, n_steps, rec_epoch):
		"""Compute the familiarisation phase for SalienceDiagnosticityEmpirical.
		
		Return network errors after each presentation, and hidden
		representations at specified epochs.
		
		"""
		# Initialise hidden representations dictionary
		h_reps = {}
		errors = []
		# Shuffle stims from each category
		np.random.shuffle(stims[0])
		np.random.shuffle(stims[1])
		# Get number of stimuli
		n_stims = len(stims[0])
		for step in range(n_steps):
			for stim in range(n_stims):
				# Train the network on an exemplar from each category, save errors
				self.net.run(stims[0][stim])
				errors.append(self.net.error)
				self.net.run(stims[1][stim])
				errors.append(self.net.error)
				if not (1+step) % rec_epoch or step==n_steps-1:
					# Save hidden representations
					h_reps[1+step] = self.net.neurons[1]
		return errors, h_reps
	
	def test_training(self, test_stims, test_goals,
					 pres_time, threshold, n_trials):
		"""Computes .
		
		The model is presented with each stimulus, alternating, for
		n_trials number of trials. For each trial, the model is presented
		with each stiumulus until the network error reaches threshold
		or for pres_time backpropagations.
		stims is a set of two stimuli with values at zero for label and
		exploration units.
		
		Return a couple (looking_times, errors).
		looking_times is a list of the number of backpropagations per
		trial before reaching stopping criteria. For each trial, a tuple
		of number of backpropagations for each stimulus is recorded.
		errors is a list of the errors per trial and per stimulus. Each
		element of this list is a couple of two lists, one per stimulus.
		
		"""
		looking_times = []
		for trial in range(n_trials):
			looking_times_trial = []
			for stim in range(len(test_stims)):
				time_left = pres_time
				error = 1
				while time_left > 0 and error > threshold:
					# Goal specification necessarry for CR models
					self.net.run(test_stims[stim], test_goals[stim])
					error = np.linalg.norm(self.net.error)
					time_left -= 1
				looking_times_trial.append(pres_time - time_left)
			looking_times.append(looking_times_trial)
		return looking_times

class SingleObjectSubject(Subject):
	"""Class computing a participant for the first labeltime study.
	
	In this class, the subject is trained with two single objects to
	reproduce the setup in Twomey & Westermann (2017).
	
	Input parameters:
		stims -- tuple of two stimuli of same size
			All object-specific information is encoded into the stimuli.
			This includes any overlap in visual/physical properties of
			the two stimuli.
			This also includes a label for one of the two stimuli (the
			absence of a label being coded as zeros). The label and its
			size in encoding are set beforehands, as it is not subject-
			specific. 
		exploration -- tuple of values for exploration importance and overlap
			The first value of the tuple defines the number of units on
			which exploration will be encoded. A bigger number of units
			means a richer exploration of the stimulus by the subject.
			The second value is a ratio (in [0, 1]), and defines the
			overlap in the encoding of exploration between the two
			stimuli, i.e. the between-stimulus similarity amongst haptic
			and interaction dimensions. This is subject-specific.
		theory -- theory implemented (CR or LaF)
		l_size -- label size
		h_ratio -- ratio of hidden neurons compared to input neurons
		lrn_rate -- learning rate(s) of the backpropagation network
		momentum -- influence of inertial term in [0, 1], or function
		model -- model used for neural network (BPN or DMN)
			If using DMN (DualMemoryNetwork), then learning rate and
			momentum must be given for both memories and lateral
			connections.
			See BackPropNetworks.DualMemoryNetwork documentation for more
			precision.
	
	Subject properties:
		stims -- tuple of two stimuli of same size
			Those stimuli include both the input stimuli (object-specific)
			and the exploration of the stimuli (subject-specific).
			When implementing a CR model, the label part is cut off.
		goals -- training goals for the network
			Same as full_stims, keeping the label for both Laf and CR.
		net -- backpropagation network used for learning
		impair -- target network for memory impairment
	
	Subject methods:
		encode_explo -- encode stimuli exploration given importance and overlap
		bg_training -- trains network on stimuli before familiarisation trials
		fam_training -- performs familiarisation trials as in T&W2017
		impair_memory -- impairs the memory, typically between training and test
	
	"""

	def __init__(self, stims, exploration, theory, l_size, h_ratio, lrn_rate,
				 momentum=None, model="DMN"):
		"""Initialise a simple labeltime subject for K&W2017.
		
		See class documentation for more details about parameters.
		
		"""
		Subject.__init__(self, stims, exploration, theory, l_size, h_ratio,
						 lrn_rate, momentum, model)
		self.stims = self.proto_stims
		del self.proto_stims
		self.goals = self.proto_goals
		del self.proto_goals
	
	def bg_training(self, bg_parameters):
		"""Background training of the network on both simuli.
		
		bg_parameters is a tuple with values mu_t, sigma_t, mu_p, sigma_p.
		To mimic the experimental conditions, total play time and play
		time per object are not strictly equal but follow a Gaussian
		distribution.
		To further mimic the experimental conditions, the model is
		presented alternatively with one object then the other, for
		differing times.
		The number of play sessions for each object is the same to avoid
		an overtraining of the last presented object. The total play
		time for each object is kept within a standard deviation from
		the mean total looking time to each object.
		
		"""
		mu_t, sigma_t = bg_parameters
		n_steps = round(np.random.normal(mu_t, sigma_t))
		for step in range(n_steps):
			self.net.run(self.stims[0],self.goals[0])
			self.net.run(self.stims[1],self.goals[1])

class CategorySubject(Subject):
	"""Class computing a participant for the second labeltime study.
	
	In this class, the subject is trained with two sets of objects to
	reproduce the setup in Twomey & Westermann (in progress).
	
	Input parameters:
		proto -- tuple of two prototype of same size
			All object-specific information is encoded into the stimuli.
			This includes any overlap in visual/physical properties of
			the two stimuli.
			This also includes a label for one of the two stimuli (the
			absence of a label being coded as zeros). The label and its
			size in encoding are set beforehands, as it is not subject-
			specific.
		stims -- tuple of two stimulus lists (derived from the prototypes)
		theory -- theory implemented (CR or LaF)
		l_size -- label size
		h_ratio -- ratio of hidden neurons compared to input neurons
		lrn_rate -- learning rate(s) of the backpropagation network
		momentum -- influence of inertial term in [0, 1], or function
		model -- model used for neural network (BPN or DMN)
			If using DMN (DualMemoryNetwork), then learning rate and
			momentum must be given for both memories and lateral
			connections.
			See BackPropNetworks.DualMemoryNetwork documentation for more
			precision.
	
	Subject properties:
		n_stims -- number of stimuli in each category
		proto_stims -- tuple of two prototype stimuli of same size
			When implementing a CR model, the label part is cut off.
		stims -- tuple of two stimuli lists of same size
			When implementing a CR model, the label part is cut off.
		proto_goals, goals -- training goals for the network
			Same as proto_stims and stims, keeping the label for both theories.
		net -- backpropagation network used for learning
		impair -- target network for memory impairment
	
	Subject methods:
		encode_explo -- encode stimuli exploration given importance and overlap
		bg_training -- trains network on stimuli before familiarisation trials
		fam_training -- performs familiarisation trials as in T&W2017
		impair_memory -- impairs the memory, typically between training and test
	
	"""
	
	def __init__(self, proto, stims, theory, l_size, h_ratio, lrn_rate,
				 momentum, model="DMN"):
		"""Initialise a simple labeltime subject for K&W_inprogress.
		
		See class documentation for more details about parameters.
		
		"""
		Subject.__init__(self, proto, (0,0), theory, l_size, h_ratio,
						 lrn_rate, momentum, model)
		self.n_stims = len(stims[0])
		self.goals = stims
		if theory == "CR":
			self.stims = ([],[])
			for stim in range(self.n_stims):
				self.stims[0].append(np.delete(stims[0][stim],
											   range(l_size),
											   axis=1))
				self.stims[1].append(np.delete(stims[1][stim],
											   range(l_size),
											   axis=1))
		else:
			self.stims = stims
	
	def bg_training(self, bg_parameters):
		"""Background training of the network on both simuli.
		
		bg_parameters is a tuple with values n_days, mu_p, sigma_p.
		To mimic the experimental conditions, exposition time per object
		per session is not fixed but follows a Gaussian distribution.
		To further mimic the experimental conditions, the model is
		presented alternatively with one object then the other, for
		differing times.
		The whole set of stimuli from both categories is presented for
		n_days times, alternating between stimuli fron each category.

		Return a dictionary of hidden representations at specified
		time-steps, with structure as follows:
		- keys = step (last is at the end of training)
			- dict, keys = "LTM", "STM"
				- category sublists (0:labelled category, 1:unlabelled category)
					- list of hidden representations (ndarrays)
		
		"""
		mu_t, sigma_t, rec_epoch = bg_parameters
		n_steps = round(np.random.normal(mu_t, sigma_t))
		h_reps = {}
		for step in range(n_steps):
			if not (1+step) % rec_epoch or step==n_steps-1:
				h_reps[1+step] = {"LTM":[[],[]], "STM":[[],[]]}
			for stim in range(self.n_stims):
				self.net.run(self.stims[0][stim],self.goals[0][stim])
				if not (1+step) % rec_epoch or step==n_steps-1:
					h_reps[1+step]["LTM"][0].append(self.net.LTM.neurons[1])
					h_reps[1+step]["STM"][0].append(self.net.STM.neurons[1])
				self.net.run(self.stims[1][stim],self.goals[1][stim])
				if not (1+step) % rec_epoch or step==n_steps-1:
					h_reps[1+step]["LTM"][1].append(self.net.LTM.neurons[1])
					h_reps[1+step]["STM"][1].append(self.net.STM.neurons[1])
		return h_reps
