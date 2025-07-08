import argparse
import os
import pickle

from simulation import run_simulation
from gp import run_GP, default_gp_params


def parse_args():
    parser = argparse.ArgumentParser(description='GP run script')

    parser.add_argument('seed', type=int, nargs='?', default=None, help='Set seed')
    parser.add_argument('network_folder_path', type=str, nargs='?', default="../networks/2_identical_intersections_period_5/1 - 100 gen", help='Path to network folder')
    parser.add_argument('sumo_config_filename', type=str, nargs='?', default="test.sumocfg", help='Name of the network config file')
    parser.add_argument('statistics_filename', type=str, nargs='?', default="statistics.xml", help='Name of the simulation statistics output file')
    parser.add_argument('population_filename', type=str, nargs='?', default="population.pkl", help='Name of the file that contains the final population')
    parser.add_argument('hof_filename', type=str, nargs='?', default="hof.pkl", help='Name of the file that contains the final hof (best individual)')
    parser.add_argument('gp_function_outputs', type=str, nargs='?', default="gp_function_outputs.pkl", help='Name of the file with outputs of gp functions')
    parser.add_argument('phase_check_period', type=int, nargs='?', default=10, help='How often does the controller check if the phase should continue; recomended to use the same value during GP training and evaluation')
    parser.add_argument('save_all_generations', type=bool, nargs='?', default=False, help='Save hof and population for all generations')

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


if __name__ == '__main__':
    args = parse_args()

    sumoCmd = [
        "sumo", "-c", args.sumo_config_path,
        "--statistic-output", args.statistics_path
    ]

    trip_stats = run_simulation(sumoCmd, args.statistics_path)
    print(f"timeLoss: {trip_stats.get('timeLoss')}")
    print(f"departDelay: {trip_stats.get('departDelay')}")
    print(f"timeLoss + departDelay: {float(trip_stats.get('timeLoss')) + float(trip_stats.get('departDelay'))}")

    if not args.save_all_generations:
        pop, stats, hof = run_GP(sumoCmd, args)

        with open(args.population_path, "wb") as f:
            pickle.dump(pop, f)

        with open(args.hof_path, "wb") as f:
            pickle.dump(hof, f)

    else:
        gp_params = default_gp_params()
        n_generations = gp_params.n_generations

        gp_params.n_generations = 1
        for i in range(n_generations):
            print(f"Generation {i+1}")
            pop, stats, hof = run_GP(sumoCmd, args, gp_params)

            gp_output_path = os.path.join(args.network_folder_path, "gp_output")

            if not os.path.isdir(gp_output_path):
                os.makedirs(gp_output_path)

            hof_path = os.path.join(gp_output_path, f"{args.hof_filename.replace('.pkl', f'{i+1}.pkl')}")
            population_path = os.path.join(gp_output_path, f"{args.population_filename.replace('.pkl', f'{i+1}.pkl')}")

            with open(population_path, "wb") as f:
                pickle.dump(pop, f)

            with open(hof_path, "wb") as f:
                pickle.dump(hof, f)

            args.population_path = population_path
            args.hof_path = hof_path

            if i == 0:
                gp_params.use_prev_population = True




