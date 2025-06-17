# import traci
import libsumo as traci


import pickle
import itertools
from functools import partial
import xml.etree.ElementTree as ET
from deap import gp, creator, base, tools, algorithms
import operator
import random
import numpy as np

from network import get_network_data


class Bool(object):
    pass


def default_gp_params():
    class GP_params:
        def __init__(self):
            self.elitism_size = 1
            self.tournament_size = 7
            self.pop_size = 50
            self.cross_p = 0.8
            self.mut_p = 0.2
            self.n_generations = 50
            self.min_initial_tree_depth = 2
            self.max_initial_tree_depth = 5
            self.max_tree_depth = 7
            self.mut_new_tree_p = 0.001
            self.mut_subtree_min_depth = 0
            self.mut_subtree_max_depth = 2
            self.cross_tree_exchange_p = 0.1
            self.n_sub_trees = 2     # number of trees per individual
            self.use_prev_population = False

    return GP_params()


def evaluate_individual(individual, sumoCmd, toolbox, args,
                        simulation_step_limit=10000,
                        phase_check_period=10,
                        keep_gp_function_outputs=False):

    tl_functions = [toolbox.compile(expr=tree) for tree in individual]

    function_rs = tl_functions[0]
    function_left = tl_functions[1]

    network_data = get_network_data(args.network_folder_path)
    junction_logic_ids = network_data["junction_logic_ids"]
    junction_ids = network_data["junction_ids"]
    junction_detectors = network_data["junction_detectors"]
    junction_detectors_flipped = network_data["junction_detectors_flipped"]
    junction_optimised_phases_info = network_data["junction_optimised_phases_info"]

    traci.start(sumoCmd)

    junction_phases = {}
    junction_previous_phase = {}
    junction_current_phase_params = {}
    for junction in junction_ids:
        tls_id = junction_logic_ids[junction]
        logic = traci.trafficlight.getCompleteRedYellowGreenDefinition(tls_id)[0]
        junction_phases[junction] = logic.getPhases()
        junction_previous_phase[junction] = -1
        junction_current_phase_params[junction] = {
            "max_duration" : None,
            "min_duration" : None,
            "time_passed_since_phase_start" : 0
        }

    simulation_completed = True
    i = 0

    gp_function_outputs = {
        "function_rs": [],
        "function_left": []
    }

    while traci.simulation.getMinExpectedNumber() > 0:

        if i > simulation_step_limit:
            simulation_completed = False
            break

        i += 1

        traci.simulationStep()

        for junction in junction_ids:

            tls_id = junction_logic_ids[junction]
            current_phase = traci.trafficlight.getPhase(tls_id)
            current_phase_params = junction_current_phase_params[junction]

            if current_phase != junction_previous_phase[junction]:
                # print(f"phase: {current_phase}, time: {i}")
                junction_previous_phase[junction] = current_phase

                if current_phase not in junction_optimised_phases_info[junction]:
                    continue

                current_phase_info = junction_optimised_phases_info[junction][current_phase]
                current_phase_direction = current_phase_info["direction"]
                current_phase_type = current_phase_info["type"]

                if current_phase_direction == "north_south":
                    detectors = junction_detectors[junction]
                else:
                    detectors = junction_detectors_flipped[junction]

                if current_phase_type == "right_straight":
                    phase_function = function_rs
                else:
                    phase_function = function_left

                phases = junction_phases[junction]

                current_phase_params["max_duration"] = phases[current_phase].maxDur
                current_phase_params["min_duration"] = phases[current_phase].minDur
                current_phase_params["time_passed_since_phase_start"] = 0

            max_duration = current_phase_params["max_duration"]
            min_duration = current_phase_params["min_duration"]
            time_passed_since_phase_start = current_phase_params["time_passed_since_phase_start"]

            if time_passed_since_phase_start % phase_check_period == 0:
                if current_phase not in junction_optimised_phases_info[junction]:
                    continue

                detector_readings_by_type = {}

                for detector_type, detectors_list in detectors.items():
                    detector_readings = [traci.multientryexit.getLastStepVehicleNumber(d) for d in detectors_list]
                    readings_sum = sum(detector_readings)
                    detector_readings_by_type[detector_type] = readings_sum

                gp_output = phase_function(**detector_readings_by_type)
                if keep_gp_function_outputs:
                    if phase_function == function_rs:
                        gp_function_outputs["function_rs"].append(gp_output)
                    else:
                        gp_function_outputs["function_left"].append(gp_output)

                new_duration = gp_output

                if new_duration < 0:
                    new_duration = 0

                if time_passed_since_phase_start + new_duration < min_duration:
                    new_duration = min_duration - time_passed_since_phase_start - 1

                traci.trafficlight.setPhaseDuration(tls_id, new_duration)

            time_passed_since_phase_start += 1
            current_phase_params["time_passed_since_phase_start"] = time_passed_since_phase_start
            if time_passed_since_phase_start > max_duration:
                traci.trafficlight.setPhaseDuration(tls_id, 0)

    traci.close()

    if keep_gp_function_outputs:
        with open(args.gp_function_outputs_path, "wb") as f:
            pickle.dump(gp_function_outputs, f)

    if not simulation_completed:    # return large number as fitness (default 10000)
        return (simulation_step_limit,)

    tree = ET.parse(args.statistics_path)
    root = tree.getroot()

    trip_stats = root.find("vehicleTripStatistics")
    # if trip_stats is not None:
    #     for key, value in trip_stats.attrib.items():
    #         print(f"{key}: {value}")

    time_loss = float(trip_stats.get("timeLoss"))
    depart_delay = float(trip_stats.get("departDelay"))
    return (time_loss + depart_delay,)


def multy_tree_mutation(individual, toolbox, gp_params):
    new_individual = individual.copy()

    for i in range(len(individual)):
        r = random.random()
        if r < gp_params.mut_new_tree_p:
            new_individual[i] = toolbox.subTree()
        elif r < gp_params.mut_p:
            new_individual[i] = toolbox.mutate_tree(new_individual[i])[0]

    return creator.Individual(new_individual),


def cross_sub_trees(individual1, individual2, toolbox):
    new_individual1 = [None] * len(individual1)
    new_individual2 = [None] * len(individual2)

    for i in range(len(individual1)):
        tree1 = individual1[i]
        tree2 = individual2[i]
        new_individual1[i], new_individual2[i] = toolbox.mate_single_tree(tree1, tree2)

    return creator.Individual(new_individual1), creator.Individual(new_individual2)

def exchange_sub_trees(individual1, individual2):
    new_individual1 = individual1.copy()
    new_individual2 = individual2.copy()

    exc_index = random.randint(0, len(individual1) - 1)

    new_individual1[exc_index], new_individual2[exc_index] = new_individual2[exc_index], new_individual1[exc_index]

    return creator.Individual(new_individual1), creator.Individual(new_individual2)


def multy_tree_crossover(individual1, individual2, toolbox, gp_params):

    if random.random() < gp_params.cross_tree_exchange_p:
        return exchange_sub_trees(individual1, individual2)
    else:
        return cross_sub_trees(individual1, individual2, toolbox)


def gp_setup(sumoCmd, args, gp_params):

    def if_then_else(input, output1, output2):
        if input:
            return output1
        else:
            return output2

    network_data = get_network_data(args.network_folder_path)
    arg_names = {}
    for i, detector_type in enumerate(network_data["junction_detectors"]["0"].keys()):
        arg_names[f"ARG{i}"] = detector_type

    # Define primitive set
    pset = gp.PrimitiveSetTyped("MAIN", itertools.repeat(int,len(arg_names)), int) # provjeri jel radi
    pset.renameArguments(**arg_names)


    # Add basic arithmetic operators
    pset.addPrimitive(operator.add, [int, int], int)
    pset.addPrimitive(operator.sub, [int, int], int)
    pset.addPrimitive(operator.mul, [int, int], int)
    pset.addPrimitive(operator.and_, [Bool, Bool], Bool)
    pset.addPrimitive(operator.or_, [Bool, Bool], Bool)
    pset.addPrimitive(operator.not_, [Bool], Bool, name="not")
    pset.addPrimitive(operator.eq, [int, int], Bool)
    pset.addPrimitive(operator.gt, [int, int], Bool)
    pset.addPrimitive(operator.lt, [int, int], Bool)
    pset.addPrimitive(if_then_else, [Bool, int, int], int, name="if_then_else")

    # Add constants
    pset.addEphemeralConstant("const", partial(random.randint,-10, 10), int)
    pset.addTerminal(False, Bool)
    pset.addTerminal(True, Bool)

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)
    creator.create("SubIndividual", gp.PrimitiveTree)

    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=gp_params.min_initial_tree_depth, max_=gp_params.max_initial_tree_depth)
    toolbox.register("subTree", tools.initIterate, creator.SubIndividual, toolbox.expr)
    toolbox.register("subTreeList", tools.initRepeat, list, toolbox.subTree, n=gp_params.n_sub_trees)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.subTreeList)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    def selElitistAndTournament(individuals, pop_size, elitism_size, tournament_size):
        return (tools.selBest(individuals, elitism_size)
                + tools.selTournament(individuals, pop_size - elitism_size, tournsize=tournament_size))

    toolbox.register("evaluate", evaluate_individual, sumoCmd=sumoCmd, toolbox=toolbox, args=args)
    toolbox.register("select", selElitistAndTournament, elitism_size=gp_params.elitism_size, tournament_size=gp_params.tournament_size)
    toolbox.register("mate_single_tree", gp.cxOnePoint)
    toolbox.register("mate", multy_tree_crossover, toolbox=toolbox, gp_params=gp_params)
    toolbox.register("expr_mut", gp.genFull, min_=gp_params.mut_subtree_min_depth, max_=gp_params.mut_subtree_max_depth)
    toolbox.register("mutate_tree", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
    toolbox.register("mutate", multy_tree_mutation, toolbox=toolbox, gp_params=gp_params)

    toolbox.decorate("mutate_tree", gp.staticLimit(key=operator.attrgetter("height"), max_value=gp_params.max_tree_depth))
    toolbox.decorate("mate_single_tree", gp.staticLimit(key=operator.attrgetter("height"), max_value=gp_params.max_tree_depth))

    pop = toolbox.population(n=gp_params.pop_size)
    hof = tools.HallOfFame(1)

    if gp_params.use_prev_population:
        with open(args.population_path, "rb") as f:
            pop = pickle.load(f)
        with open(args.hof_path, "rb") as f:
            hof = pickle.load(f)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    return pop, toolbox, hof, stats

def run_GP(sumoCmd, args, gp_params=None):

    if gp_params is None:
        gp_params = default_gp_params()

    pop, toolbox, hof, stats = gp_setup(sumoCmd, args, gp_params)

    # vjerojatnost mutacije postavlja se na 1 jer se koristi posebna funkcija za mutaciju
    # koja sama osigurava da se mutacija odvija s vjerojatnosti gp_params.mut_p
    pop, log = algorithms.eaSimple(
        pop,
        toolbox,
        gp_params.cross_p,
        1,
        gp_params.n_generations,
        stats,
        halloffame=hof,
        verbose=True)

    return pop, stats, hof


