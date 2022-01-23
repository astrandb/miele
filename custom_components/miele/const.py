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
