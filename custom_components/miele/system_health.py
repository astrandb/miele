"""Provide info to system health."""
from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback
from pymiele import MIELE_API

from .const import VERSION


@callback
def async_register(
    hass: HomeAssistant, register: system_health.SystemHealthRegistration
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info)


async def system_health_info(hass):
    """Get info for the info page."""

    return {
        "component_version": VERSION,
        "reach_miele_cloud": system_health.async_check_can_reach_url(hass, MIELE_API),
    }
