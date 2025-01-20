"""Services for Miele integration."""

import logging

import aiohttp
import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID, CONF_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.service import async_extract_config_entry_ids

from .const import (
    AMBIENT_COLORS,
    API,
    COLORS,
    DEVICE_NAME,
    DOMAIN,
    LIGHT,
    MODES,
    POWER_OFF,
    POWER_ON,
    PROCESS_ACTION,
    PROCESS_ACTIONS,
    PROGRAM_ID,
    START_TIME,
    TARGET_TEMPERATURE,
    VENTILATION_STEP,
)

SERVICE_PROCESS_ACTION = cv.make_entity_service_schema(
    {
        vol.Required("action"): vol.In(PROCESS_ACTIONS),
    },
)

GROUP_SGA = "sga"
MSG1 = "Only one parameter allowed"

SERVICE_GENERIC_ACTION = vol.All(
    cv.make_entity_service_schema(
        {
            vol.Exclusive(PROCESS_ACTION, GROUP_SGA, msg=MSG1): vol.All(
                int, vol.Range(min=1, max=10)
            ),
            vol.Exclusive(LIGHT, GROUP_SGA, msg=MSG1): vol.All(
                int, vol.Range(min=1, max=2)
            ),
            vol.Exclusive(START_TIME, GROUP_SGA, msg=MSG1): list,
            vol.Exclusive(PROGRAM_ID, GROUP_SGA, msg=MSG1): cv.positive_int,
            vol.Exclusive(VENTILATION_STEP, GROUP_SGA, msg=MSG1): vol.All(
                int, vol.Range(min=1, max=4)
            ),
            vol.Exclusive(TARGET_TEMPERATURE, GROUP_SGA, msg=MSG1): dict,
            vol.Exclusive(DEVICE_NAME, GROUP_SGA, msg=MSG1): cv.string,
            vol.Exclusive(POWER_ON, GROUP_SGA, msg=MSG1): cv.boolean,
            vol.Exclusive(POWER_OFF, GROUP_SGA, msg=MSG1): cv.boolean,
            vol.Exclusive(COLORS, GROUP_SGA, msg=MSG1): vol.In(AMBIENT_COLORS),
            vol.Exclusive(MODES, GROUP_SGA, msg=MSG1): cv.positive_int,
        },
    ),
    cv.has_at_least_one_key(
        PROCESS_ACTION,
        LIGHT,
        START_TIME,
        PROGRAM_ID,
        VENTILATION_STEP,
        TARGET_TEMPERATURE,
        DEVICE_NAME,
        POWER_ON,
        POWER_OFF,
        COLORS,
        MODES,
    ),
)

SERVICE_RAW = vol.Schema(
    {
        vol.Required("serialno"): cv.string,
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_PROGRAM = cv.make_entity_service_schema(
    {
        vol.Required(PROGRAM_ID): cv.positive_int,
    },
    extra=vol.ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:  # noqa: C901
    """Set up services."""

    async def extract_our_config_entry_ids(service_call: ServiceCall):
        return [
            entry_id
            for entry_id in await async_extract_config_entry_ids(hass, service_call)
            if (entry := hass.config_entries.async_get_entry(entry_id))
            and entry.domain == DOMAIN
        ]

    async def send_process_action(call: ServiceCall):
        serno = ""
        _LOGGER.debug("Call: %s", call)
        if not (our_entry_ids := await extract_our_config_entry_ids(call)):
            raise HomeAssistantError(
                "Failed to call service 'process_action'. Config entry for target not found"
            )
        _LOGGER.debug("Entries: %s", our_entry_ids)
        device_reg = dr.async_get(hass)
        for ent in call.data[CONF_DEVICE_ID]:
            device_entry = device_reg.async_get(ent)
            for ident in device_entry.identifiers:
                for val in ident:
                    if val != DOMAIN:
                        serno = val

            _api = hass.data[DOMAIN][our_entry_ids[0]][API]
            act = PROCESS_ACTIONS[call.data["action"]]
            try:
                await _api.send_action(serno, {PROCESS_ACTION: act})
            except aiohttp.ClientResponseError as ex:
                raise HomeAssistantError(
                    f"Service process_action: {ex.status} {ex.message}"
                ) from ex

    async def send_generic_action(call: ServiceCall):
        serno = ""
        _LOGGER.debug("Call: %s", call)
        if not (our_entry_ids := await extract_our_config_entry_ids(call)):
            raise HomeAssistantError(
                "Failed to call service 'generic_action'. Config entry for target not found."
            )
        if CONF_DEVICE_ID not in call.data:
            raise HomeAssistantError(
                "Cannot call generic_action on entity. Only on device."
            )
        _LOGGER.debug("Entries: %s", our_entry_ids)
        device_reg = dr.async_get(hass)
        for ent in call.data[CONF_DEVICE_ID]:
            device_entry = device_reg.async_get(ent)
            for ident in device_entry.identifiers:
                for val in ident:
                    if val != DOMAIN:
                        serno = val

            _api = hass.data[DOMAIN][our_entry_ids[0]][API]
            data = call.data.copy()
            if CONF_ENTITY_ID in data:
                data.pop(CONF_ENTITY_ID)
            if CONF_DEVICE_ID in data:
                data.pop(CONF_DEVICE_ID)
            try:
                await _api.send_action(serno, data)
            except aiohttp.ClientResponseError as ex:
                raise HomeAssistantError(
                    f"Service generic_action: {ex.status} {ex.message}"
                ) from ex

    async def send_raw(call: ServiceCall):
        _LOGGER.debug("Call: %s", call)
        account = list(hass.data[DOMAIN].keys())[0]
        _api = hass.data[DOMAIN][account][API]
        try:
            await _api.send_action(call.data["serialno"], call.data["extra"])
        except aiohttp.ClientResponseError as ex:
            raise HomeAssistantError(f"Service raw: {ex.status} {ex.message}") from ex

    async def set_program(call: ServiceCall):
        serno = ""
        _LOGGER.debug("Call: %s", call)
        if not (our_entry_ids := await extract_our_config_entry_ids(call)):
            raise HomeAssistantError(
                "Failed to call service 'set_program'. Config entry for target not found."
            )
        if CONF_DEVICE_ID not in call.data:
            raise HomeAssistantError(
                "Cannot call set_program on entity. Only on device."
            )
        _LOGGER.debug("Entries: %s", our_entry_ids)
        device_reg = dr.async_get(hass)
        for ent in call.data[CONF_DEVICE_ID]:
            device_entry = device_reg.async_get(ent)
            for ident in device_entry.identifiers:
                for val in ident:
                    if val != DOMAIN:
                        serno = val

            _api = hass.data[DOMAIN][our_entry_ids[0]][API]
            data = call.data.copy()
            if CONF_ENTITY_ID in data:
                data.pop(CONF_ENTITY_ID)
            if CONF_DEVICE_ID in data:
                data.pop(CONF_DEVICE_ID)
            try:
                await _api.set_program(serno, data)
            except aiohttp.ClientResponseError as ex:
                raise HomeAssistantError(
                    f"Service set_program: {ex.status} {ex.message}"
                ) from ex

    hass.services.async_register(
        DOMAIN, "process_action", send_process_action, SERVICE_PROCESS_ACTION
    )
    hass.services.async_register(
        DOMAIN, "generic_action", send_generic_action, SERVICE_GENERIC_ACTION
    )
    hass.services.async_register(DOMAIN, "raw", send_raw, SERVICE_RAW)
    hass.services.async_register(DOMAIN, "set_program", set_program, SERVICE_PROGRAM)
