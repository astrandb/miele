"""Constants for the Miele integration."""

DOMAIN = "miele"
VERSION = "0.1.3"
API_READ_TIMEOUT = 20

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
HOB_INDUCT_EXTR = 74

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
    HOB_INDUCT_EXTR: "hob_induct_extr",
}

APPLIANCE_ICONS = {
    WASHING_MACHINE: "mdi:washing-machine",
    TUMBLE_DRYER: "mdi:tumble-dryer",
    DISHWASHER: "mdi:dishwasher",
    OVEN: "mdi:chef-hat",
    OVEN_MICROWAVE: "mdi:chef-hat",
    HOB_HIGHLIGHT: "mdi:pot-steam-outline",
    STEAM_OVEN: "mdi:chef-hat",
    MICROWAVE: "mdi:microwave",
    COFFEE_SYSTEM: "mdi:coffee-maker",
    HOOD: "mdi:turbine",
    FRIDGE: "mdi:fridge-industrial-outline",
    FREEZER: "mdi:fridge-industrial-outline",
    FRIDGE_FREEZER: "mdi:fridge-outline",
    ROBOT_VACUUM_CLEANER: "mdi:robot-vacuum",
    WASHER_DRYER: "mdi:washing-machine",
    DISH_WARMER: "mdi:heat-wave",
    HOB_INDUCTION: "mdi:pot-steam-outline",
    STEAM_OVEN_COMBI: "mdi:chef-hat",
    WINE_CABINET: "mdi:glass-wine",
    WINE_CONDITIONING_UNIT: "mdi:glass-wine",
    WINE_STORAGE_CONDITIONING_UNIT: "mdi:glass-wine",
    STEAM_OVEN_MICRO: "mdi:chef-hat",
    DIALOG_OVEN: "mdi:chef-hat",
    WINE_CABINET_FREEZER: "mdi:glass-wine",
    HOB_INDUCT_EXTR: "mdi:pot-steam-outline",
}

STATE_STATUS_OFF = 1
STATE_STATUS_ON = 2
STATE_STATUS_PROGRAMMED = 3
STATE_STATUS_WAITING_TO_START = 4
STATE_STATUS_RUNNING = 5
STATE_STATUS_PAUSE = 6
STATE_STATUS_PROGRAM_ENDED = 7
STATE_STATUS_FAILURE = 8
STATE_STATUS_PROGRAM_INTERRUPTED = 9
STATE_STATUS_IDLE = 10
STATE_STATUS_RINSE_HOLD = 11
STATE_STATUS_SERVICE = 12
STATE_STATUS_SUPERFREEZING = 13
STATE_STATUS_SUPERCOOLING = 14
STATE_STATUS_SUPERHEATING = 15
STATE_STATUS_SUPERCOOLING_SUPERFREEZING = 146
STATE_STATUS_NOT_CONNECTED = 255

# Define various states
STATE_STATUS = {
    0: "reserved",
    STATE_STATUS_OFF: "off",
    STATE_STATUS_ON: "on",
    STATE_STATUS_PROGRAMMED: "programmed",
    STATE_STATUS_WAITING_TO_START: "waiting_to_start",
    STATE_STATUS_RUNNING: "running",
    STATE_STATUS_PAUSE: "pause",
    STATE_STATUS_PROGRAM_ENDED: "program_ended",
    STATE_STATUS_FAILURE: "failure",
    STATE_STATUS_PROGRAM_INTERRUPTED: "program_interrupted",
    STATE_STATUS_IDLE: "idle",
    STATE_STATUS_RINSE_HOLD: "rinse_hold",
    STATE_STATUS_SERVICE: "service",
    STATE_STATUS_SUPERFREEZING: "superfreezing",
    STATE_STATUS_SUPERCOOLING: "supercooling",
    STATE_STATUS_SUPERHEATING: "superheating",
    STATE_STATUS_SUPERCOOLING_SUPERFREEZING: "supercooling_superfreezing",
    STATE_STATUS_NOT_CONNECTED: "not_connected",
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
    263: "cleaning",
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
    516: "hand_iron_2",
    517: "normal",
    518: "normal_plus",
    519: "cooling_down",
    520: "hand_iron_1",
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
    # Robot vacuum cleaner
    5889: "vacuum_cleaning",
    5890: "returning",
    5892: "going_to_target_area",
    5893: "wheel_lifted",
    5899: "not_charging",
    5903: "docked",
    5904: "docked",
    # Error conditions/API quirks.
    65535: "not_running",  # Seems to be an API error/default value.
}

WASHING_MACHINE_PROGRAM_ID = {
    -1: "no_program",  # Extrapolated from other device types.
    0: "no_program",  # Returned by the API when no program is selected.
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
    45: "cool_air",  # washer-dryer
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
    190: "eco_40_60",
}
DISHWASHER_PROGRAM_ID = {
    -1: "no_program",  # Sometimes returned by the API when the machine is switched off entirely, in conjunection with program phase 65535.
    0: "no_program",  # Returned by the API when the machine is switched off entirely.
    1: "intensive",
    2: "maintenance",
    3: "eco",
    6: "automatic",
    9: "solar_save",
    10: "gentle",
    11: "extra_quiet",
    12: "hygiene",
    13: "quick_power_wash",
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
    44: "glasses_warm",
}
TUMBLE_DRYER_PROGRAM_ID = {
    -1: "no_program",  # Extrapolated from other device types.
    0: "no_program",  # Extrapolated from other device types
    10: "automatic_plus",
    20: "cottons",
    23: "cottons_hygiene",
    30: "minimum_iron",
    31: "gentle_minimum_iron",
    40: "woollens_handcare",
    50: "delicates",
    60: "warm_air",
    70: "cool_air",
    80: "express",
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
    # steam_smoothing
    # bed_linen
}
OVEN_PROGRAM_ID = {
    -1: "no_program",  # Extrapolated from other device types.
    0: "no_program",  # Extrapolated from other device types
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
ROBOT_VACUUM_CLEANER_PROGRAM_ID = {
    -1: "no_program",  # Extrapolated from other device types
    0: "no_program",  # Extrapolated from other device types
    1: "auto",
    2: "spot",
    3: "turbo",
    4: "silent",
}

STATE_PROGRAM_ID = {
    WASHING_MACHINE: WASHING_MACHINE_PROGRAM_ID,
    TUMBLE_DRYER: TUMBLE_DRYER_PROGRAM_ID,
    DISHWASHER: DISHWASHER_PROGRAM_ID,
    OVEN: OVEN_PROGRAM_ID,
    WASHER_DRYER: WASHING_MACHINE_PROGRAM_ID,
    ROBOT_VACUUM_CLEANER: ROBOT_VACUUM_CLEANER_PROGRAM_ID,
}

STATE_DRYING_STEP = {
    0: "extra_dry",
    1: "normal_plus",
    2: "normal",
    3: "slightly_dry",
    4: "hand_iron_1",
    5: "hand_iron_2",
    6: "machine_iron",
    7: "smoothing",
}

COLORS = "colors"
DEVICE_NAME = "deviceName"
LIGHT = "light"
LIGHT_ON = 1
LIGHT_OFF = 2
MODES = "modes"
POWER_ON = "powerOn"
POWER_OFF = "powerOff"
PROCESS_ACTION = "processAction"
PROGRAM_ID = "programId"
START_TIME = "startTime"
TARGET_TEMPERATURE = "targetTemperature"
VENTILATION_STEP = "ventilationStep"

ACT_START = 1
ACT_STOP = 2
ACT_PAUSE = 3
ACT_START_SUPERFREEZE = 4
ACT_STOP_SUPERFREEZE = 5
ACT_START_SUPERCOOL = 6
ACT_STOP_SUPERCOOL = 7

# Possible actions
PROCESS_ACTIONS = {
    "start": ACT_START,
    "stop": ACT_STOP,
    "pause": ACT_PAUSE,
    "start_superfreezing": ACT_START_SUPERFREEZE,
    "stop_superfreezing": ACT_STOP_SUPERFREEZE,
    "start_supercooling": ACT_START_SUPERCOOL,
    "stop_supercooling": ACT_STOP_SUPERCOOL,
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

ACTIONS = "actions"
API = "api"
