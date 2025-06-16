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
            self.cross_p = 0.6
            self.mut_p = 0.4
            self.n_generations = 50
            self.min_tree_size = 2
            self.max_tree_size = 5
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


def multy_tree_mutation(ind, toolbox, new_tree_p=0.001):
    new_ind = ind.copy()
    mut_index = random.randint(0, len(ind)-1)

    if random.random() < new_tree_p:
        new_ind[mut_index] = toolbox.subTree()
    else:
        new_ind[mut_index] = toolbox.mutate_tree(new_ind[mut_index])[0]
    return creator.Individual(new_ind),


def cross_sub_trees(ind1, ind2, toolbox):
    new_ind1 = [None] * len(ind1)
    new_ind2 = [None] * len(ind2)

    for i in range(len(ind1)):
        tree1 = ind1[i]
        tree2 = ind2[i]
        new_ind1[i], new_ind2[i] = toolbox.mate_single_tree(tree1, tree2)

    return creator.Individual(new_ind1), creator.Individual(new_ind2)

def exchange_sub_trees(ind1, ind2, toolbox):
    new_ind1 = ind1.copy()
    new_ind2 = ind2.copy()

    exc_index = random.randint(0, len(ind1)-1)

    new_ind1[exc_index], new_ind2[exc_index] = new_ind2[exc_index], new_ind1[exc_index]

    return creator.Individual(new_ind1), creator.Individual(new_ind2)


def multy_tree_crossover(ind1, ind2, toolbox, tree_exchange_p=0.1):

    if random.random() < tree_exchange_p:
        return exchange_sub_trees(ind1, ind2, toolbox)
    else:
        return cross_sub_trees(ind1, ind2, toolbox)


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
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=gp_params.min_tree_size, max_=gp_params.max_tree_size)
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
    toolbox.register("mate", multy_tree_crossover, toolbox=toolbox)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
    toolbox.register("mutate_tree", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
    toolbox.register("mutate", multy_tree_mutation, toolbox=toolbox)

    toolbox.decorate("mutate_tree", gp.staticLimit(key=operator.attrgetter("height"), max_value=7))
    toolbox.decorate("mate_single_tree", gp.staticLimit(key=operator.attrgetter("height"), max_value=7))

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

    pop, log = algorithms.eaSimple(
        pop,
        toolbox,
        gp_params.cross_p,
        gp_params.mut_p,
        gp_params.n_generations,
        stats,
        halloffame=hof,
        verbose=True)

    return pop, stats, hof


