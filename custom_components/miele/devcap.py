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
