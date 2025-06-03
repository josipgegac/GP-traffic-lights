import argparse
import os
import pickle
import random

from simulation import run_simulation
from gp import run_GP


def parse_args():
    parser = argparse.ArgumentParser(description='Model train script')

    parser.add_argument('seed', type=int, nargs='?', default=None, help='Set seed')
    parser.add_argument('network_folder_path', type=str, nargs='?', default="../networks/cross3ltl", help='Path to network folder')
    parser.add_argument('sumo_config_filename', type=str, nargs='?', default="test.sumocfg", help='Name of network config file')
    parser.add_argument('statistics_filename', type=str, nargs='?', default="statistics.xml", help='Name of statistics output file')
    parser.add_argument('population_filename', type=str, nargs='?', default="population.pkl", help='Name of population output file')
    parser.add_argument('hof_filename', type=str, nargs='?', default="hof.pkl", help='Name of hof output file')

    args = parser.parse_args()

    sumo_config_path = os.path.join(args.network_folder_path, args.sumo_config_filename)
    statistics_path = os.path.join(args.network_folder_path, args.statistics_filename)
    population_path = os.path.join(args.network_folder_path, args.population_filename)
    hof_path = os.path.join(args.network_folder_path, args.hof_filename)

    args.sumo_config_path = sumo_config_path
    args.statistics_path = statistics_path
    args.population_path = population_path
    args.hof_path = hof_path

    return args


if __name__ == '__main__':
    args = parse_args()

    sumoCmd = [
        "sumo", "-c", args.sumo_config_path,
        "--statistic-output", args.statistics_path
    ]

    trip_stats = run_simulation(sumoCmd, args.statistics_path)
    # for key, value in trip_stats.items():
    #     print(f"{key}: {value}")

    pop, stats, hof = run_GP(sumoCmd, args)
    # for tree in hof[0]:
    #     print(tree)

    with open(args.population_path, "wb") as f:
        pickle.dump(pop, f)

    with open(args.hof_path, "wb") as f:
        pickle.dump(hof, f)
