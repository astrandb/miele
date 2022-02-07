"""Services for Miele integration."""

import copy
import logging

import aiohttp
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry
from homeassistant.helpers.service import async_extract_config_entry_ids

from .const import AMBIENT_COLORS, DOMAIN, PROCESS_ACTIONS

SERVICE_PROCESS_ACTION = cv.make_entity_service_schema(
    {
        vol.Required("action"): vol.In(PROCESS_ACTIONS),
    },
)

SERVICE_GENERIC_ACTION = cv.make_entity_service_schema(
    {
        vol.Optional("processAction"): vol.All(int, vol.Range(min=1, max=10)),
        vol.Optional("light"): vol.All(int, vol.Range(min=1, max=2)),
        vol.Optional("startTime"): list,
        vol.Optional("programId"): cv.positive_int,
        vol.Optional("targetTemperature"): dict,
        vol.Optional("deviceName"): cv.string,
        vol.Optional("powerOn"): cv.boolean,
        vol.Optional("powerOff"): cv.boolean,
        vol.Optional("colors"): vol.In(AMBIENT_COLORS),
        vol.Optional("modes"): cv.positive_int,
    },
)

SERVICE_RAW = vol.Schema(
    {
        vol.Required("serialno"): cv.string,
    },
    extra=vol.ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    async def extract_our_config_entry_ids(service_call: ServiceCall):
        return [
            entry_id
            for entry_id in await async_extract_config_entry_ids(hass, service_call)
            if (entry := hass.config_entries.async_get_entry(entry_id))
            and entry.domain == DOMAIN
        ]

    async def send_process_action(call: ServiceCall):
        _LOGGER.debug("Call: %s", call)
        if not (our_entry_ids := await extract_our_config_entry_ids(call)):
            raise HomeAssistantError(
                "Failed to call service 'process_action'. Config entry for target not found"
            )
        _LOGGER.debug("Entries: %s", our_entry_ids)
        device_reg = device_registry.async_get(hass)
        for ent in call.data["device_id"]:
            device_entry = device_reg.async_get(ent)
            for ident in device_entry.identifiers:
                for val in ident:
                    if val != DOMAIN:
                        serno = val

            _api = hass.data[DOMAIN][our_entry_ids[0]]["api"]
            act = PROCESS_ACTIONS[call.data["action"]]
            try:
                await _api.send_action(serno, {"processAction": act})
            except aiohttp.ClientResponseError as ex:
                raise HomeAssistantError(
                    f"Service generic_action: {ex.status} {ex.message}"
                )
        return

    async def send_generic_action(call: ServiceCall):
        _LOGGER.debug("Call: %s", call)
        if not (our_entry_ids := await extract_our_config_entry_ids(call)):
            raise HomeAssistantError(
                "Failed to call service 'generic_action'. Config entry for target not found"
            )
        _LOGGER.debug("Entries: %s", our_entry_ids)
        device_reg = device_registry.async_get(hass)
        for ent in call.data["device_id"]:
            device_entry = device_reg.async_get(ent)
            for ident in device_entry.identifiers:
                for val in ident:
                    if val != DOMAIN:
                        serno = val

            _api = hass.data[DOMAIN][our_entry_ids[0]]["api"]
            data = copy(call.data)
            data = data.pop("entity_id")
            try:
                await _api.send_action(serno, data)
            except aiohttp.ClientResponseError as ex:
                raise HomeAssistantError(
                    f"Service generic_action: {ex.status} {ex.message}"
                )
        return

    async def send_raw(call: ServiceCall):
        _LOGGER.debug("Call: %s", call)
        account = list(hass.data[DOMAIN].keys())[0]
        _api = hass.data[DOMAIN][account]["api"]
        try:
            await _api.send_action(call.data["serialno"], call.data["extra"])
        except aiohttp.ClientResponseError as ex:
            raise HomeAssistantError(
                f"Service raw: {ex.status} {ex.message}"
            )
        return

    hass.services.async_register(
        DOMAIN, "process_action", send_process_action, SERVICE_PROCESS_ACTION
    )
    hass.services.async_register(
        DOMAIN, "generic_action", send_generic_action, SERVICE_GENERIC_ACTION
    )
    hass.services.async_register(
        DOMAIN, "raw", send_raw, SERVICE_RAW
    )
    return
