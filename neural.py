import numpy as np
import copy

def binary_function(values):
		result = []
		for value in values[0]:
			result_val = 0 if value < 0 else 1
			result.append(result_val)
		return result

class NeuralNetwork:
	mutation_rate = 0.1
	def __init__(self, input_to_hidden_weights = None, hidden_to_output_weights = None, hidden_biases = None, output_biases = None):
		np.random.seed()
		self.input_to_hidden_weights = 2 * np.random.random((6, 5)) - 1
		self.hidden_to_output_weights = 2 * np.random.random((5, 2)) - 1
		self.hidden_biases = 2 * np.random.random((1, 5)) - 1
		self.output_biases = 2 * np.random.random((1, 2)) - 1

	def rectifier(self, values):
		return list(map(lambda x: 0 if x < 0 else x, values[0]))

	def run_network(self, input_values):
		input_values = input_values.astype(float)
		input_values_times_weights = np.matmul(input_values, self.input_to_hidden_weights)
		hidden_values = self.rectifier(input_values_times_weights + self.hidden_biases)
		hidden_values_times_weights = np.matmul(hidden_values, self.hidden_to_output_weights)
		output_values = binary_function(hidden_values_times_weights + self.output_biases)
		return output_values

	def breed(network1, network2):
		child1 = NeuralNetwork()
		child2 = NeuralNetwork()
		child3 = NeuralNetwork()
		child4 = NeuralNetwork()

		child1.input_to_hidden_weights = copy.deepcopy(network1.input_to_hidden_weights)
		child1.hidden_to_output_weights = copy.deepcopy(network2.hidden_to_output_weights)
		child1.hidden_biases = copy.deepcopy(network2.hidden_biases)
		child1.output_biases = copy.deepcopy(network1.output_biases)

		child2.input_to_hidden_weights = copy.deepcopy(network2.input_to_hidden_weights)
		child2.hidden_to_output_weights = copy.deepcopy(network1.hidden_to_output_weights)
		child2.hidden_biases = copy.deepcopy(network1.hidden_biases)
		child2.output_biases = copy.deepcopy(network2.output_biases)

		child3.input_to_hidden_weights = copy.deepcopy(network1.input_to_hidden_weights)
		child3.hidden_to_output_weights = copy.deepcopy(network1.hidden_to_output_weights)
		child3.hidden_biases = copy.deepcopy(network2.hidden_biases)
		child3.output_biases = copy.deepcopy(network2.output_biases)

		child4.input_to_hidden_weights = copy.deepcopy(network2.input_to_hidden_weights)
		child4.hidden_to_output_weights = copy.deepcopy(network2.hidden_to_output_weights)
		child4.hidden_biases = copy.deepcopy(network1.hidden_biases)
		child4.output_biases = copy.deepcopy(network1.output_biases.c)

		return (child1, child2, child3, child4)

	def mutate(self):
		np.random.seed()
		val1 = (2 * np.random.random((6, 5)) - 1) * NeuralNetwork.mutation_rate
		self.input_to_hidden_weights += (2 * np.random.random((6, 5)) - 1) * NeuralNetwork.mutation_rate
		self.hidden_to_output_weights += (2 * np.random.random((5, 2)) - 1) * NeuralNetwork.mutation_rate
		self.hidden_biases += (2 * np.random.random((1, 5)) - 1) * NeuralNetwork.mutation_rate
		self.output_biases += (2 * np.random.random((1, 2)) - 1) * NeuralNetwork.mutation_rate

	def save(self):
		print self.input_to_hidden_weights, self.hidden_to_output_weights, self.hidden_biases, self.output_biases

	def __copy__(self):
		return NeuralNetwork(
			self.input_to_hidden_weights.copy(), 
			self.hidden_to_output_weights.copy(), 
			self.hidden_biases.copy(), 
			self.output_biases.copy()
		)