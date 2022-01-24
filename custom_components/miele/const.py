"""Constants for the Miele integration."""

DOMAIN = "miele"
VERSION = "0.0.3"

MIELE_API = "https://api.mcs3.miele.com/v1"
OAUTH2_AUTHORIZE = "https://api.mcs3.miele.com/thirdparty/login"
OAUTH2_TOKEN = "https://api.mcs3.miele.com/thirdparty/token"

STATE_STATUS = {
    0: "reserved",
    1: "off",
    2: "on",
    3: "programmed",
    4: "programmed_waiting_to_start",
    5: "running",
    6: "pause",
    7: "end_programmed",
    8: "failure",
    9: "programme interrupted",
    10: "idle",
    11: "rinse hold",
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
}

STATE_PROGRAM_ID = {
    1: "cottons",
    3: "minimum_iron",
    4: "delicates",
    8: "wool",
    9: "silk",
    21: "empty_spin",
    23: "dress_shirts",
    27: "impregnate",
    29: "sportswear",
    31: "automatic_plus",
    37: "outdoor",
    38: "quick_power_wash",
    48: "rinse_fluff",
    50: "dark wash",
    52: "rinse_only_starch",
    122: "express_20",
    123: "dark_jeans",
}

STATE_PROGRAM_PHASE = {
    # Washing Machine
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
    1794: "pre_wash",
    1795: "main_wash",
    1796: "rinse",
    1797: "interim_rinse",
    1798: "final_rinse",
    1799: "drying",
    1800: "finished",
    1801: "pre_wash",
}

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
