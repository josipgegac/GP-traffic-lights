# import traci
import argparse
import os

import libsumo as traci
import xml.etree.ElementTree as ET

from gp import gp_setup, default_gp_params, evaluate_individual
from network import get_network_data


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


def run_simulation(sumoCmd, statistics_path):

    network_data = get_network_data()

    traci.start(sumoCmd)

    i = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        i += 1

        traci.simulationStep()

    traci.close()


    tree = ET.parse(statistics_path)
    root = tree.getroot()

    trip_stats = root.find('vehicleTripStatistics')
    # if trip_stats is not None:
    #     for key, value in trip_stats.attrib.items():
    #         print(f"{key}: {value}")



    return trip_stats


def run_simulation_with_gp(sumoCmd, individual, sumo_config_path, statistics_path):

    args = parse_args()
    params = default_gp_params()

    sumoCmd = [
        "sumo", "-c", sumo_config_path,
        "--statistic-output", statistics_path
    ]

    _, toolbox, _, _ = gp_setup(sumoCmd, args, params)

    evaluate_individual(individual, sumoCmd, toolbox, args)

    tree = ET.parse(statistics_path)
    root = tree.getroot()

    trip_stats = root.find('vehicleTripStatistics')
    if trip_stats is not None:
        for key, value in trip_stats.attrib.items():
            print(f"{key}: {value}")

    return trip_stats