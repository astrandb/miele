"""The Miele integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
from http import HTTPStatus
from json.decoder import JSONDecodeError
import logging

from aiohttp import ClientResponseError
import async_timeout
import flatdict
from homeassistant.components import persistent_notification
from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.config_entry_oauth2_flow import (
    OAuth2Session,
    async_get_config_entry_implementation,
)
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    DataUpdateCoordinator,
    UpdateFailed,
)
import voluptuous as vol

from .api import AsyncConfigEntryAuth
from .const import (
    ACTIONS,
    API,
    API_READ_TIMEOUT,
    CONF_ID,
    CONF_PROGRAM_IDS,
    CONF_SENSORS,
    CONF_VALUE,
    CONF_VALUE_RAW,
    DOMAIN,
    MANUFACTURER,
    VERSION,
)
from .devcap import (  # noqa: F401
    TEST_ACTION_21,
    TEST_ACTION_23,
    TEST_DATA_1,
    TEST_DATA_4,
    TEST_DATA_7,
    TEST_DATA_12,
    TEST_DATA_17_CM,
    TEST_DATA_17_CVA,
    TEST_DATA_18,
    TEST_DATA_21,
    TEST_DATA_23,
    TEST_DATA_24,
    TEST_DATA_74,
)
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

CONFIG_PROGRAM_IDS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VALUE_RAW): cv.positive_int,
        vol.Required(CONF_VALUE): cv.string,
    }
)

CONFIG_SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID): cv.entity_id,
        vol.Optional(CONF_PROGRAM_IDS): vol.All(
            cv.ensure_list, [CONFIG_PROGRAM_IDS_SCHEMA]
        ),
    }
)

CONFIG_SCHEMA_ROOT = vol.Schema(
    {
        # For compatibility with other integration
        vol.Inclusive(CONF_CLIENT_ID, "oauth"): cv.string,
        vol.Inclusive(CONF_CLIENT_SECRET, "oauth"): cv.string,
        vol.Optional(CONF_SENSORS): vol.All(cv.ensure_list, [CONFIG_SENSOR_SCHEMA]),
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: CONFIG_SCHEMA_ROOT},
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.FAN,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.VACUUM,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Miele component."""
    hass.data[DOMAIN] = {}
    if DOMAIN not in config:
        config[DOMAIN] = {}

    await _setup_sensor_config(hass, config)

    if CONF_CLIENT_ID in config[DOMAIN] and CONF_CLIENT_ID in config[DOMAIN]:
        persistent_notification.async_create(
            hass,
            "Configuration of the Miele platform in YAML is deprecated. "
            "Your existing configuration has been imported into the UI "
            "automatically and can be safely removed from your configuration.yaml file",
            MANUFACTURER,
            "miele_config_import",
        )

        await async_import_client_credential(
            hass,
            DOMAIN,
            ClientCredential(
                config[DOMAIN][CONF_CLIENT_ID], config[DOMAIN][CONF_CLIENT_SECRET]
            ),
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Miele from a config entry."""
    implementation = await async_get_config_entry_implementation(hass, entry)

    session = OAuth2Session(hass, entry, implementation)
    try:
        await session.async_ensure_token_valid()
    except ClientResponseError as ex:
        _LOGGER.debug("API error: %s (%s)", ex.code, ex.message)
        if ex.code in (HTTPStatus.UNAUTHORIZED,):
            raise ConfigEntryAuthFailed(
                f"Token not valid, trigger renewal: {ex}"
            ) from ex
        raise ConfigEntryNotReady from ex

    hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN]["id_log"] = []
    hass.data[DOMAIN][entry.entry_id]["retries_401"] = 0
    hass.data[DOMAIN][entry.entry_id]["listener"] = None
    hass.data[DOMAIN][entry.entry_id][API] = AsyncConfigEntryAuth(
        aiohttp_client.async_get_clientsession(hass), session
    )

    if ACTIONS not in hass.data[DOMAIN][entry.entry_id]:
        hass.data[DOMAIN][entry.entry_id][ACTIONS] = {}
    coordinator = await get_coordinator(hass, entry)
    if not coordinator.last_update_success:
        await coordinator.async_config_entry_first_refresh()
    serialnumbers = list(coordinator.data.keys())

    miele_api = hass.data[DOMAIN][entry.entry_id][API]
    for serial in serialnumbers:
        try:
            async with async_timeout.timeout(API_READ_TIMEOUT):
                res = await miele_api.request(
                    "GET",
                    f"/devices/{serial}/actions",
                    agent_suffix=f"Miele for Home Assistant/{VERSION}",
                )
                if res.status == 401:
                    raise ConfigEntryAuthFailed(
                        "Authentication failure when fetching actions"
                    )
            result = await res.json()
            hass.data[DOMAIN][entry.entry_id][ACTIONS][serial] = result
        except asyncio.TimeoutError as error:
            raise ConfigEntryNotReady from error
        except JSONDecodeError:
            _LOGGER.warning(
                "Could not decode json from fetch of actions for %s", serial
            )

    # hass.data[DOMAIN][entry.entry_id][ACTIONS]["1223023"] = TEST_ACTION_23

    # _LOGGER.debug("First data - flat: %s", coordinator.data)
    # _LOGGER.debug("First actions: %s", hass.data[DOMAIN][entry.entry_id][ACTIONS])

    async def _callback_update_data(data) -> None:
        # data["1223001"] = TEST_DATA_1
        # data["1223004"] = TEST_DATA_4
        # data["1223007"] = TEST_DATA_7
        # data["1223012"] = TEST_DATA_12
        # data["122A017"] = TEST_DATA_17_CM
        # data["122B017"] = TEST_DATA_17_CVA
        # data["1223018"] = TEST_DATA_18
        # data["1223021"] = TEST_DATA_21
        # data["1223023"] = TEST_DATA_23
        # data["1223024"] = TEST_DATA_24
        # data["1223074"] = TEST_DATA_74
        flat_result: dict = {}
        try:
            for ent in data:
                flat_result[ent] = dict(flatdict.FlatterDict(data[ent], delimiter="|"))
            coordinator.async_set_updated_data(flat_result)
        except Exception:  # pylint: disable=broad-except  # noqa: E722
            _LOGGER.warning("Failed to process pushed data from API")

    async def _callback_update_actions(data) -> None:
        hass.data[DOMAIN][entry.entry_id][ACTIONS] = data
        # Force update of UI
        # data["1223021"] = TEST_ACTION_21
        coordinator.async_set_updated_data(coordinator.data)

    hass.data[DOMAIN][entry.entry_id]["listener"] = asyncio.create_task(
        hass.data[DOMAIN][entry.entry_id][API].listen_events(
            data_callback=_callback_update_data,
            actions_callback=_callback_update_actions,
        )
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_setup_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN][entry.entry_id]["listener"].cancel()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def get_coordinator(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> DataUpdateCoordinator:
    """Get the data update coordinator."""
    if "coordinator" in hass.data[DOMAIN][entry.entry_id]:
        return hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async def async_fetch():
        miele_api = hass.data[DOMAIN][entry.entry_id][API]
        try:
            async with async_timeout.timeout(API_READ_TIMEOUT):
                res = await miele_api.request(
                    "GET",
                    "/devices",
                    agent_suffix=f"Miele for Home Assistant/{VERSION}",
                )
            if res.status == 401:
                hass.data[DOMAIN][entry.entry_id]["retries_401"] += 1
                if hass.data[DOMAIN][entry.entry_id]["retries_401"] == 5:
                    raise ConfigEntryAuthFailed(
                        "Authentication failure when fetching data"
                    )
                else:
                    raise UpdateFailed(
                        f"HTTP status 401: {hass.data[DOMAIN][entry.entry_id]['retries_401']}"
                    )
            result = await res.json()
        except JSONDecodeError as error:
            _LOGGER.warning("Could not decode json from coordinator fetch")
            raise UpdateFailed(error) from error

        hass.data[DOMAIN][entry.entry_id]["retries_401"] = 0
        flat_result: dict = {}
        # result["1223001"] = TEST_DATA_1
        # result["1223004"] = TEST_DATA_4
        # result["1223007"] = TEST_DATA_7
        # result["1223012"] = TEST_DATA_12
        # result["122A017"] = TEST_DATA_17_CM
        # result["122B017"] = TEST_DATA_17_CVA
        # result["1223018"] = TEST_DATA_18
        # result["1223021"] = TEST_DATA_21
        # result["1223023"] = TEST_DATA_23
        # result["1223024"] = TEST_DATA_24
        # result["1223074"] = TEST_DATA_74

        try:
            for ent in result:
                flat_result[ent] = dict(
                    flatdict.FlatterDict(result[ent], delimiter="|")
                )
        except TypeError as ex:
            raise UpdateFailed(ex) from ex

        # _LOGGER.debug("Data: %s", flat_result)
        return flat_result

    hass.data[DOMAIN][entry.entry_id]["coordinator"] = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_method=async_fetch,
        update_interval=timedelta(seconds=60),
    )
    await hass.data[DOMAIN][entry.entry_id]["coordinator"].async_refresh()
    return hass.data[DOMAIN][entry.entry_id]["coordinator"]


async def _setup_sensor_config(hass: HomeAssistant, config: ConfigType):
    """Set up sensors configuration."""

    # configuration.yaml
    # miele:
    #   sensors:
    #     - id: sensor.tumble_dryer_program
    #       program_ids:
    #         - value_raw: 14
    #           value: shirts
    #         - value_raw: 31
    #           value: bed_linen
    # ---> becomes
    # hass.data[DOMAIN] = {
    #   "sensors": {
    #       "sensor.tumble_dryer_program": {
    #           "program_ids": {
    #              14: "shirts",
    #              31: "bed_linen"
    #           }
    #       }
    #   }
    # }
    if CONF_SENSORS in config[DOMAIN]:
        hass.data[DOMAIN][CONF_SENSORS] = {}
        for sensor_config in config[DOMAIN][CONF_SENSORS]:
            hass.data[DOMAIN][CONF_SENSORS][sensor_config[CONF_ID]] = {}
            if CONF_PROGRAM_IDS in sensor_config:
                hass.data[DOMAIN][CONF_SENSORS][sensor_config[CONF_ID]][
                    CONF_PROGRAM_IDS
                ] = {}
                for program_id_definition in sensor_config[CONF_PROGRAM_IDS]:
                    hass.data[DOMAIN][CONF_SENSORS][sensor_config[CONF_ID]][
                        CONF_PROGRAM_IDS
                    ][program_id_definition[CONF_VALUE_RAW]] = program_id_definition[
                        CONF_VALUE
                    ]
