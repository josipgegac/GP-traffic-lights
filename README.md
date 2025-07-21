# GP-traffic-lights

Create conda environment:
```shell
conda env create --file package-list.yml
```
These exact versions of all SUMO-related packages, as well as version 1.20.0 of the SUMO simulator,
are required in order to have the exact same results when running simulations.
Other versions will have similar but slightly different results.

Additionally, install package graphviz for tree visualizations. Good luck.

The script run_gp.py is used to run the genetic algorithm, which saves the population and best individual.
The script load_best_solution.py is used to evaluate the best individuals.
Check parse_args functions for argument explanations.

The script create_routes.sh is used to generate random routes for a specific network.
