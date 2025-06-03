# import traci
import libsumo as traci

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
            "north-south" : ["0_north", "0_south"],
            "west-east" : ["0_west", "0_east"]
        }
    }

    junction_logic_ids = {"0" : "0"}
    tls_id = "0"

    return junction_ids, junction_detectors, junction_logic_ids, detector_ids, tls_id


def run_simulation(sumoCmd):

    traci.start(sumoCmd)

    junction_ids, junction_detectors, junction_logic_ids, detector_ids, tls_id = get_network_data()

    i = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        i += 1

        traci.simulationStep()

        current_phase = traci.trafficlight.getPhase(tls_id)

        for junction in junction_ids:
            n_s_detectors = junction_detectors[junction]["north-south"]
            n_s_readings = [traci.multientryexit.getLastStepVehicleNumber(d) for d in n_s_detectors]
            n_s_sum = sum(n_s_readings)

            w_e_detectors = junction_detectors[junction]["west-east"]
            w_e_readings = [traci.multientryexit.getLastStepVehicleNumber(d) for d in w_e_detectors]
            w_e_sum = sum(w_e_readings)


            if (n_s_sum >= w_e_sum + 5) and (current_phase == 0):
                traci.trafficlight.setPhaseDuration(tls_id, 1)

            if (w_e_sum >= n_s_sum + 5) and (current_phase == 4):
                traci.trafficlight.setPhaseDuration(tls_id, 1)

    traci.close()


    tree = ET.parse('statistics.xml')
    root = tree.getroot()

    trip_stats = root.find('vehicleTripStatistics')
    # if trip_stats is not None:
    #     for key, value in trip_stats.attrib.items():
    #         print(f"{key}: {value}")

    return trip_stats


individual_occurances = dict()

def evaluate_individual(individual, sumoCmd, compileFunc):

    individual_occurances[str(individual)] = individual_occurances.get(str(individual), 0) + 1

    func = compileFunc(expr=individual)

    traci.start(sumoCmd)

    junction_ids, junction_detectors, junction_logic_ids, detector_ids, tls_id = get_network_data()

    logic = traci.trafficlight.getCompleteRedYellowGreenDefinition(tls_id)[0]
    phases = logic.getPhases()

    i = 0
    previous_phase=-1
    while traci.simulation.getMinExpectedNumber() > 0:
        i += 1

        traci.simulationStep()

        current_phase = traci.trafficlight.getPhase(tls_id)
        if current_phase != previous_phase:
            for junction in junction_ids:
                n_s_detectors = junction_detectors[junction]["north-south"]
                n_s_readings = [traci.multientryexit.getLastStepVehicleNumber(d) for d in n_s_detectors]
                n_s_sum = sum(n_s_readings)

                w_e_detectors = junction_detectors[junction]["west-east"]
                w_e_readings = [traci.multientryexit.getLastStepVehicleNumber(d) for d in w_e_detectors]
                w_e_sum = sum(w_e_readings)

                if current_phase == 0:
                    phase_duration = phases[0].duration
                    max_duration = phases[0].maxDur
                    min_duration = phases[0].minDur

                    new_duration = phase_duration + func(n_s=n_s_sum, w_e=w_e_sum)
                    if new_duration > max_duration:
                        new_duration = max_duration
                    if new_duration < min_duration:
                        new_duration = min_duration

                    traci.trafficlight.setPhaseDuration(tls_id, new_duration)

                if current_phase == 4:
                    phase_duration = phases[4].duration
                    max_duration = phases[4].maxDur
                    min_duration = phases[4].minDur

                    new_duration = phase_duration - func(n_s=n_s_sum, w_e=w_e_sum)
                    if new_duration > max_duration:
                        new_duration = max_duration
                    if new_duration < min_duration:
                        new_duration = min_duration

                    traci.trafficlight.setPhaseDuration(tls_id, new_duration)


            previous_phase = current_phase


        # for junction in junction_ids:
        #     n_s_detectors = junction_detectors[junction]["north-south"]
        #     n_s_readings = [traci.multientryexit.getLastStepVehicleNumber(d) for d in n_s_detectors]
        #     n_s_sum = sum(n_s_readings)
        #
        #     w_e_detectors = junction_detectors[junction]["west-east"]
        #     w_e_readings = [traci.multientryexit.getLastStepVehicleNumber(d) for d in w_e_detectors]
        #     w_e_sum = sum(w_e_readings)
        #
        #     if (n_s_sum >= w_e_sum + 5) and (current_phase == 0):
        #         traci.trafficlight.setPhaseDuration(tls_id, 1)
        #
        #     if (w_e_sum >= n_s_sum + 5) and (current_phase == 4):
        #         traci.trafficlight.setPhaseDuration(tls_id, 1)

    traci.close()

    tree = ET.parse('statistics.xml')
    root = tree.getroot()

    trip_stats = root.find('vehicleTripStatistics')
    # if trip_stats is not None:
    #     for key, value in trip_stats.attrib.items():
    #         print(f"{key}: {value}")

    time_loss = float(trip_stats.get("timeLoss"))
    return (time_loss,)


def run_GP(sumoCmd, seed=None):

    tournament_size = 3
    pop_size = 100
    cross_p = 0.6
    mut_p = 0.4
    n_generations = 50

    def if_then_else(input, output1, output2):
        if input:
            return output1
        else:
            return output2

    def and_f(x,y):
        return x and y

    def or_f(x,y):
        return x or y

    # Define primitive set
    pset = gp.PrimitiveSetTyped("MAIN", [int, int], int)  # 2 inputs
    pset.renameArguments(ARG0='n_s', ARG1='w_e')

    # Add basic arithmetic operators
    pset.addPrimitive(operator.add, [int, int], int)
    pset.addPrimitive(operator.sub, [int, int], int)
    pset.addPrimitive(operator.mul, [int, int], int)
    # pset.addPrimitive(and_f, [bool, bool], bool, name="and")
    # pset.addPrimitive(or_f,[bool, bool], bool, name="or")
    pset.addPrimitive(operator.and_, [bool, bool], bool)
    pset.addPrimitive(operator.or_, [bool, bool], bool)
    # pset.addPrimitive(lambda x, y: x and y, [bool, bool], bool, name="and")
    # pset.addPrimitive(lambda x, y: x or y, [bool, bool], bool, name="or")
    pset.addPrimitive(operator.not_, [bool], bool, name="not")
    pset.addPrimitive(operator.eq, [int, int], bool)
    pset.addPrimitive(operator.gt, [int, int], bool)
    pset.addPrimitive(operator.lt, [int, int], bool)
    # pset.addPrimitive(lambda cond, x, y: x if cond else y, [bool, int, int], int, name="if_then_else")
    pset.addPrimitive(if_then_else, [bool, int, int], int, name="if_then_else")

    # Add constants
    pset.addEphemeralConstant("const", partial(random.randint,-10, 10), int)
    pset.addTerminal(False, bool)
    pset.addTerminal(True, bool)

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=2, max_=4)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    def selElitistAndTournament(individuals, pop_size, elitism_size=1, tournsize=3):
        return (tools.selBest(individuals, elitism_size)
                + tools.selTournament(individuals, pop_size - elitism_size, tournsize=tournsize))

    toolbox.register("evaluate", evaluate_individual, sumoCmd=sumoCmd, compileFunc=toolbox.compile)
    toolbox.register("select", selElitistAndTournament, elitism_size=1, tournsize=tournament_size)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

    if seed is not None:
        seed = random.seed(42)

    pop = toolbox.population(n=pop_size)
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

    # trip_stats = run_simulation(sumoCmd)
    # for key, value in trip_stats.items():
    #     print(f"{key}: {value}")
    #
    # pop, stats, hof = run_GP(sumoCmd)
    # print(hof[0])

    def if_then_else(input, output1, output2):
        if input:
            return output1
        else:
            return output2

    # Define primitive set
    pset = gp.PrimitiveSetTyped("MAIN", [int, int], int)  # 2 inputs
    pset.renameArguments(ARG0='n_s', ARG1='w_e')

    # Add basic arithmetic operators
    pset.addPrimitive(operator.add, [int, int], int)
    pset.addPrimitive(operator.sub, [int, int], int)
    pset.addPrimitive(operator.mul, [int, int], int)
    # pset.addPrimitive(and_f, [bool, bool], bool, name="and")
    # pset.addPrimitive(or_f,[bool, bool], bool, name="or")
    pset.addPrimitive(operator.and_, [bool, bool], bool)
    pset.addPrimitive(operator.or_, [bool, bool], bool)
    # pset.addPrimitive(lambda x, y: x and y, [bool, bool], bool, name="and")
    # pset.addPrimitive(lambda x, y: x or y, [bool, bool], bool, name="or")
    pset.addPrimitive(operator.not_, [bool], bool, name="not")
    pset.addPrimitive(operator.eq, [int, int], bool)
    pset.addPrimitive(operator.gt, [int, int], bool)
    pset.addPrimitive(operator.lt, [int, int], bool)
    # pset.addPrimitive(lambda cond, x, y: x if cond else y, [bool, int, int], int, name="if_then_else")
    pset.addPrimitive(if_then_else, [bool, int, int], int, name="if_then_else")

    # Add constants
    pset.addEphemeralConstant("const", partial(random.randint, -10, 10), int)
    pset.addTerminal(False, bool)
    pset.addTerminal(True, bool)

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=2, max_=4)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    with open("best_individual.txt") as f:
        tree = f.readline().strip()

        individual = gp.PrimitiveTree.from_string(tree, pset)
        evaluate_individual(individual, sumoCmd, toolbox.compile)



