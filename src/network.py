import copy
import json
import os


def cross1ltl_data():

    junction_ids = ["0"]
    junction_detectors_north_south = {
        "0": {
            "north_south_rs": ["0_north", "0_south"],
            "north_south_left": ["0_north", "0_south"],
            "west_east_rs": ["0_west", "0_east"],
            "west_east_left": ["0_west", "0_east"],
        }
    }

    junction_detectors_west_east = copy.deepcopy(junction_detectors_north_south)
    for junction, detectors in junction_detectors_west_east.items():
        detectors["north_south_rs"], detectors["west_east_rs"] = detectors["west_east_rs"], detectors["north_south_rs"]
        detectors["north_south_left"], detectors["west_east_left"] = detectors["west_east_left"], detectors["north_south_left"]

    junction_detectors = [junction_detectors_north_south, junction_detectors_west_east]

    junction_logic_ids = {"0": "0"}

    junction_optimised_phases_info = {
        "0": {
            0: {"direction": "north_south",
                "direction_index": 0,
                "type": "right_straight",
                "type_index": 0},
            4: {"direction": "west_east",
                "direction_index": 1,
                "type": "right_straight",
                "type_index": 0},
        }
    }

    junction_functions_list_index = {"0": 0}
    junction_function_counts = 1

    tls_program_index = 0

    network_data = {
        "junction_ids": junction_ids,
        "junction_detectors": junction_detectors,
        "junction_logic_ids": junction_logic_ids,
        "junction_optimised_phases_info": junction_optimised_phases_info,
        "junction_functions_list_index": junction_functions_list_index,
        "junction_function_counts": junction_function_counts,
        "tls_program_index": tls_program_index,
    }

    return network_data


def cross3ltl_data():

    junction_ids = ["0"]
    junction_detectors_north_south = {
        "0": {
            "north_south_rs": ["0_north_right", "0_north_straight", "0_south_right", "0_south_straight"],
            "north_south_left": ["0_north_left", "0_south_left"],
            "west_east_rs": ["0_west_right", "0_west_straight", "0_east_right", "0_east_straight"],
            "west_east_left": ["0_west_left", "0_east_left"],
        }
    }

    junction_detectors_west_east = copy.deepcopy(junction_detectors_north_south)
    for junction, detectors in junction_detectors_west_east.items():
        detectors["north_south_rs"], detectors["west_east_rs"] = detectors["west_east_rs"], detectors["north_south_rs"]
        detectors["north_south_left"], detectors["west_east_left"] = detectors["west_east_left"], detectors["north_south_left"]

    junction_detectors = [junction_detectors_north_south, junction_detectors_west_east]

    junction_logic_ids = {"0": "0"}

    junction_optimised_phases_info = {
        "0": {
            0: {"direction": "north_south",
                "direction_index": 0,
                "type": "right_straight",
                "type_index": 0},
            2: {"direction": "north_south",
                "direction_index": 0,
                "type": "left",
                "type_index": 1},
            4: {"direction": "west_east",
                "direction_index": 1,
                "type": "right_straight",
                "type_index": 0},
            6: {"direction": "west_east",
                "direction_index": 1,
                "type": "left",
                "type_index": 1},
        }
    }

    junction_functions_list_index = {"0": 0}
    junction_function_counts = 2

    tls_program_index = 0

    network_data = {
        "junction_ids": junction_ids,
        "junction_detectors": junction_detectors,
        "junction_logic_ids": junction_logic_ids,
        "junction_optimised_phases_info": junction_optimised_phases_info,
        "junction_functions_list_index": junction_functions_list_index,
        "junction_function_counts": junction_function_counts,
        "tls_program_index": tls_program_index,
    }

    return network_data

def identical_intersections_data():
    junction_ids = ["0", "1"]
    junction_detectors_north_south = {
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

    junction_detectors_west_east = copy.deepcopy(junction_detectors_north_south)
    for junction, detectors in junction_detectors_west_east.items():
        detectors["north_south_rs"], detectors["west_east_rs"] = detectors["west_east_rs"], detectors["north_south_rs"]
        detectors["north_south_left"], detectors["west_east_left"] = detectors["west_east_left"], detectors["north_south_left"]

    junction_detectors = [junction_detectors_north_south, junction_detectors_west_east]

    junction_logic_ids = {"0": "0", "1": "1"}

    junction_optimised_phases_info = {
        "0": {
            0: {"direction": "north_south",
                "direction_index": 0,
                "type": "right_straight",
                "type_index": 0},
            2: {"direction": "north_south",
                "direction_index": 0,
                "type": "left",
                "type_index": 1},
            4: {"direction": "west_east",
                "direction_index": 1,
                "type": "right_straight",
                "type_index": 0},
            6: {"direction": "west_east",
                "direction_index": 1,
                "type": "left",
                "type_index": 1},
        },
        "1": {
            0: {"direction": "north_south",
                "direction_index": 0,
                "type": "right_straight",
                "type_index": 0},
            2: {"direction": "north_south",
                "direction_index": 0,
                "type": "left",
                "type_index": 1},
            4: {"direction": "west_east",
                "direction_index": 1,
                "type": "right_straight",
                "type_index": 0},
            6: {"direction": "west_east",
                "direction_index": 1,
                "type": "left",
                "type_index": 1},
        }
    }

    junction_functions_list_index = {"0": 0, "1": 0}
    junction_function_counts = 2

    tls_program_index = 0

    network_data = {
        "junction_ids": junction_ids,
        "junction_detectors": junction_detectors,
        "junction_logic_ids": junction_logic_ids,
        "junction_optimised_phases_info": junction_optimised_phases_info,
        "junction_functions_list_index": junction_functions_list_index,
        "junction_function_counts": junction_function_counts,
        "tls_program_index": tls_program_index,
    }

    return network_data


def different_intersections_data():
    junction_ids = ["0", "1"]
    # kljucevi se moraju podudarati za sva krizanja jer su oni imena ulaza u gp programe,
    # a postoji samo jedan set primitiva (ogranicenje DEAP-a)
    junction_detectors_north_south = {
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

    junction_detectors_west_east = copy.deepcopy(junction_detectors_north_south)
    for junction, detectors in junction_detectors_west_east.items():
        detectors["north_south_rs"], detectors["west_east_rs"] = detectors["west_east_rs"], detectors["north_south_rs"]
        detectors["north_south_left"], detectors["west_east_left"] = detectors["west_east_left"], detectors["north_south_left"]

    junction_detectors = [junction_detectors_north_south, junction_detectors_west_east]

    junction_logic_ids = {"0": "0", "1": "1"}

    junction_optimised_phases_info = {
        "0": {
            0: {"direction": "north_south",
                "direction_index": 0,
                "type": "right_straight",
                "type_index": 0},
            2: {"direction": "north_south",
                "direction_index": 0,
                "type": "left",
                "type_index": 1},
            4: {"direction": "west_east",
                "direction_index": 1,
                "type": "right_straight",
                "type_index": 0},
            6: {"direction": "west_east",
                "direction_index": 1,
                "type": "left",
                "type_index": 1},
        },
        "1": {
            0: {"direction": "north_south",
                "direction_index": 0,
                "type": "right_straight",
                "type_index": 0},
            4: {"direction": "west_east",
                "direction_index": 1,
                "type": "right_straight",
                "type_index": 0},
        }
    }

    junction_functions_list_index = {"0": 0, "1": 1}
    junction_function_counts = [2, 1]

    tls_program_index = 0

    network_data = {
        "junction_ids": junction_ids,
        "junction_detectors": junction_detectors,
        "junction_logic_ids": junction_logic_ids,
        "junction_optimised_phases_info": junction_optimised_phases_info,
        "junction_functions_list_index": junction_functions_list_index,
        "junction_function_counts": junction_function_counts,
        "tls_program_index": tls_program_index,
    }

    return network_data


def bologna_data():
    junction_ids = ["219", "210", "221", "235"]
    # kljucevi se moraju podudarati za sva krizanja jer su oni imena ulaza u gp programe,
    # a postoji samo jedan set primitiva (ogranicenje DEAP-a)
    junction_detectors_north = {
        "219": {
            "north_rs": ["219_t0", "219_t1", "219_t2"],
            "south_rs": ["219_b0", "219_b3"],
            "north_left": [], # prazna lista znaci da ce nema tih detektora i vrijednost ce uvijek biti 0
            "south_left": ["219_b1", "219_b2", "219_b4"],
            "west_rs": ["219_l0", "219_l1"],
            "east_rs": ["219_r0", "219_r1"],
            "west_left": ["219_l2"],
            "east_left": ["219_r2"],
        },
        "210": {
            # ne optimiraju se lijeve faze pa sve kombiniraju svi detektori u smjerovima north-south i west-east te onda
            # efektivno postoje samo dvije grupe detektora
            # ovo se radi kako se ne bi trebali definirati posebni psetovi za svako raskrizje
            "north_rs": ["210_t0", "210_t1", "210_t2", "210_b0", "210_b1", "210_b2"],
            "south_rs": ["210_t0", "210_t1", "210_t2", "210_b0", "210_b1", "210_b2"],
            "north_left": ["210_t0", "210_t1", "210_t2", "210_b0", "210_b1", "210_b2"],
            "south_left": ["210_t0", "210_t1", "210_t2", "210_b0", "210_b1", "210_b2"],

            "west_rs": ["210_l0", "210_l1", "210_l2", "210_l3", "210_l4", "210_l5", "210_r1"],
            "east_rs": ["210_l0", "210_l1", "210_l2", "210_l3", "210_l4", "210_l5", "210_r1"],
            "west_left": ["210_l0", "210_l1", "210_l2", "210_l3", "210_l4", "210_l5", "210_r1"],
            "east_left": ["210_l0", "210_l1", "210_l2", "210_l3", "210_l4", "210_l5", "210_r1"],
        },
        "221": {
            # vrijedi isto kao kod "210"
            "north_rs": ["221_t0", "221_t1", "221_t2", "221_b0", "221_b1", "221_b2"],
            "south_rs": ["221_t0", "221_t1", "221_t2", "221_b0", "221_b1", "221_b2"],
            "north_left": ["221_t0", "221_t1", "221_t2", "221_b0", "221_b1", "221_b2"],
            "south_left": ["221_t0", "221_t1", "221_t2", "221_b0", "221_b1", "221_b2"],

            "west_rs": ["221_l0", "221_l1", "221_l2", "221_l3", "221_l4", "221_l5", "221_l6", "221_l7", "221_l8", "221_l9"],
            "east_rs": ["221_l0", "221_l1", "221_l2", "221_l3", "221_l4", "221_l5", "221_l6", "221_l7", "221_l8", "221_l9"],
            "west_left": ["221_l0", "221_l1", "221_l2", "221_l3", "221_l4", "221_l5", "221_l6", "221_l7", "221_l8", "221_l9"],
            "east_left": ["221_l0", "221_l1", "221_l2", "221_l3", "221_l4", "221_l5", "221_l6", "221_l7", "221_l8", "221_l9"],
        },
        "235": {
            "north_rs": ["235_t0", "235_t1", "235_t2"],
            "south_rs": ["235_b0"],
            "north_left": [],  # prazna lista znaci da ce nema tih detektora i vrijednost ce uvijek biti 0
            "south_left": ["235_b1", "235_b2"],
            "west_rs": ["235_l0"],
            "east_rs": ["235_r0", "235_r1", "235_r2", "235_r3"],
            "west_left": [],
            "east_left": [],
        },

    }

    junction_detectors_south = copy.deepcopy(junction_detectors_north)
    for junction, detectors in junction_detectors_south.items():
        detectors["north_rs"], detectors["south_rs"] = detectors["south_rs"], detectors["north_rs"]
        detectors["north_left"], detectors["south_left"] = detectors["south_left"], detectors["north_left"]
        detectors["west_rs"], detectors["east_rs"] = detectors["east_rs"], detectors["west_rs"]
        detectors["west_left"], detectors["east_left"] = detectors["east_left"], detectors["west_left"]

    junction_detectors_west = copy.deepcopy(junction_detectors_north)
    for junction, detectors in junction_detectors_west.items():
        detectors["north_rs"], detectors["south_rs"], detectors["west_rs"], detectors["east_rs"] = (
            detectors["west_rs"], detectors["east_rs"], detectors["south_rs"], detectors["north_rs"])
        detectors["north_left"], detectors["south_left"], detectors["west_left"], detectors["east_left"] = (
            detectors["west_left"], detectors["east_left"], detectors["south_left"], detectors["north_left"])

    junction_detectors_east = copy.deepcopy(junction_detectors_west)
    for junction, detectors in junction_detectors_east.items():
        detectors["north_rs"], detectors["south_rs"] = detectors["south_rs"], detectors["north_rs"]
        detectors["north_left"], detectors["south_left"] = detectors["south_left"], detectors["north_left"]
        detectors["west_rs"], detectors["east_rs"] = detectors["east_rs"], detectors["west_rs"]
        detectors["west_left"], detectors["east_left"] = detectors["east_left"], detectors["west_left"]

    # sadrzi razlicite orijentacije detektora, tj "okrenuta" raskrizja
    junction_detectors = [junction_detectors_north, junction_detectors_west, junction_detectors_south, junction_detectors_east]

    junction_logic_ids = {"219": "219", "210": "210", "221": "221", "235": "235"}

    junction_optimised_phases_info = {
        "219": {
            0: {"direction": "west",
                "direction_index": 1,
                "type": "left",
                "type_index": 1},
            3: {"direction": "west",
                "direction_index": 1,
                "type": "right_straight",
                "type_index": 0},
            5: {"direction": "east",
                "direction_index": 3,
                "type": "left",
                "type_index": 1},
            8: {"direction": "north",
                "direction_index": 0,
                "type": "right_straight",
                "type_index": 0},
            11: {"direction": "south",
                "direction_index": 2,
                "type": "left",
                "type_index": 1},
        },
        "210": {
            0: {"direction": "west",
                "direction_index": 1,
                "type": "right_straight",
                "type_index": 0},
            4: {"direction": "north",
                "direction_index": 0,
                "type": "right_straight",
                "type_index": 0},
        },
        "221": {
            0: {"direction": "north",
                "direction_index": 0,
                "type": "right_straight",
                "type_index": 0},
            3: {"direction": "west",
                "direction_index": 1,
                "type": "right_straight",
                "type_index": 0},
        },
        "235": {
            0: {"direction": "north",
                "direction_index": 0,
                "type": "right_straight",
                "type_index": 0},
            2: {"direction": "south",
                "direction_index": 2,
                "type": "left",
                "type_index": 1},
            8: {"direction": "west",
                "direction_index": 1,
                "type": "right_straight",
                "type_index": 0},
        },
    }

    junction_functions_list_index = {"219": 0, "210": 1, "221": 2, "235": 3}
    junction_function_counts = [2, 1, 1, 2]
    tls_program_index = 1

    network_data = {
        "junction_ids": junction_ids,
        "junction_detectors": junction_detectors,
        "junction_logic_ids": junction_logic_ids,
        "junction_optimised_phases_info": junction_optimised_phases_info,
        "junction_functions_list_index": junction_functions_list_index,
        "junction_function_counts": junction_function_counts,
        "tls_program_index": tls_program_index,
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
    if "bologna" in network_folder_path:
        return bologna_data()

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
