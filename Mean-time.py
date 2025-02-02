#%% Packages


import os
import pickle

import numpy as np
from scipy.sparse.linalg import spsolve
from scipy.special import comb

from homeostatic.definitions import coefficient_matrix

#%% Parameters


new_clone_is_soft = False
max_level_value = 100
mu_value = 1.0
n_mean_value = 10
gamma_value = 1.0
base_stimulus = 10
clones = 2
sample_value = 0

#%% Reading Samples


if clones == 2:
    stimulus_value = [base_stimulus * gamma_value, base_stimulus * gamma_value]

    probability_values = np.genfromtxt(
        "Samples/Established-Matrix/Matrix-2C.csv", delimiter=","
    )
    nu_value = np.genfromtxt(
        "Samples/Established-Nu-Matrix/Nu-Matrix-2C.csv", delimiter=","
    )
elif clones == 3:
    stimulus_value = [
        base_stimulus * gamma_value,
        base_stimulus * gamma_value,
        base_stimulus * gamma_value,
    ]

    probability_values = np.genfromtxt(
        "Samples/Matrices/Matrix-{}.csv".format(sample_value), delimiter=","
    )
    if sample_value < 3:
        if new_clone_is_soft:
            nu_value = np.genfromtxt(
                "Samples/Nu-Matrices/Nu-Matrix-Soft.csv", delimiter=","
            )
        else:
            nu_value = np.genfromtxt(
                "Samples/Nu-Matrices/Nu-Matrix-Hard.csv", delimiter=","
            )
    else:
        if new_clone_is_soft:
            nu_value = np.genfromtxt(
                "Samples/Nu-Matrices/Nu-Matrix-Soft-(D).csv", delimiter=","
            )
        else:
            nu_value = np.genfromtxt(
                "Samples/Nu-Matrices/Nu-Matrix-Hard-(D).csv", delimiter=","
            )

dimension_value = probability_values.shape[0]
nu_value = nu_value * n_mean_value

#%% Solving difference equations


M = coefficient_matrix(
    probability_values, max_level_value, mu_value, nu_value, stimulus_value
)
b = [-1] * int(comb(max_level_value, dimension_value))

Solution = spsolve(M, b)

#%% Storing Data

if clones == 2:
    parameters_path = "Results/Mean time to extinction/Established/Parameters.bin"
    data_path = "Results/Mean time to extinction/Established/Data.bin"
elif clones == 3:
    if new_clone_is_soft:
        parameters_path = (
            f"Results/Mean time to extinction/Soft/Matrix-{sample_value}/Parameters.bin"
        )
        data_path = (
            f"Results/Mean time to extinction/Soft/Matrix-{sample_value}/Data.bin"
        )
    else:
        parameters_path = (
            f"Results/Mean time to extinction/Hard/Matrix-{sample_value}/Parameters.bin"
        )
        data_path = (
            f"Results/Mean time to extinction/Hard/Matrix-{sample_value}/Data.bin"
        )

os.makedirs(os.path.dirname(parameters_path), exist_ok=True)
os.makedirs(os.path.dirname(data_path), exist_ok=True)

with open(parameters_path, "wb") as file:
    param_data = [
        new_clone_is_soft,
        max_level_value,
        mu_value,
        n_mean_value,
        gamma_value,
        clones,
        sample_value,
        dimension_value,
        nu_value,
    ]
    pickle.dump(param_data, file)

with open(data_path, "wb") as file:
    pickle.dump(Solution, file)
