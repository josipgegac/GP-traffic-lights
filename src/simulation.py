# import traci
import argparse
import os

import libsumo as traci
import xml.etree.ElementTree as ET

from gp import gp_setup, default_gp_params, evaluate_individual, evaluate_individual_2


def run_simulation(sumoCmd, statistics_path, simulation_step_limit: int = 10000):

    traci.start(sumoCmd)

    i = 0
    while traci.simulation.getMinExpectedNumber() > 0:

        if i >= simulation_step_limit:
            print("Stopping simulation.")
            break

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


def run_simulation_with_gp(sumoCmd, individual, args, keep_gp_function_outputs=False):

    params = default_gp_params()

    _, toolbox, _, _ = gp_setup(sumoCmd, args, params)

    evaluate_individual_2(individual, sumoCmd, toolbox, args, keep_gp_function_outputs=keep_gp_function_outputs)

    tree = ET.parse(args.statistics_path)
    root = tree.getroot()

    trip_stats = root.find('vehicleTripStatistics')
    # if trip_stats is not None:
    #     for key, value in trip_stats.attrib.items():
    #         print(f"{key}: {value}")

    return trip_stats