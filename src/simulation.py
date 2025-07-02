# import traci
import argparse
import os

import libsumo as traci
import xml.etree.ElementTree as ET

from gp import gp_setup, default_gp_params, evaluate_individual


def run_simulation(sumoCmd, statistics_path, simulation_step_limit: int = 50000):

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

    return trip_stats


def run_simulation_with_gp(sumoCmd, individual, args, keep_gp_function_outputs=False, simulation_step_limit=15000):

    params = default_gp_params()

    _, toolbox, _, _ = gp_setup(sumoCmd, args, params)

    fintess_value = evaluate_individual(individual, sumoCmd, toolbox, args,
                                        phase_check_period=args.phase_check_period,
                                        keep_gp_function_outputs=keep_gp_function_outputs,
                                        simulation_step_limit=simulation_step_limit)
    if fintess_value == simulation_step_limit:
        print("\nSimulation did not finish.\n")

    tree = ET.parse(args.statistics_path)
    root = tree.getroot()

    trip_stats = root.find('vehicleTripStatistics')

    return trip_stats