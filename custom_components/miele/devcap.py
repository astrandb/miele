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

TEST_DATA_7 = {
    "ident": {
        "type": {
            "key_localized": "Device type",
            "value_raw": 7,
            "value_localized": "Dishwasher",
        },
        "deviceName": "",
        "protocolVersion": 2,
        "deviceIdentLabel": {
            "fabNumber": "<fabNumber1>",
            "fabIndex": "64",
            "techType": "G6865-W",
            "matNumber": "<matNumber1>",
            "swids": [
                "<swid1>",
                "<swid2>",
                "<swid3>",
                "<...>",
            ],
        },
        "xkmIdentLabel": {"techType": "EK039W", "releaseVersion": "02.72"},
    },
    "state": {
        "ProgramID": {
            "value_raw": 38,
            "value_localized": "QuickPowerWash",
            "key_localized": "Program name",
        },
        "status": {
            "value_raw": 5,
            "value_localized": "In use",
            "key_localized": "status",
        },
        "programType": {
            "value_raw": 2,
            "value_localized": "Automatic programme",
            "key_localized": "Program type",
        },
        "programPhase": {
            "value_raw": 1799,
            "value_localized": "Drying",
            "key_localized": "Program phase",
        },
        "remainingTime": [0, 15],
        "startTime": [0, 0],
        "targetTemperature": [
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"}
        ],
        "temperature": [
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"},
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"},
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"},
        ],
        "signalInfo": False,
        "signalFailure": False,
        "signalDoor": False,
        "remoteEnable": {
            "fullRemoteControl": True,
            "smartGrid": False,
            "mobileStart": False,
        },
        "ambientLight": None,
        "light": None,
        "elapsedTime": [0, 59],
        "spinningSpeed": {
            "unit": "rpm",
            "value_raw": None,
            "value_localized": None,
            "key_localized": "Spin speed",
        },
        "dryingStep": {
            "value_raw": None,
            "value_localized": "",
            "key_localized": "Drying level",
        },
        "ventilationStep": {
            "value_raw": None,
            "value_localized": "",
            "key_localized": "Fan level",
        },
        "plateStep": [],
        "ecoFeedback": None,
        "batteryLevel": None,
    },
}

TEST_DATA_18 = {
    "ident": {
        "type": {
            "key_localized": "Device type",
            "value_raw": 18,
            "value_localized": "Hood",
        },
        "deviceName": "",
        "protocolVersion": 2,
        "deviceIdentLabel": {
            "fabNumber": "<fabNumber3>",
            "fabIndex": "64",
            "techType": "Fläkt",
            "matNumber": "<matNumber3>",
            "swids": [
                "<swid1>",
                "<swid2>",
                "<swid3>",
                "<...>",
            ],
        },
        "xkmIdentLabel": {"techType": "EK039W", "releaseVersion": "02.72"},
    },
    "state": {
        "ProgramID": {
            "value_raw": 0,
            "value_localized": "",
            "key_localized": "Program name",
        },
        "status": {
            "value_raw": 1,
            "value_localized": "Off",
            "key_localized": "status",
        },
        "programType": {
            "value_raw": 0,
            "value_localized": "",
            "key_localized": "Program type",
        },
        "programPhase": {
            "value_raw": 0,
            "value_localized": "",
            "key_localized": "Program phase",
        },
        "remainingTime": [0, 0],
        "startTime": [0, 0],
        "targetTemperature": [
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"}
        ],
        "temperature": [
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"},
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"},
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"},
        ],
        "signalInfo": False,
        "signalFailure": False,
        "signalDoor": False,
        "remoteEnable": {
            "fullRemoteControl": True,
            "smartGrid": False,
            "mobileStart": False,
        },
        "ambientLight": "blue",
        "light": None,
        "elapsedTime": [0, 0],
        "spinningSpeed": {
            "unit": "rpm",
            "value_raw": None,
            "value_localized": None,
            "key_localized": "Spin speed",
        },
        "dryingStep": {
            "value_raw": None,
            "value_localized": "",
            "key_localized": "Drying level",
        },
        "ventilationStep": {
            "value_raw": 1,
            "value_localized": "Step1",
            "key_localized": "Fan level",
        },
        "plateStep": [],
        "ecoFeedback": None,
        "batteryLevel": None,
    },
}

TEST_DATA_24 = {
    "ident": {
        "type": {
            "key_localized": "Device type",
            "value_raw": 24,
            "value_localized": "Washer dryer",
        },
        "deviceName": "",
        "protocolVersion": 4,
        "deviceIdentLabel": {
            "fabNumber": "<fabNumber2>",
            "fabIndex": "32",
            "techType": "WTR870",
            "matNumber": "<matNumber2>",
            "swids": [
                "<swid1>",
                "<swid2>",
                "<swid3>",
                "<...>",
            ],
        },
        "xkmIdentLabel": {"techType": "EK037", "releaseVersion": "03.88"},
    },
    "state": {
        "ProgramID": {
            "value_raw": 3,
            "value_localized": "Minimum iron",
            "key_localized": "Program name",
        },
        "status": {"value_raw": 1, "value_localized": "Off", "key_localized": "status"},
        "programType": {
            "value_raw": 1,
            "value_localized": "Own programme",
            "key_localized": "Program type",
        },
        "programPhase": {
            "value_raw": 256,
            "value_localized": "",
            "key_localized": "Program phase",
        },
        "remainingTime": [1, 59],
        "startTime": [0, 0],
        "targetTemperature": [
            {"value_raw": 3000, "value_localized": 30, "unit": "Celsius"},
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"},
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"},
        ],
        "temperature": [
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"},
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"},
            {"value_raw": -32768, "value_localized": None, "unit": "Celsius"},
        ],
        "signalInfo": False,
        "signalFailure": False,
        "signalDoor": True,
        "remoteEnable": {
            "fullRemoteControl": True,
            "smartGrid": False,
            "mobileStart": False,
        },
        "ambientLight": None,
        "light": None,
        "elapsedTime": [0, 0],
        "spinningSpeed": {
            "unit": "rpm",
            "value_raw": 1000,
            "value_localized": "1000",
            "key_localized": "Spin speed",
        },
        "dryingStep": {
            "value_raw": 0,
            "value_localized": "",
            "key_localized": "Drying level",
        },
        "ventilationStep": {
            "value_raw": None,
            "value_localized": "",
            "key_localized": "Fan level",
        },
        "plateStep": [],
        "ecoFeedback": None,
        "batteryLevel": None,
    },
}
