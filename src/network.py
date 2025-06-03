import copy
import json
import os


def get_network_data():
    junction_ids = ["0"]
    junction_detectors = {
        "0": {
            "north_south_rs": ["0_north_right", "0_north_straight", "0_south_right", "0_south_straight"],
            "north_south_left": ["0_north_left", "0_south_left"],
            "west_east_rs": ["0_west_right", "0_west_straight", "0_east_right", "0_east_straight"],
            "west_east_left": ["0_west_left", "0_east_left"],
        }
    }

    junction_detectors_flipped = copy.deepcopy(junction_detectors)
    for junction, detectors in junction_detectors_flipped.items():
        detectors["north_south_rs"], detectors["west_east_rs"] = detectors["west_east_rs"], detectors["north_south_rs"]
        detectors["north_south_left"], detectors["west_east_left"] = detectors["west_east_left"], detectors[
            "north_south_left"]

    junction_logic_ids = {"0": "0"}

    junction_optimised_phases_info = {
        "0": {
            0: {"direction": "north_south",
                "type": "right_straight"},
            2: {"direction": "north_south",
                "type": "left"},
            4: {"direction": "west_east",
                "type": "right_straight"},
            6: {"direction": "west_east",
                "type": "left"},
        }
    }

    network_data = {
        "junction_ids": junction_ids,
        "junction_detectors": junction_detectors,
        "junction_logic_ids": junction_logic_ids,
        "junction_detectors_flipped": junction_detectors_flipped,
        "junction_optimised_phases_info": junction_optimised_phases_info
    }

    return network_data


if __name__ == "__main__":
    network_folder_path = "../networks/cross3ltl"
    sumo_config_filename = "test.sumocfg"
    statistics_filename = "statistics.xml"

    network_data_path = os.path.join(network_folder_path, "network_data.txt")
    sumo_config_path = os.path.join(network_folder_path, sumo_config_filename)
    statistics_path = os.path.join(network_folder_path, statistics_filename)

    sumoCmd = [
        "sumo", "-c", sumo_config_path,
        "--statistic-output", statistics_path
    ]

    network_data = get_network_data()

    with open(network_data_path, "w") as f:
        json.dump(network_data, f, indent=4)
