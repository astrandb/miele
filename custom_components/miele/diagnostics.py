"""Diagnostics support for Miele."""
from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

TO_REDACT = {CONF_PASSWORD, CONF_USERNAME, "access_token", "refresh_token"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]

    diagnostics_data = {
        "info": async_redact_data(config_entry.data, TO_REDACT),
        "data": coordinator.data,
    }

    return diagnostics_data
