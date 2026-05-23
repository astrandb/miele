"""pytest fixtures."""

from collections.abc import Generator
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import load_fixture
from pytest_homeassistant_custom_component.syrupy import HomeAssistantSnapshotExtension
from syrupy import SnapshotAssertion

from homeassistant.core import HomeAssistant
from homeassistant.util.json import json_loads

# pylint: disable=redefined-outer-name


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    return


@pytest.fixture
def data_file_name() -> str:
    """Filename for data fixture."""
    return "miele_devices.json"


@pytest.fixture(name="load_default_appliances")
def load_default_station_fixture(data_file_name: str) -> dict:
    """Load data for default farm of appliances."""
    return json_loads(load_fixture(data_file_name))


@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture(
    hass: HomeAssistant,
    load_default_data: dict,
):
    """Skip calls to get data from API."""
    with patch(
        "custom_components.weatherlink.pyweatherlink.WLHubV2.get_data",
        return_value=load_default_data,
    ):
        yield


@pytest.fixture
def entity_registry_enabled_by_default() -> Generator[None]:
    """Test fixture that ensures all entities are enabled in the registry."""
    with patch(
        "homeassistant.helpers.entity.Entity.entity_registry_enabled_default",
        return_value=True,
    ):
        yield


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Home Assistant extension."""
    return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture
def mock_api():
    """Mock api."""
    with (
        patch(
            "custom_components.weatherlink.pyweatherlink.WLHubV2.get_data"
        ) as mock_api,
    ):
        yield mock_api
