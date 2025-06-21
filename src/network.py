import copy
import json
import os


def cross1ltl_data():

    junction_ids = ["0"]
    junction_detectors = {
        "0": {
            "north_south_rs": ["0_north", "0_south"],
            "north_south_left": ["0_north", "0_south"],
            "west_east_rs": ["0_west", "0_east"],
            "west_east_left": ["0_west", "0_east"],
        }
    }

    junction_detectors_flipped = copy.deepcopy(junction_detectors)
    for junction, detectors in junction_detectors_flipped.items():
        detectors["north_south_rs"], detectors["west_east_rs"] = detectors["west_east_rs"], detectors["north_south_rs"]
        detectors["north_south_left"], detectors["west_east_left"] = detectors["west_east_left"], detectors["north_south_left"]

    junction_logic_ids = {"0": "0"}

    junction_optimised_phases_info = {
        "0": {
            0: {"direction": "north_south",
                "type": "right_straight",
                "type_index": 0},
            4: {"direction": "west_east",
                "type": "right_straight",
                "type_index": 0},
        }
    }

    junction_functions_list_index = {"0": 0}
    junction_function_counts = 1

    network_data = {
        "junction_ids": junction_ids,
        "junction_detectors": junction_detectors,
        "junction_logic_ids": junction_logic_ids,
        "junction_detectors_flipped": junction_detectors_flipped,
        "junction_optimised_phases_info": junction_optimised_phases_info,
        "junction_functions_list_index": junction_functions_list_index,
        "junction_function_counts": junction_function_counts,
    }

    return network_data


def cross3ltl_data():

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
                "type": "right_straight",
                "type_index": 0},
            2: {"direction": "north_south",
                "type": "left",
                "type_index": 1},
            4: {"direction": "west_east",
                "type": "right_straight",
                "type_index": 0},
            6: {"direction": "west_east",
                "type": "left",
                "type_index": 1},
        }
    }

    junction_functions_list_index = {"0": 0}
    junction_function_counts = 2

    network_data = {
        "junction_ids": junction_ids,
        "junction_detectors": junction_detectors,
        "junction_logic_ids": junction_logic_ids,
        "junction_detectors_flipped": junction_detectors_flipped,
        "junction_optimised_phases_info": junction_optimised_phases_info,
        "junction_functions_list_index": junction_functions_list_index,
        "junction_function_counts": junction_function_counts,
    }

    return network_data

def identical_intersections_data():
    junction_ids = ["0", "1"]
    junction_detectors = {
        "0": {
            "north_south_rs": ["0_north_right", "0_north_straight", "0_south_right", "0_south_straight"],
            "north_south_left": ["0_north_left", "0_south_left"],
            "west_east_rs": ["0_west_right", "0_west_straight", "0_east_right", "0_east_straight"],
            "west_east_left": ["0_west_left", "0_east_left"],
        },
        "1": {
            "north_south_rs": ["1_north_right", "1_north_straight", "1_south_right", "1_south_straight"],
            "north_south_left": ["1_north_left", "1_south_left"],
            "west_east_rs": ["1_west_right", "1_west_straight", "1_east_right", "1_east_straight"],
            "west_east_left": ["1_west_left", "1_east_left"],
        }
    }

    junction_detectors_flipped = copy.deepcopy(junction_detectors)
    for junction, detectors in junction_detectors_flipped.items():
        detectors["north_south_rs"], detectors["west_east_rs"] = detectors["west_east_rs"], detectors["north_south_rs"]
        detectors["north_south_left"], detectors["west_east_left"] = detectors["west_east_left"], detectors[
            "north_south_left"]

    junction_logic_ids = {"0": "0", "1": "1"}

    junction_optimised_phases_info = {
        "0": {
            0: {"direction": "north_south",
                "type": "right_straight",
                "type_index": 0},
            2: {"direction": "north_south",
                "type": "left",
                "type_index": 1},
            4: {"direction": "west_east",
                "type": "right_straight",
                "type_index": 0},
            6: {"direction": "west_east",
                "type": "left",
                "type_index": 1},
        },
        "1": {
            0: {"direction": "north_south",
                "type": "right_straight",
                "type_index": 0},
            2: {"direction": "north_south",
                "type": "left",
                "type_index": 1},
            4: {"direction": "west_east",
                "type": "right_straight",
                "type_index": 0},
            6: {"direction": "west_east",
                "type": "left",
                "type_index": 1},
        }
    }

    junction_functions_list_index = {"0": 0, "1": 0}
    junction_function_counts = 2

    network_data = {
        "junction_ids": junction_ids,
        "junction_detectors": junction_detectors,
        "junction_logic_ids": junction_logic_ids,
        "junction_detectors_flipped": junction_detectors_flipped,
        "junction_optimised_phases_info": junction_optimised_phases_info,
        "junction_functions_list_index": junction_functions_list_index,
        "junction_function_counts": junction_function_counts,
    }

    return network_data


def different_intersections_data():
    junction_ids = ["0", "1"]
    # kljucevi se moraju podudarati za sva krizanja jer su oni imena ulaza u gp programe,
    # a postoji samo jedan set primitiva (ogranicenje DEAP-a)
    junction_detectors = {
        "0": {
            "north_south_rs": ["0_north_right", "0_north_straight", "0_south_right", "0_south_straight"],
            "north_south_left": ["0_north_left", "0_south_left"],
            "west_east_rs": ["0_west_right", "0_west_straight", "0_east_right", "0_east_straight"],
            "west_east_left": ["0_west_left", "0_east_left"],
        },
        "1": {
            "north_south_rs": ["1_north", "1_south"],
            "north_south_left": ["1_north", "1_south"],
            "west_east_rs": ["1_west", "1_east"],
            "west_east_left": ["1_west", "1_east"],
        }
    }

    junction_detectors_flipped = copy.deepcopy(junction_detectors)
    for junction, detectors in junction_detectors_flipped.items():
        detectors["north_south_rs"], detectors["west_east_rs"] = detectors["west_east_rs"], detectors["north_south_rs"]
        detectors["north_south_left"], detectors["west_east_left"] = detectors["west_east_left"], detectors["north_south_left"]

    junction_logic_ids = {"0": "0", "1": "1"}

    junction_optimised_phases_info = {
        "0": {
            0: {"direction": "north_south",
                "type": "right_straight",
                "type_index": 0},
            2: {"direction": "north_south",
                "type": "left",
                "type_index": 1},
            4: {"direction": "west_east",
                "type": "right_straight",
                "type_index": 0},
            6: {"direction": "west_east",
                "type": "left",
                "type_index": 1},
        },
        "1": {
            0: {"direction": "north_south",
                "type": "right_straight",
                "type_index": 0},
            4: {"direction": "west_east",
                "type": "right_straight",
                "type_index": 0},
        }
    }

    junction_functions_list_index = {"0": 0, "1": 1}
    junction_function_counts = [2, 1]

    network_data = {
        "junction_ids": junction_ids,
        "junction_detectors": junction_detectors,
        "junction_logic_ids": junction_logic_ids,
        "junction_detectors_flipped": junction_detectors_flipped,
        "junction_optimised_phases_info": junction_optimised_phases_info,
        "junction_functions_list_index": junction_functions_list_index,
        "junction_function_counts": junction_function_counts,
    }

    return network_data


def bologna_data():
    junction_ids = ["219", "221", "210", "235"]
    # kljucevi se moraju podudarati za sva krizanja jer su oni imena ulaza u gp programe,
    # a postoji samo jedan set primitiva (ogranicenje DEAP-a)
    junction_detectors = {
        "0": {
            "north_south_rs": ["0_north_right", "0_north_straight", "0_south_right", "0_south_straight"],
            "north_south_left": ["0_north_left", "0_south_left"],
            "west_east_rs": ["0_west_right", "0_west_straight", "0_east_right", "0_east_straight"],
            "west_east_left": ["0_west_left", "0_east_left"],
        },
        "1": {
            "north_south_rs": ["1_north", "1_south"],
            "north_south_left": ["1_north", "1_south"],
            "west_east_rs": ["1_west", "1_east"],
            "west_east_left": ["1_west", "1_east"],
        }
    }

    junction_detectors_flipped = copy.deepcopy(junction_detectors)
    for junction, detectors in junction_detectors_flipped.items():
        detectors["north_south_rs"], detectors["west_east_rs"] = detectors["west_east_rs"], detectors["north_south_rs"]
        detectors["north_south_left"], detectors["west_east_left"] = detectors["west_east_left"], detectors["north_south_left"]

    junction_logic_ids = {"0": "0", "1": "1"}

    junction_optimised_phases_info = {
        "0": {
            0: {"direction": "north_south",
                "type": "right_straight",
                "type_index": 0},
            2: {"direction": "north_south",
                "type": "left",
                "type_index": 1},
            4: {"direction": "west_east",
                "type": "right_straight",
                "type_index": 0},
            6: {"direction": "west_east",
                "type": "left",
                "type_index": 1},
        },
        "1": {
            0: {"direction": "north_south",
                "type": "right_straight",
                "type_index": 0},
            4: {"direction": "west_east",
                "type": "right_straight",
                "type_index": 0},
        }
    }

    junction_functions_list_index = {"0": 0, "1": 1}
    junction_function_counts = [2, 1]

    network_data = {
        "junction_ids": junction_ids,
        "junction_detectors": junction_detectors,
        "junction_logic_ids": junction_logic_ids,
        "junction_detectors_flipped": junction_detectors_flipped,
        "junction_optimised_phases_info": junction_optimised_phases_info,
        "junction_functions_list_index": junction_functions_list_index,
        "junction_function_counts": junction_function_counts,
    }

    return network_data


def get_network_data(network_folder_path):

    if "cross1ltl" in network_folder_path:
        return cross1ltl_data()
    if "cross3ltl" in network_folder_path:
        return cross3ltl_data()
    if "2_identical_intersections" in network_folder_path:
        return identical_intersections_data()
    if "2_different_intersections" in network_folder_path:
        return different_intersections_data()

    return None




if __name__ == "__main__":
    network_folder_path = "../networks/cross3ltl"
    sumo_config_filename = "test.sumocfg"
    statistics_filename = "statistics.xml"

    network_data_path = os.path.join(network_folder_path, "network_data.json")
    sumo_config_path = os.path.join(network_folder_path, sumo_config_filename)
    statistics_path = os.path.join(network_folder_path, statistics_filename)

    sumoCmd = [
        "sumo", "-c", sumo_config_path,
        "--statistic-output", statistics_path
    ]

    network_data = get_network_data(network_folder_path)

    with open(network_data_path, "w") as f:
        json.dump(network_data, f, indent=4)
