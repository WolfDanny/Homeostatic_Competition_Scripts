#%% Packages


from homeostatic import *
from scipy.special import comb
from scipy.stats import uniform
from itertools import chain, combinations
from scipy.sparse import coo_matrix, csc_matrix
from scipy.sparse.linalg import inv
import numpy as np
import pickle
import gc
import os

#%% Global parameters


new_clone_is_soft = False
max_level_value = 179
mu_value = 1.0
n_mean_value = 10
gamma_value = 1.0
clones = 3
base_stimulus = 10
model_value = ModelHolder  # 1 = First auxiliary process (X^(1)), 2 = Second auxiliary process (X^(2))
sample_value = SampleHolder  # Not used if 'clones' is 2

#%% Reading Samples


if clones == 2:
    stimulus_value = [base_stimulus * gamma_value, base_stimulus * gamma_value]
    distribution = np.zeros((max_level_value, max_level_value))

    probability_values = np.genfromtxt("../Samples/Established-Matrix/Matrix-2C.csv", delimiter=",")
    nu_value = np.genfromtxt("../Samples/Established-Nu-Matrix/Nu-Matrix-2C.csv", delimiter=",")

if clones == 3:
    stimulus_value = [base_stimulus * gamma_value, base_stimulus * gamma_value, base_stimulus * gamma_value]
    distribution = np.zeros((max_level_value, max_level_value, max_level_value))

    probability_values = np.genfromtxt("../Samples/Matrices/Matrix-{}.csv".format(sample_value), delimiter=",")
    if sample_value < 3:
        if new_clone_is_soft:
            nu_value = np.genfromtxt("../Samples/Nu-Matrices/Nu-Matrix-Soft.csv", delimiter=",")
        else:
            nu_value = np.genfromtxt("../Samples/Nu-Matrices/Nu-Matrix-Hard.csv", delimiter=",")
    else:
        if new_clone_is_soft:
            nu_value = np.genfromtxt("../Samples/Nu-Matrices/Nu-Matrix-Soft-(D).csv", delimiter=",")
        else:
            nu_value = np.genfromtxt("../Samples/Nu-Matrices/Nu-Matrix-Hard-(D).csv", delimiter=",")

dimension_value = probability_values.shape[0]
nu_value = nu_value * n_mean_value

#%% Linear level reduction algorithm


matrices = [[], [], []]

# Calculating main diagonal matrices
for level_value in range(dimension_value, max_level_value + 1):
    matrix = main_diagonal_matrices_approximation(level_value, max_level_value, dimension_value, probability_values, mu_value, nu_value, stimulus_value, model_value)
    matrices[0].append(matrix)

# Calculating lower diagonal matrices
for level_value in range(dimension_value + 1, max_level_value + 1):
    matrix = death_diagonal_matrices_approximation(level_value, dimension_value, mu_value, model_value)
    matrices[1].append(matrix)

# Calculating upper diagonal matrices
for level_value in range(dimension_value, max_level_value):
    matrix = birth_diagonal_matrices_approximation(level_value, dimension_value, probability_values, nu_value, stimulus_value)
    matrices[2].append(matrix)

# Calculating the inverses of H matrices, and storing them in inverse order
h_matrices = [inv(matrices[0][-1])]

for level_value in range(len(matrices[0]) - 1):
    gc.collect()
    matrix = matrices[0][-(level_value + 2)]
    matrix_term = matrices[2][-(level_value + 1)].dot(h_matrices[-1].dot(matrices[1][-(level_value + 1)]))
    matrix -= matrix_term
    matrix = np.linalg.inv(matrix.todense())
    h_matrices.append(csc_matrix(matrix))

# Calculating the relative values of the distribution
distribution = [np.array([1])]

for level_value in range(len(h_matrices) - 1):
    value = (distribution[level_value] * (-1)) * matrices[2][level_value].dot(h_matrices[-(level_value + 2)])
    distribution.append(value.flatten())

# Normalising the values of the distribution
subTotals = [level.sum() for level in distribution]
total = sum(subTotals)

for level_value in range(len(distribution)):
    distribution[level_value] = distribution[level_value] / total

#%% Storing results

if clones == 2:
    params = '../Results/QSD/Established/Model-{0}/Parameters.bin'.format(model_value)
    dat = '../Results/QSD/Established/Model-{0}/Data.bin'.format(model_value)

if clones == 3:
    if new_clone_is_soft:
        params = '../Results/QSD/Soft/Model-{}/Parameters.bin'.format(model_value)
        dat = '../Results/QSD/Soft/Model-{0}/QSD-S-{1}/Data.bin'.format(model_value, sample_value)
    else:
        params = '../Results/QSD/Hard/Model-{}/Parameters.bin'.format(model_value)
        dat = '../Results/QSD/Hard/Model-{0}/QSD-S-{1}/Data.bin'.format(model_value, sample_value)

os.makedirs(os.path.dirname(params), exist_ok=True)
file = open(params, 'wb')
parameters = (["dimension_value", "max_level_value", "mu_value", "gamma_value", "stimulus_value", "model_value"], dimension_value, max_level_value, mu_value, gamma_value, stimulus_value, model_value)
pickle.dump(parameters, file)
file.close()

os.makedirs(os.path.dirname(dat), exist_ok=True)
file = open(dat, 'wb')
pickle.dump(distribution, file)
file.close()
