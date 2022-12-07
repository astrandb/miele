"""Diagnostics support for Miele."""
from __future__ import annotations

from typing import Any

import async_timeout
from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import ACTIONS, API, DOMAIN

TO_REDACT = {
    CONF_PASSWORD,
    CONF_USERNAME,
    "access_token",
    "refresh_token",
    "ident|deviceIdentLabel|fabNumber",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]

    device_data = {}
    action_data = {}
    ino = 0
    for val, key in enumerate(coordinator.data):
        ino += 1
        device_data[f"Appliance_{ino}"] = coordinator.data[key]
        if ACTIONS in hass.data[DOMAIN][config_entry.entry_id]:
            action_data[f"Appliance_{ino}"] = hass.data[DOMAIN][config_entry.entry_id][
                ACTIONS
            ][key]

    diagnostics_data = {
        "info": async_redact_data(config_entry.data, TO_REDACT),
        "data": async_redact_data(device_data, TO_REDACT),
        "actions": async_redact_data(action_data, TO_REDACT),
        "id_log": hass.data[DOMAIN]["id_log"],
    }

    return diagnostics_data


async def async_get_device_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    info = {}
    info["manufacturer"] = device.manufacturer
    info["model"] = device.model

    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]

    device_data = {}
    action_data = {}
    program_data = {}

    for val, key in enumerate(coordinator.data):
        if ("miele", key) in device.identifiers:
            device_data = coordinator.data[key]
            if ACTIONS in hass.data[DOMAIN][config_entry.entry_id]:
                action_data = hass.data[DOMAIN][config_entry.entry_id][ACTIONS].get(
                    key, {}
                )
            miele_api = hass.data[DOMAIN][config_entry.entry_id][API]
            async with async_timeout.timeout(20):
                res = await miele_api.request("GET", f"/devices/{key}/programs")
            if res.status >= 300:
                program_data = {"httpStatus": res.status}
            else:
                program_data = await res.json()

    diagnostics_data = {
        "info": async_redact_data(info, TO_REDACT),
        "data": async_redact_data(device_data, TO_REDACT),
        "actions": async_redact_data(action_data, TO_REDACT),
        "programs": program_data,
        "id_log": hass.data[DOMAIN]["id_log"],
    }

    return diagnostics_data
