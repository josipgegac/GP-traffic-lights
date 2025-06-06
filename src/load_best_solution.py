import os
import pickle

from simulation import run_simulation_with_gp

if __name__ == '__main__':
    network_folder_path = "../networks/cross3ltl-5"
    hof_path = os.path.join(network_folder_path, "hof.pkl")
    sumo_config_path = os.path.join(network_folder_path, "test.sumocfg")
    statistics_path = os.path.join(network_folder_path, "statistics.xml")

    with open(hof_path, 'rb') as f:
        hof = pickle.load(f)

    best_individual = hof[0]
    for tree in best_individual:
        print(tree)

    sumoCmd = [
        "sumo", "-c", sumo_config_path,
        "--statistic-output", statistics_path
    ]

    trip_stats = run_simulation_with_gp(sumoCmd, best_individual, sumo_config_path, statistics_path)
    # for key, value in trip_stats.items():
    #     print(f"{key}: {value}")