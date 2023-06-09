"""Platform for Miele switch integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging
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
    ACT_START_SUPERCOOL,
    ACT_START_SUPERFREEZE,
    ACT_STOP_SUPERCOOL,
    ACT_STOP_SUPERFREEZE,
    ACTIONS,
    API,
    COFFEE_SYSTEM,
    DIALOG_OVEN,
    DISHWASHER,
    DOMAIN,
    FREEZER,
    FRIDGE,
    FRIDGE_FREEZER,
    HOOD,
    MANUFACTURER,
    MICROWAVE,
    OVEN,
    OVEN_MICROWAVE,
    POWER_OFF,
    POWER_ON,
    PROCESS_ACTION,
    STEAM_OVEN,
    STEAM_OVEN_COMBI,
    STEAM_OVEN_MICRO,
    TUMBLE_DRYER,
    TUMBLE_DRYER_SEMI_PROFESSIONAL,
    WASHER_DRYER,
    WASHING_MACHINE,
    WINE_CABINET_FREEZER,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class MieleSwitchDescription(SwitchEntityDescription):
    """Class describing Miele switch entities."""

    data_tag: str | None = None
    type_key: str = "ident|type|value_localized"
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
            icon="mdi:snowflake",
            translation_key="supercooling",
            on_data={PROCESS_ACTION: ACT_START_SUPERCOOL},
            off_data={PROCESS_ACTION: ACT_STOP_SUPERCOOL},
        ),
    ),
    MieleSwitchDefinition(
        types=[FREEZER, FRIDGE_FREEZER, WINE_CABINET_FREEZER],
        description=MieleSwitchDescription(
            key="superfreezing",
            data_tag="state|status|value_raw",
            on_value=13,
            icon="mdi:snowflake",
            translation_key="superfreezing",
            on_data={PROCESS_ACTION: ACT_START_SUPERFREEZE},
            off_data={PROCESS_ACTION: ACT_STOP_SUPERFREEZE},
        ),
    ),
    MieleSwitchDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
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
            icon="mdi:power",
            translation_key="power_on",
            on_data={POWER_ON: True},
            off_data={POWER_OFF: True},
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
        self._api = hass.data[DOMAIN][entry.entry_id][API]
        self._api_data = hass.data[DOMAIN][entry.entry_id]

        self._idx = idx
        self._ent = ent
        self.entity_description = description
        _LOGGER.debug("init switch %s", ent)
        appl_type = self.coordinator.data[self._ent][self.entity_description.type_key]
        if appl_type == "":
            appl_type = self.coordinator.data[self._ent][
                "ident|deviceIdentLabel|techType"
            ]
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{self.entity_description.key}-{self._ent}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=appl_type,
            manufacturer=MANUFACTURER,
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
                self._api_data.get(ACTIONS, {}).get(self._ent, {}).get(POWER_OFF, True)
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
                self._api_data.get(ACTIONS, {}).get(self._ent, {}).get(POWER_OFF, False)
            ) or (
                self._api_data.get(ACTIONS, {}).get(self._ent, {}).get(POWER_ON, False)
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
