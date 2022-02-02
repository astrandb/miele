"""Services for Miele integration."""

import logging

import aiohttp
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry
from homeassistant.helpers.service import async_extract_config_entry_ids

from .const import DOMAIN, PROCESS_ACTIONS

SERVICE_PROCESS_ACTION = cv.make_entity_service_schema(
    {
        vol.Required("action"): vol.In(PROCESS_ACTIONS),
    },
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
                _LOGGER.error("Service process_action: %s - %s", ex.status, ex.message)
        return

    hass.services.async_register(
        DOMAIN, "process_action", send_process_action, SERVICE_PROCESS_ACTION
    )
    return
