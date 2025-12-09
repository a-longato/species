# SPECIES: Simulating Populations Evolving Complex Interactions in Ecological Systems
This is the repository for the coding project for the course of Optimization for AI, first year of the Master of Science in Data Science and Artificial Intelligence (a.y. 2025/2026, UniTS). The project has been developed by Alessandro Longato.

## Overview
The objective of **SPECIES** are to simulate natural selection in a closed environment, analyze the survival strategies of prey and predator, and observe emergent behavior (evolution,
population cycles). To do so, two populations of agents (herbivores and carnivores) are free to compete for resources and evolve generation after generation in a grid environment. Genetic evolution happens as agents pass traits to offspring with a fixed mutation probability. Lotka-Volterra population cycles and evolutionary "arms races" emerge as results of interactions between populations. A Streamlit user interface allows users to observe the simulations in real-time, while helper scripts are used to gather and process data. For more information about the results, refer to `presentation.pdf`.

The project is divided into three distinct experimental configurations:
*   **`baseline/`**: Standard simulation with one population of Herbivores and one population of Carnivores.
*   **`2herb/`**: Introduces a second species of Herbivores (Unarmored vs. Armored) to test niche differentiation.
*   **`2herb_2carn/`**: A complex scenario with two species of Herbivores and two species of Carnivores competing simultaneously.

## How to Run
First, clone this repository.
```sh
git clone https://github.com/a-longato/species.git
cd species
```
Then, install the required Python packages. It is recommended to use a virtual environment.
```sh
pip install streamlit numpy matplotlib
```
To run a specific experiment, navigate to the folder of the experiment you wish to observe and run the corresponding Streamlit app. The baseline experiment is used as example below.
```sh    
cd baseline
streamlit run simulation.py
```
Feel free to change the configuration file and run the simulation with different parameters.
