"""Platform for Miele switch integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Final

import aiohttp
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
from .const import (
    COFFEE_SYSTEM,
    DIALOG_OVEN,
    DISHWASHER,
    DOMAIN,
    FREEZER,
    FRIDGE,
    FRIDGE_FREEZER,
    HOOD,
    MICROWAVE,
    OVEN,
    OVEN_MICROWAVE,
    STEAM_OVEN,
    STEAM_OVEN_COMBI,
    STEAM_OVEN_MICRO,
    TUMBLE_DRYER,
    WASHER_DRYER,
    WASHING_MACHINE,
    WINE_CABINET_FREEZER,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class MieleSwitchDescription(SwitchEntityDescription):
    """Class describing Miele switch entities."""

    data_tag: str | None = None
    type_key: str | None = None
    on_value: int = 0
    off_value: int = 0
    on_data: dict[str, Any] | None = None
    off_data: dict[str, Any] | None = None


@dataclass
class MieleSwitchDefinition:
    """Class for defining switch entities."""

    types: tuple[int, ...]
    description: MieleSwitchDescription = None


SWITCH_TYPES: Final[tuple[MieleSwitchDefinition, ...]] = (
    MieleSwitchDefinition(
        types=[FRIDGE, FRIDGE_FREEZER],
        description=MieleSwitchDescription(
            key="supercooling",
            data_tag="state|status|value_raw",
            on_value=14,
            type_key="ident|type|value_localized",
            icon="mdi:snowflake",
            name="Supercooling",
            on_data={"processAction": 6},
            off_data={"processAction": 7},
        ),
    ),
    MieleSwitchDefinition(
        types=[FREEZER, FRIDGE_FREEZER, WINE_CABINET_FREEZER],
        description=MieleSwitchDescription(
            key="superfreezing",
            data_tag="state|status|value_raw",
            on_value=13,
            type_key="ident|type|value_localized",
            icon="mdi:snowflake",
            name="Superfreezing",
            on_data={"processAction": 4},
            off_data={"processAction": 5},
        ),
    ),
    MieleSwitchDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
            DISHWASHER,
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            COFFEE_SYSTEM,
            HOOD,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
        ],
        description=MieleSwitchDescription(
            key="poweronoff",
            data_tag="state|status|value_raw",
            off_value=1,
            type_key="ident|type|value_localized",
            icon="mdi:power",
            name="Power on",
            on_data={"powerOn": True},
            off_data={"powerOff": True},
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
                    MieleSwitch(
                        coordinator,
                        idx,
                        ent,
                        definition.description,
                        hass,
                        config_entry,
                    )
                )

    async_add_entities(entities)


class MieleSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Switch."""

    entity_description: MieleSwitchDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleSwitchDescription,
        hass: HomeAssistant,
        entry: ConfigType,
    ):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._api = hass.data[DOMAIN][entry.entry_id]["api"]
        self._api_data = hass.data[DOMAIN][entry.entry_id]

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
        """Return the state of the switch."""
        if self.entity_description.key in {"supercooling", "superfreezing"}:
            return (
                self.coordinator.data[self._ent][self.entity_description.data_tag]
                == self.entity_description.on_value
            )

        elif self.entity_description.key in {"poweronoff"}:
            power_data = (
                self._api_data.get("actions", {})
                .get(self._ent, {})
                .get("powerOff", True)
            )
            return power_data

        return False

    @property
    def available(self):
        """Return the availability of the entity."""

        if not self.coordinator.last_update_success:
            return False

        if self.entity_description.key in {"poweronoff"}:
            power_data = (
                self._api_data.get("actions", {})
                .get(self._ent, {})
                .get("powerOff", False)
            ) or (
                self._api_data.get("actions", {})
                .get(self._ent, {})
                .get("powerOn", False)
            )
            return power_data

        return self.coordinator.data[self._ent]["state|status|value_raw"] != 255

    async def async_turn_on(self, **kwargs):
        """Turn on the device."""
        _LOGGER.debug("turn_on -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, self.entity_description.on_data)
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Turn_on: %s - %s", ex.status, ex.message)

        # await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn off the device."""
        _LOGGER.debug("turn_off -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, self.entity_description.off_data)
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Turn_off: %s - %s", ex.status, ex.message)

        # await self.coordinator.async_request_refresh()
