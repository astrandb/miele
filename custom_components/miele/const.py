"""Constants for the Miele integration."""

DOMAIN = "miele"
VERSION = "0.0.12"

MIELE_API = "https://api.mcs3.miele.com/v1"
OAUTH2_AUTHORIZE = "https://api.mcs3.miele.com/thirdparty/login"
OAUTH2_TOKEN = "https://api.mcs3.miele.com/thirdparty/token"


# Define appliance types
WASHING_MACHINE = 1
TUMBLE_DRYER = 2
DISHWASHER = 7
OVEN = 12
OVEN_MICROWAVE = 13
HOB_HIGHLIGHT = 14
STEAM_OVEN = 15
MICROWAVE = 16
COFFEE_SYSTEM = 17
HOOD = 18
FRIDGE = 19
FREEZER = 20
FRIDGE_FREEZER = 21
ROBOT_VACUUM_CLEANER = 23
WASHER_DRYER = 24
DISH_WARMER = 25
HOB_INDUCTION = 27
STEAM_OVEN_COMBI = 31
WINE_CABINET = 32
WINE_CONDITIONING_UNIT = 33
WINE_STORAGE_CONDITIONING_UNIT = 34
STEAM_OVEN_MICRO = 45
DIALOG_OVEN = 67
WINE_CABINET_FREEZER = 68

APPLIANCE_TYPES = {
    WASHING_MACHINE: "washing_machine",
    TUMBLE_DRYER: "tumble_dryer",
    DISHWASHER: "dishwasher",
    OVEN: "oven",
    OVEN_MICROWAVE: "oven_microwave",
    HOB_HIGHLIGHT: "hob_highlight",
    STEAM_OVEN: "steam_oven",
    MICROWAVE: "microwave",
    COFFEE_SYSTEM: "coffee_system",
    HOOD: "hood",
    FRIDGE: "fridge",
    FREEZER: "freezer",
    FRIDGE_FREEZER: "fridge_freezer",
    ROBOT_VACUUM_CLEANER: "robot_vacuum_cleaner",
    WASHER_DRYER: "washer_dryer",
    DISH_WARMER: "dish_warmer",
    HOB_INDUCTION: "hob_induction",
    STEAM_OVEN_COMBI: "steam_oven_combi",
    WINE_CABINET: "wine_cabinet",
    WINE_CONDITIONING_UNIT: "wine_conditioning_unit",
    WINE_STORAGE_CONDITIONING_UNIT: "wine_storage_conditioning_unit",
    STEAM_OVEN_MICRO: "steam_oven_micro",
    DIALOG_OVEN: "dialog_oven",
    WINE_CABINET_FREEZER: "wine_cabinet_freezer",
}

# Define various states
STATE_STATUS = {
    0: "reserved",
    1: "off",
    2: "on",
    3: "programmed",
    4: "waiting_to_start",
    5: "running",
    6: "pause",
    7: "program_ended",
    8: "failure",
    9: "program_interrupted",
    10: "idle",
    11: "rinse_hold",
    12: "service",
    13: "superfreezing",
    14: "supercooling",
    15: "superheating",
    146: "supercooling_superfreezing",
    255: "not_connected",
}

STATE_PROGRAM_TYPE = {
    0: "normal_operation_mode",
    1: "own_program",
    2: "automatic_program",
    3: "cleaning_care_program",
    4: "cleaning_care_program",  # used by washer-dryer
}

STATE_PROGRAM_PHASE = {
    # Washing Machine
    0: "not_running",  # Returned by the API when the machine is switched off entirely.
    256: "not_running",
    257: "pre_wash",
    258: "soak",
    259: "pre_wash",
    260: "main_wash",
    261: "rinse",
    262: "rinse_hold",
    263: "main_wash",
    264: "cooling_down",
    265: "drain",
    266: "spin",
    267: "anti_crease",
    268: "finished",
    269: "venting",
    270: "starch_stop",
    271: "freshen_up_and_moisten",
    272: "steam_smoothing",
    279: "hygiene",
    280: "drying",
    285: "disinfecting",
    295: "steam_smoothing",
    # Dryer
    512: "not_running",
    513: "program_running",
    514: "drying",
    515: "machine_iron",
    516: "hand_iron",
    517: "normal",
    518: "normal_plus",
    519: "cooling_down",
    520: "hand_iron",
    521: "anti_crease",
    522: "finished",
    523: "extra_dry",
    524: "hand_iron",
    526: "moisten",
    527: "thermo_spin",
    528: "timed_drying",
    529: "warm_air",
    530: "steam_smoothing",
    531: "comfort_cooling",
    532: "rinse_out_lint",
    533: "rinses",
    534: "smoothing",
    538: "slightly_dry",
    539: "safety_cooling",
    # Dishwasher
    1792: "not_running",
    1793: "reactivating",
    1794: "pre_dishwash",
    1795: "main_dishwash",
    1796: "rinse",
    1797: "interim_rinse",
    1798: "final_rinse",
    1799: "drying",
    1800: "finished",
    1801: "pre_dishwash",
}

WASHING_MACHINE_PROGRAM_ID = {
    1: "cottons",
    3: "minimum_iron",
    4: "delicates",
    8: "woollens",
    9: "silks",
    17: "starch",
    18: "rinse",
    21: "drain_spin",
    22: "curtains",
    23: "shirts",
    24: "denim",
    27: "proofing",
    29: "sportswear",
    31: "automatic_plus",
    37: "outerwear",
    39: "pillows",
    46: "warm_air",  # washer-dryer
    48: "rinse_out_lint",  # washer-dryer
    50: "dark_garments",
    52: "separate_rinse_starch",
    53: "first_wash",
    69: "cottons_hygiene",
    75: "steam_care",  # washer-dryer
    76: "freshen_up",  # washer-dryer
    77: "trainers",
    91: "clean_machine",
    95: "down_duvets",
    122: "express_20",
    123: "denim",
    129: "down_filled_items",
    133: "cottons_eco",
    146: "quick_power_wash",
}
DISHWASHER_PROGRAM_ID = {
    0: "not_running",  # Returned by the API when the machine is switched off entirely.
    26: "intensive",
    27: "maintenance",  # or maintenance_program?
    28: "eco",
    30: "normal",
    31: "automatic",
    32: "automatic",  # sources disagree on ID
    34: "solar_save",
    35: "gentle",
    36: "extra_quiet",
    37: "hygiene",
    38: "quick_power_wash",
    42: "tall_items",
}
TUMBLE_DRYER_PROGRAM_ID = {
    10: "automatic_plus",
    20: "cottons",
    23: "cottons_hygiene",
    30: "minimum_iron",
    31: "gentle_minimum_iron",
    40: "woollens_handcare",
    50: "delicates",
    60: "warm_air",
    70: "cool_air",
    80: "express_20",
    90: "cottons",
    100: "gentle_smoothing",
    120: "proofing",
    130: "denim",
    131: "gentle_denim",
    150: "sportswear",
    160: "outerwear",
    170: "silks_handcare",
    190: "standard_pillows",
    220: "basket_program",
    240: "smoothing",
}
OVEN_PROGRAM_ID = {
    6: "eco_fan_heat",
    7: "auto_roast",
    10: "full_grill",
    11: "economy_grill",
    13: "fan_plus",
    14: "intensive_bake",
    24: "conventional_heat",
    25: "top_heat",
    29: "fan_grill",
    31: "bottom_heat",
}

STATE_PROGRAM_ID = {
    WASHING_MACHINE: WASHING_MACHINE_PROGRAM_ID,
    TUMBLE_DRYER: TUMBLE_DRYER_PROGRAM_ID,
    DISHWASHER: DISHWASHER_PROGRAM_ID,
    OVEN: OVEN_PROGRAM_ID,
    WASHER_DRYER: WASHING_MACHINE_PROGRAM_ID,
}

# Possible actions
PROCESS_ACTIONS = {
    "start": 1,
    "stop": 2,
    "pause": 3,
    "start_superfreezing": 4,
    "stop_superfreezing": 5,
    "start_supercooling": 6,
    "stop_supercooling": 7,
}

AMBIENT_COLORS = {
    "white",
    "blue",
    "red",
    "yellow",
    "orange",
    "green",
    "pink",
    "purple",
    "turquoise",
}
