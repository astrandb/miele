"""Device capabilities."""

# API Version 1.0.5

DEV_TYPES = {
    1: "Washing Machine",
    2: "Thumble Dryer",
    7: "Dishwasher",
    19: "Fridge",
    20: "Freezer",
}

STATE_CAPABILITIES = {
    19: {
        "ProgramID",
        "status",
        "programType",
        "targetTemperature",
        "temperature",
        "signalInfo",
        "signalFailure",
        "signalDoor",
        "remoteEnable",
    },
    20: {
        "ProgramID",
        "status",
        "programType",
        "targetTemperature",
        "temperature",
        "signalInfo",
        "signalFailure",
        "signalDoor",
        "remoteEnable",
    },
}

ACTION_CAPABILITIES = {
    19: {"targetTemperature", "startSupercooling"},
    20: {"targetTemperature", "startSuperfreezing"},
}

LIVE_ACTION_CAPABILITIES = {
    "711934968": {
        "processAction": [4],
        "light": [],
        "ambientLight": [],
        "startTime": [],
        "ventilationStep": [],
        "programId": [],
        "targetTemperature": [{"zone": 1, "min": -26, "max": -16}],
        "deviceName": True,
        "powerOn": False,
        "powerOff": False,
        "colors": [],
        "modes": [1],
    },
    "711944869": {
        "processAction": [6],
        "light": [],
        "ambientLight": [],
        "startTime": [],
        "ventilationStep": [],
        "programId": [],
        "targetTemperature": [{"zone": 1, "min": 1, "max": 9}],
        "deviceName": True,
        "powerOn": False,
        "powerOff": False,
        "colors": [],
        "modes": [1],
    },
}
