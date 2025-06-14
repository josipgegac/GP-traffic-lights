# import traci
import libsumo as traci


import itertools
from functools import partial
import time
import xml.etree.ElementTree as ET
from deap import gp, creator, base, tools, algorithms
import operator
import math
import random
import numpy as np

import matplotlib.pyplot as plt
import networkx as nx

import pygraphviz as pgv



def get_network_data():

    junction_ids = ["0"]
    detector_ids = traci.multientryexit.getIDList()
    junction_detectors = {
        "0" : {
            "north_south_rs" : ["0_north_right", "0_north_straight", "0_south_right", "0_south_straight"],
            "north_south_left" : ["0_north_left", "0_south_left"],
            "west_east_rs" : ["0_west_right", "0_west_straight", "0_east_right", "0_east_straight"],
            "west_east_left" : ["0_west_left", "0_east_left"],
        }
    }

    junction_logic_ids = {"0" : "0"}
    tls_id = "0"

    network_data = {"junction_ids": junction_ids,
                    "junction_detectors": junction_detectors,
                    "junction_logic_ids": junction_logic_ids,
                    "detector_ids": detector_ids,
                    "tls_id": tls_id}

    return network_data


def run_simulation(sumoCmd):

    traci.start(sumoCmd)

    network_data = get_network_data()

    i = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        i += 1

        traci.simulationStep()

    traci.close()


    tree = ET.parse('statistics.xml')
    root = tree.getroot()

    trip_stats = root.find('vehicleTripStatistics')
    # if trip_stats is not None:
    #     for key, value in trip_stats.attrib.items():
    #         print(f"{key}: {value}")

    return trip_stats


def evaluate_individual(individual, sumoCmd, toolbox, simulation_step_limit=10000):

    tl_functions = [toolbox.compile(expr=tree) for tree in individual]

    phase_functions = {
        0 : tl_functions[0],
        2 : tl_functions[1],
        4 : tl_functions[2],
        6 : tl_functions[3]
    }

    traci.start(sumoCmd)

    network_data = get_network_data()
    tls_id = network_data["tls_id"]
    junction_ids = network_data["junction_ids"]
    junction_detectors = network_data["junction_detectors"]

    logic = traci.trafficlight.getCompleteRedYellowGreenDefinition(tls_id)[0]
    phases = logic.getPhases()

    simulation_completed = True
    i = 0
    previous_phase=-1
    while traci.simulation.getMinExpectedNumber() > 0:

        if i > simulation_step_limit:
            simulation_completed = False
            break

        i += 1

        traci.simulationStep()

        current_phase = traci.trafficlight.getPhase(tls_id)
        if current_phase != previous_phase:     # phase length is defined at only at the start of the phase
            for junction in junction_ids:

                detector_readings_by_type = {}

                for detector_type, detectors_list in junction_detectors[junction].items():
                    detector_readings = [traci.multientryexit.getLastStepVehicleNumber(d) for d in detectors_list]
                    readings_sum = sum(detector_readings)
                    detector_readings_by_type[detector_type] = readings_sum

                if current_phase in phase_functions.keys():
                    phase_function = phase_functions[current_phase]
                    phase_duration = phases[current_phase].duration
                    max_duration = phases[current_phase].maxDur
                    min_duration = phases[current_phase].minDur

                    new_duration = phase_duration + phase_function(**detector_readings_by_type)
                    if new_duration > max_duration:
                        new_duration = max_duration
                    if new_duration < min_duration:
                        new_duration = min_duration

                    traci.trafficlight.setPhaseDuration(tls_id, new_duration)

            previous_phase = current_phase

    traci.close()

    if not simulation_completed:    # return large number as fitness (default 10000)
        return (simulation_step_limit,)

    tree = ET.parse('statistics.xml')
    root = tree.getroot()

    trip_stats = root.find('vehicleTripStatistics')
    # if trip_stats is not None:
    #     for key, value in trip_stats.attrib.items():
    #         print(f"{key}: {value}")

    time_loss = float(trip_stats.get("timeLoss"))
    return (time_loss,)


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


def run_GP(sumoCmd, seed=None):

    tournament_size = 7
    pop_size = 50
    cross_p = 0.6
    mut_p = 0.4
    n_generations = 100
    min_tree_size = 2
    max_tree_size = 5
    n_sub_trees = 4     # number of trees per individual
    use_prev_best = False

    def if_then_else(input, output1, output2):
        if input:
            return output1
        else:
            return output2


    # Define primitive set
    pset = gp.PrimitiveSetTyped("MAIN", itertools.repeat(int,4), int)  # 2 inputs

    traci.start(sumoCmd)
    network_data = get_network_data()
    arg_names = {}
    for i, detector_type in enumerate(network_data["junction_detectors"]["0"].keys()):
        arg_names[f"ARG{i}"] = detector_type
    pset.renameArguments(**arg_names)
    traci.close()

    # Add basic arithmetic operators
    pset.addPrimitive(operator.add, [int, int], int)
    pset.addPrimitive(operator.sub, [int, int], int)
    pset.addPrimitive(operator.mul, [int, int], int)
    pset.addPrimitive(operator.and_, [bool, bool], bool)
    pset.addPrimitive(operator.or_, [bool, bool], bool)
    pset.addPrimitive(operator.not_, [bool], bool, name="not")
    pset.addPrimitive(operator.eq, [int, int], bool)
    pset.addPrimitive(operator.gt, [int, int], bool)
    pset.addPrimitive(operator.lt, [int, int], bool)
    pset.addPrimitive(if_then_else, [bool, int, int], int, name="if_then_else")

    # Add constants
    pset.addEphemeralConstant("const", partial(random.randint,-10, 10), int)
    pset.addTerminal(False, bool)
    pset.addTerminal(True, bool)

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)
    creator.create("SubIndividual", gp.PrimitiveTree)

    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=min_tree_size, max_=max_tree_size)
    toolbox.register("subTree", tools.initIterate, creator.SubIndividual, toolbox.expr)
    toolbox.register("subTreeList", tools.initRepeat, list, toolbox.subTree, n=n_sub_trees)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.subTreeList)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    def selElitistAndTournament(individuals, pop_size, elitism_size=1, tournsize=3):
        return (tools.selBest(individuals, elitism_size)
                + tools.selTournament(individuals, pop_size - elitism_size, tournsize=tournsize))

    toolbox.register("evaluate", evaluate_individual, sumoCmd=sumoCmd, toolbox=toolbox)
    toolbox.register("select", selElitistAndTournament, elitism_size=1, tournsize=tournament_size)
    toolbox.register("mate_single_tree", gp.cxOnePoint)
    toolbox.register("mate", multy_tree_crossover, toolbox=toolbox)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
    toolbox.register("mutate_tree", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
    toolbox.register("mutate", multy_tree_mutation, toolbox=toolbox)

    # if seed is not None:
    #     seed = random.seed(42)

    pop = toolbox.population(n=pop_size)

    if use_prev_best:
        with open("best_individual.txt") as f:
            trees = f.readlines()

            individual = [gp.PrimitiveTree.from_string(tree.strip(), pset) for tree in trees]
            individual = creator.Individual(individual)

            # evaluate_individual(individual, sumoCmd, toolbox)

            pop[0] = individual

    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop, log = algorithms.eaSimple(pop, toolbox, cross_p, mut_p, n_generations, stats, halloffame=hof, verbose=True)

    return pop, stats, hof

if __name__ == '__main__':
    sumoCmd = [
        "sumo", "-c", "test.sumocfg",
        "--statistic-output", "statistics.xml"
    ]

    trip_stats = run_simulation(sumoCmd)
    # for key, value in trip_stats.items():
    #     print(f"{key}: {value}")

    pop, stats, hof = run_GP(sumoCmd)
    for tree in hof[0]:
        print(tree)

