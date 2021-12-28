"""Platform for Miele switch integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import get_coordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class MieleSwitchDescription(SwitchEntityDescription):
    """Class describing Miele switch entities."""

    data_tag: str | None = None
    type_key: str | None = None
    on_value: int = 0


@dataclass
class MieleSwitchDefinition:
    """Class for defining switch entities."""

    types: tuple[int, ...]
    description: MieleSwitchDescription = None


SWITCH_TYPES: Final[tuple[MieleSwitchDefinition, ...]] = (
    MieleSwitchDefinition(
        types=[19, 21],
        description=MieleSwitchDescription(
            key="supercooling",
            data_tag="state|status|value_raw",
            on_value=14,
            type_key="ident|type|value_localized",
            name="Supercooling",
        ),
    ),
    MieleSwitchDefinition(
        types=[20, 21, 68],
        description=MieleSwitchDescription(
            key="superfreezing",
            data_tag="state|status|value_raw",
            on_value=13,
            type_key="ident|type|value_localized",
            name="Superfreezing",
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator = await get_coordinator(hass, config_entry)

    entities = []
    for idx, ent in enumerate(coordinator.data):
        for definition in SWITCH_TYPES:
            if coordinator.data[ent]["ident|type|value_raw"] in definition.types:
                entities.append(
                    MieleSwitch(coordinator, idx, ent, definition.description)
                )

    async_add_entities(entities)


class MieleSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Sensor."""

    entity_description: MieleSwitchDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleSwitchDescription,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._idx = idx
        self._ent = ent
        self.entity_description = description
        _LOGGER.debug("init switch %s", ent)
        self._attr_name = f"{self.coordinator.data[self._ent][self.entity_description.type_key]} {self.entity_description.name}"
        self._attr_unique_id = f"{self.entity_description.key}-{self._ent}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=self.coordinator.data[self._ent][self.entity_description.type_key],
            manufacturer="Miele",
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"],
        )

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return (
            self.coordinator.data[self._ent][self.entity_description.data_tag]
            == self.entity_description.on_value
        )

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug("turn_on -> kwargs: %s", kwargs)
        """Turn the entity on."""

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug("turn_off -> kwargs: %s", kwargs)
        """Turn the entity off."""
