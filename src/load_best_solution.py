import argparse
import os
import pickle

import re
import graphviz
import pandas as pd
from deap import gp, creator, base



from simulation import run_simulation_with_gp


def parse_args():
    parser = argparse.ArgumentParser(description='GP evaluate script')

    parser.add_argument('seed', type=int, nargs='?', default=None, help='Set seed')
    parser.add_argument('network_folder_path', type=str, nargs='?', default="../networks/bologna_period_10/1 - 200 gen", help='Path to network folder')
    parser.add_argument('sumo_config_filename', type=str, nargs='?', default="test.sumocfg", help='Name of the network config file')
    parser.add_argument('statistics_filename', type=str, nargs='?', default="statistics.xml", help='Name of the simulation statistics output file')
    parser.add_argument('population_filename', type=str, nargs='?', default="population.pkl", help='Name of the file that contains the final population')
    parser.add_argument('hof_filename', type=str, nargs='?', default="hof.pkl", help='Name of the file that contains the final hof (best individual)')
    parser.add_argument('gp_function_outputs', type=str, nargs='?', default="gp_function_outputs.pkl", help='Name of the file with outputs of gp functions')
    parser.add_argument('phase_check_period', type=int, nargs='?', default=10, help='How often does the controller check if the phase should continue; recomended to use the same value during GP training and evaluation')
    parser.add_argument('visualise_trees', type=bool, nargs='?', default=True, help='If true tree visualisations get saved as .png files in "visualisations" folder inside the network folder')
    parser.add_argument('print_gp_function_outputs', type=bool, nargs='?', default=False, help='Print all GP function outputs obtained during the simulation, as well as some statistics')

    args = parser.parse_args()

    sumo_config_path = os.path.join(args.network_folder_path, args.sumo_config_filename)
    statistics_path = os.path.join(args.network_folder_path, args.statistics_filename)
    population_path = os.path.join(args.network_folder_path, args.population_filename)
    hof_path = os.path.join(args.network_folder_path, args.hof_filename)
    gp_function_outputs_path = os.path.join(args.network_folder_path, args.gp_function_outputs)

    args.sumo_config_path = sumo_config_path
    args.statistics_path = statistics_path
    args.population_path = population_path
    args.hof_path = hof_path
    args.gp_function_outputs_path = gp_function_outputs_path

    return args


def visualise_tree(tree, filename, format="png", view=True):
    nodes, edges, labels = gp.graph(tree)

    g = graphviz.Graph(format=format)
    for node in nodes:
        g.node(str(node), str(labels[node]))
    for src, tgt in edges:
        g.edge(str(src), str(tgt))

    g.render(filename, cleanup=True, view=view)


if __name__ == '__main__':

    args = parse_args()

    with open(args.hof_path, 'rb') as f:
        hof = pickle.load(f)

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

    best_individual = hof[0]

    if args.visualise_trees:
        if not isinstance(best_individual, gp.PrimitiveTree):
            for i in range(len(best_individual)):
                sub_individual = best_individual[i]
                if not isinstance(sub_individual, gp.PrimitiveTree):
                    for j in range(len(sub_individual)):
                        tree = sub_individual[j]
                        visualisation_path = os.path.join(args.network_folder_path, f"visualisations/{i}/{j}")
                        visualise_tree(tree, visualisation_path, view=False)
                else:
                    visualisation_path = os.path.join(args.network_folder_path, f"visualisations/{i}")
                    visualise_tree(sub_individual, visualisation_path, view=False)
        else:
            visualisation_path = os.path.join(args.network_folder_path, "visualisations/0")
            visualise_tree(best_individual, visualisation_path, view=False)


    sumoCmd = [
        "sumo-gui", "-c", args.sumo_config_path,
        "--statistic-output", args.statistics_path
    ]

    trip_stats = run_simulation_with_gp(sumoCmd, best_individual, args, keep_gp_function_outputs=args.print_gp_function_outputs)
    print(f"timeLoss: {trip_stats.get('timeLoss')}")
    print(f"departDelay: {trip_stats.get('departDelay')}")
    print(f"timeLoss + departDelay: {float(trip_stats.get('timeLoss')) + float(trip_stats.get('departDelay'))}")

    if args.print_gp_function_outputs:
        with open(args.gp_function_outputs_path, "rb") as f:
            gp_function_outputs = pickle.load(f)

        for junction, outputs in gp_function_outputs.items():
            print(f"junction: {junction}\n==================================================================")
            if not isinstance(outputs[0], list):
                print(f"outputs = {outputs}")
                s = pd.Series(outputs)
                print(f"unique values: {s.nunique()}")
                print(f"values greater than period: {sum(s > args.phase_check_period)}")
                print(s.describe())
                # print(s.value_counts())
                print()
            else:
                for i, l in enumerate(outputs):
                    print(f"function: {i}")
                    print(f"\toutputs = {l}")
                    s = pd.Series(l)
                    print(f"\tunique values: {s.nunique()}")
                    print(f"\tvalues greater than period: {sum(s > args.phase_check_period)}")
                    print("\t" + str(s.describe()).replace('\n', '\n\t'))
                    # print("\t" + str(s.value_counts()))
                    print()
            print()
