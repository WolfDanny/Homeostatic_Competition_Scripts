# %% Packages

import os
import sys

sys.path.append(
    os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), os.pardir)
)

import pickle
from distutils.spawn import find_executable

import matplotlib.pyplot as plt
import seaborn as sns

from homeostatic.definitions import level_position_full_space

if find_executable("latex"):
    plt.rcParams.update({"text.usetex": True})
    plt.rcParams["text.latex.preamble"] = r"\usepackage{graphicx}\usepackage{eucal}"
sns.set(font="serif")

# %% Loading data and generating figures


plotted_state = [4, 8, 8]
scenario_names = [
    ["$\\textbf{(a)}$", "$\\textbf{(b)}$"],
    ["$\\textbf{(c)}$", "$\\textbf{(d)}$"],
]
experiments = ["Hard", "Soft"]

label_size = 20
title_size = 22

for folder in experiments:
    fig, graphs = plt.subplots(2, 2, figsize=(6, 6), constrained_layout=True)
    matrices = 4
    for current_matrix in range(matrices):
        row = int(current_matrix / 2)
        col = current_matrix % 2
        division_distributions = [[] for _ in range(3)]
        for current_clone in range(3):
            with open(
                f"{folder}/Matrix-{current_matrix}/Clone-{current_clone + 1}/Parameters-{current_matrix}.bin",
                "rb",
            ) as file:
                load_data = pickle.load(file)

            dimension_value = load_data[1]
            max_level_value = load_data[2]
            num_divisions = load_data[6]

            del load_data

            indexes = [i for i in range(num_divisions + 1)]

            for current_division in range(num_divisions + 1):
                with open(
                    f"{folder}/Matrix-{current_matrix}/Clone-{current_clone + 1}/Data-{current_division}.bin",
                    "rb",
                ) as file:
                    data = pickle.load(file)

                probability_value = (
                    data[sum(plotted_state)]
                    .todense()[
                        level_position_full_space(
                            sum(plotted_state), dimension_value, plotted_state
                        )
                    ]
                    .tolist()[0][0]
                )
                division_distributions[current_clone].append(probability_value)

            normalising_constant = sum(division_distributions[current_clone])
            for division in range(num_divisions + 1):
                division_distributions[current_clone][division] = (
                    division_distributions[current_clone][division]
                    / normalising_constant
                )

        graphs[row, col].plot(
            indexes,
            division_distributions[0],
            color="black",
            linestyle="solid",
            label="$\\mathcal{D}_{1}$",
        )
        graphs[row, col].plot(
            indexes,
            division_distributions[1],
            color="red",
            linestyle="dashed",
            label="$\\mathcal{D}_{2}$",
        )
        graphs[row, col].plot(
            indexes,
            division_distributions[2],
            color="deepskyblue",
            linestyle="dotted",
            label="$\\mathcal{D}_{3}$",
        )

        graphs[row, col].set_title(scenario_names[row][col], fontsize=title_size)
        graphs[row, col].tick_params(bottom=True, left=True, length=4)
        graphs[row, col].set_ylim(0, 0.3)
        graphs[row, col].set_xlim(0, 35)
        graphs[row, col].set_facecolor("white")
        graphs[row, col].spines["bottom"].set_color("k")
        graphs[row, col].spines["top"].set_color("k")
        graphs[row, col].spines["right"].set_color("k")
        graphs[row, col].spines["left"].set_color("k")

        if row == 1:
            graphs[row, col].set_xlabel(
                "$\\textrm{Number of divisions}$", fontsize=label_size
            )
        else:
            graphs[row, col].tick_params(labelbottom=False)

        if col == 0:
            graphs[row, col].set_ylabel("$\\textrm{Probability}$", fontsize=label_size)
        else:
            graphs[row, col].tick_params(labelleft=False)

        if row == 0 and col == 1:
            graphs[row, col].legend(
                loc="best", facecolor="white", framealpha=1, fontsize=label_size
            )

    fig.savefig(f"DD-{folder[0]}.pdf")

    for row in range(2):
        for col in range(2):
            graphs[row][col].clear()
    fig.clear()
    plt.close(fig="all")
