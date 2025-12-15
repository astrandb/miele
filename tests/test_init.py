"""Test initial setup."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.miele import async_unload_entry
from custom_components.miele.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from . import setup_integration
from .const import ENTRY_ID, MOCK_CONFIG_V2


async def test_setup_entry(
    hass: HomeAssistant, bypass_get_station, bypass_get_data, bypass_get_all_sensors
) -> None:
    """Test setup entry."""
    entry = MockConfigEntry(
        domain=DOMAIN, version=2, data=MOCK_CONFIG_V2, entry_id=ENTRY_ID
    )
    await setup_integration(hass, entry)

    assert entry.state is ConfigEntryState.LOADED

    assert await async_unload_entry(hass, entry)
    assert DOMAIN not in hass.data


async def test_devices_created_count(
    hass: HomeAssistant,
    bypass_get_station,
    bypass_get_data,
    bypass_get_all_sensors,
) -> None:
    """Test that one device is created."""
    config_entry = MockConfigEntry(
        domain=DOMAIN, version=2, data=MOCK_CONFIG_V2, entry_id=ENTRY_ID
    )

    await setup_integration(hass, config_entry)

    device_registry = dr.async_get(hass)

    assert len(device_registry.devices) == 1
