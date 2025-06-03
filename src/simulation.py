# import traci
import libsumo as traci
import xml.etree.ElementTree as ET
from network import get_network_data

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