#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import copy

from collections import deque

def sigmf(m):
	return 1 / (1 + np.exp(-m))

def exp_decay(n):
	return 0.25 * np.exp(-n)

class BackPropNetwork(object):
	"""Class computing a simple backpropagation network.
	
	Input parameters:
		n_neurons -- list, num of neurons per layer [input,hidden1,...,output]
		n_salient -- number of neurons for the salient feature (always the first feature)
		lrn_rates -- tuple of learning rates for backpropagation in ]0, 1]
			Values are given in this order: global learning rate, learning rate specific
			to salient feature inputs to first hidden layer, learning rate specific to
			non-salient feature inputs to first hidden layer
		momentum -- influence of inertial term in [0, 1], or function
			If set to a value, it only takes into account the last update
			values, pondering them with the given value.
			If set to a function, computes the function on the index of
			each previous update values in the inertia queue, pondering them
			in the calculus with those computed values.
			Default value is an exponential decay function.
			For the model to converge, sum(momentum) must be strictly less
			than lrn_rates.
		
	BackPropNetwork properties:
		n_layers -- number of layers for the network
		neurons -- list of n arrays of neuron activation (one array per layer)
			Neuron layers are row vectors, of dimension given by n_neurons.
			All neuron layers have their activation set at 0.
		weights -- list of n-1 arrays of connection weight between neuron layers
			Weights are initialised as random uniform values in [-.25, .25].
			weights[i] is the matrix of connections between layers i and i+1.
		inertia -- weight update values at previous steps
			Queue structure of which each element is a list of update values
			for all weight matrices at a previous run step of the algorithm.
		lrn_rates -- learning rate for backpropagation
		momentum -- influence of inertial terms
		inertial_memory -- number of inertial terms to keep in memory
		error -- error of the network on the last presented stimulus
	
	BackPropNetwork methods:
		init_weights_matrix
			Creates a matrix of weights from a layer to the next one,
			including weights for a bias value.
		forward -- forward activation from a layer of neuron to the next one
			When forwarding, adds a bias neuron to each bottom layer.
		gradient_output -- computes the gradients for output layer
		gradient_back -- computes the gradient for inner layers
		weight_delta -- computes the update values for weight matrices
		update_weights -- updates all weight matrices
		run -- runs the network with one (a set of) input pattern(s)
		
	"""
	def __init__(self,n_neurons,n_salient,lrn_rates,momentum=exp_decay):
		"""Initialise a simple back-propagation neural network.
		
		See class documentation for more details about parameters.
		
		"""
		self.error = None
		self.n_layers = len(n_neurons)
		# Setting up neuron layers
		self.neurons = [np.zeros((1, n_neurons[i]))
						for i in range(self.n_layers)]
		# Setting up connection weights
		self.weights = [self.init_weights_matrix(n_neurons[i],
												 n_neurons[i+1])
						for i in range(self.n_layers - 1)]
		# Setting first previous update values to zeros
		self.inertia = deque([[self.weights[i] * 0
							   for i in range(self.n_layers - 1)]])
		# Adding learning parameters
		# Defaults to having a bias term
		self.lrn_rates = (lrn_rates[0],
						  np.vstack((np.full((n_salient, 1),
											 lrn_rates[1]),
									 np.full((n_neurons[0] - n_salient, 1),
											 lrn_rates[2]),
									 [[lrn_rates[0]]])))
		# Set limit size of inertia queue (according to momentum function)
		self.momentum, self.inertia_memory = self.init_momentum(momentum)
	
	def init_weights_matrix(self, m, n, bias = True):
		"""Initialise weights as unfiform random values in [-0.25,0.25].
		
		Creates a matrix of m+1 rows --adding bias weights--, and n columns.
		If bias is set to False, then the bias weight is not added to m.
		
		"""
		if bias:
			return (np.random.ranf((m+1, n)) / 2) - 0.25
		return (np.random.ranf((m, n)) / 2) - 0.25
	
	def init_momentum(self, momentum):
		"""Initialise momentum and inertia memory size.
		
		Return a tuple (momentum, inertia_memory).
		
		"""
		if isinstance(momentum, float):
			return (momentum, 1)
		else:
			# Remember values only if weight given by momentum > 1e-3
			r = 1
			m = 0
			while r > 1e-3:
				m += 1
				r = momentum(m)
			inertia_memory = m
			# Check for total inertia being less than lrn_rates
			try:
				total_inertia = sum([momentum(x)
									 for x in range(inertia_memory)])
				min_lrn_rate = min(self.lrn_rates[0], np.min(self.lrn_rates[1]))
				assert total_inertia < min_lrn_rate
			except AssertionError:
				print("Inertia function weighing too much.",
					  "Setting it to min_lrn_rate/2")
				momentum = min_lrn_rate/2
				inertia_memory = 1
			return (momentum, inertia_memory)
	
	def forward(self, layer, gate=sigmf):
		"""Forward neuron activation from layer to layer+1.
		
		Returns the activation of layer i+1 as the activation of layer i
		and a bias neuron, multiplied by the weight matrix from i to i+1.
		i is the index of a layer, starting from the input layer at 0.
		Default behaviour is to further pass the activation of i+1
		through a sigmoid function. The parameter 'gate' can be set to
		another gate function, or None.
		
		"""
		layer1 = np.hstack((self.neurons[layer], [[1]]))
		layer2 = np.dot(layer1, self.weights[layer])
		if gate:
			return gate(layer2)
		return layer2
	
	def gradient_output(self, goal):
		"""Compute gradient for the output layer given a goal.
		
		Assume the cost function is the euclidian distance between goal
		and activation of output neurons, divide by 2.
		Assume the activation gate function is the linear function.
		
		"""
		# If no label units in model (i.e. STM model), remove label from goal
		l_size = goal.size - self.neurons[-1].size	
		if l_size:
			goal = np.delete(goal, range(l_size), axis=1)
		delta_c = self.neurons[-1] - goal
		self.error = delta_c
		sigma_prime = 1
		sigma_prime += .1 # Adding an offset term to avoid local minima
		return np.multiply(delta_c, sigma_prime)
	
	def gradient_back(self, gradient_upper, i):
		"""Compute gradient for any inner layer using previous layer gradient.
		
		Assume the activation gate function is the logistic function.
		i is the index for the bottom layer in this calculus.
		Do the calculus without bias weights, as they are
		not needed to compute gradients.
		
		"""
		weights = np.delete(self.weights[i], (-1), axis=0)
		gradient_descent = np.dot(gradient_upper,np.transpose(weights))
		sigma_prime = np.multiply(self.neurons[i], (1 - self.neurons[i]))
		sigma_prime += .1 # Adding an offset term to avoid local minima
		return np.multiply(gradient_descent, sigma_prime)
	
	def weight_delta(self, gradient_upper, i):
		"""Compute the update value for weights of layer i to i+1.
		
		First adds the bias (1) to the activation of layer i
		to update bias weights with the gradient.
		
		"""
		layer = np.hstack((self.neurons[i], [[1]]))
		return np.dot(np.transpose(layer), gradient_upper)
	
	def update_weights(self, i, delta):
		"""Compute updated value for weights of layer i to i+1."""
		if i == 0:
			# Use salient-spefici learning rates
			new_weights = self.weights[i] - np.multiply(delta,self.lrn_rates[1])
		else:
			# Use global learning rate
			new_weights = self.weights[i] - delta * self.lrn_rates[0]
		if isinstance(self.momentum,float):
			new_weights += self.momentum * self.inertia[0][i]
		else:
			for t in range(len(self.inertia)):
				new_weights += self.momentum(t) * self.inertia[t][i]
		return new_weights

	def propagate(self, stimulus):
		"""Compute the forward propagation."""
		# Input stimulus to the network
		# TODO - Assert stimulus shape is consistent
		self.neurons[0] = stimulus
		# Forward propagation
		# Linear gate function for connections to output layer
		for layer in range(1, self.n_layers-1):
			self.neurons[layer] = self.forward(layer-1)
		layer += 1
		self.neurons[layer] = self.forward(layer-1, gate=None)

	def backpropagate(self, goal, r=False):
		"""Compute the backpropagation of the error."""
		# Backward computing of gradients
		# First value of gradients never used as no gradient for input layer
		gradients = [None for _ in range(self.n_layers)]
		# Start with output layer gradient
		gradients[self.n_layers - 1] = self.gradient_output(goal)
		# Loop over gradients backwards, starting with last hidden layer
		for layer in range(self.n_layers - 2, 0, -1):
			gradients[layer] = self.gradient_back(gradients[layer + 1], layer)
		# Get update values (delta) for weights and update weights
		weight_deltas = []
		for layer in range(self.n_layers - 1):
			delta = self.weight_delta(gradients[layer + 1], layer)
			weight_deltas.append(delta)
			self.weights[layer] = self.update_weights(layer, delta)
		# Store new deltas in the inertia of the network, forget too old ones
		self.inertia.appendleft(weight_deltas)
		if len(self.inertia) > self.inertia_memory:
			self.inertia.pop()
		if r:
			return gradients
		
	def run(self, stimulus, goal=None):
		"""Run the full propagation+backpropagation for a stimulus.
		
		Stimulus must be a numpy array of the same shape as the first
		layer of neurons (specified when creating the network).
		
		"""
		# Set up goal if none specified
		if goal is None:
			goal = stimulus
		self.propagate(stimulus)
		self.backpropagate(goal)
