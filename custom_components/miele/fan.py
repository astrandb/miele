"""Platform for Miele fan entity."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Final, Optional

import aiohttp
from homeassistant.components.fan import (
    SUPPORT_PRESET_MODE,
    FanEntity,
    FanEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util.percentage import (  # percentage_to_ranged_value
    int_states_in_range,
    ranged_value_to_percentage,
)

from . import get_coordinator
from .const import API, DOMAIN, HOOD, POWER_OFF, POWER_ON, VENTILATION_STEP

_LOGGER = logging.getLogger(__name__)

SPEED_RANGE = (1, 4)


@dataclass
class MieleFanDescription(FanEntityDescription):
    """Class describing Miele fan entities."""

    ventilationStep_tag: str | None = None
    type_key: str | None = None
    convert: Callable[[Any], Any] | None = None
    preset_modes: list | None = None
    supported_features: int = 0


@dataclass
class MieleFanDefinition:
    """Class for defining fan entities."""

    types: tuple[int, ...]
    description: MieleFanDescription = None


FAN_TYPES: Final[tuple[MieleFanDefinition, ...]] = (
    MieleFanDefinition(
        types=[
            HOOD,
        ],
        description=MieleFanDescription(
            key="fan",
            ventilationStep_tag="state|ventilationStep|value_raw",
            type_key="ident|type|value_localized",
            name="Fan",
            preset_modes=list(range(SPEED_RANGE[0], SPEED_RANGE[1] + 1)),
            supported_features=SUPPORT_PRESET_MODE,
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the fan platform."""
    coordinator = await get_coordinator(hass, config_entry)

    entities = []
    for idx, ent in enumerate(coordinator.data):
        for definition in FAN_TYPES:
            if coordinator.data[ent]["ident|type|value_raw"] in definition.types:
                entities.append(
                    MieleFan(
                        coordinator,
                        idx,
                        ent,
                        definition.description,
                        hass,
                        config_entry,
                    )
                )

    async_add_entities(entities)


class MieleFan(CoordinatorEntity, FanEntity):
    """Representation of a Fan."""

    entity_description: MieleFanDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleFanDescription,
        hass: HomeAssistant,
        entry: ConfigType,
    ):
        """Initialize the fan."""
        super().__init__(coordinator)
        self._api = hass.data[DOMAIN][entry.entry_id][API]

        self._idx = idx
        self._ent = ent
        self._ed = description
        _LOGGER.debug("Init fan %s", ent)
        self._attr_name = (
            f"{self.coordinator.data[self._ent][self._ed.type_key]} {self._ed.name}"
        )
        self._attr_unique_id = f"{self._ed.key}-{self._ent}"
        self._attr_preset_modes = self._ed.preset_modes
        self._attr_preset_mode = None
        self._attr_supported_features = self._ed.supported_features
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=self.coordinator.data[self._ent][self._ed.type_key],
            manufacturer="Miele",
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"],
        )

    @property
    def is_on(self):
        """Return current on/off state."""
        return True

    @property
    def preset_mode(self) -> str:
        """Return the current preset_mode of the fan."""
        return self.coordinator.data[self._ent][self._ed.ventilationStep_tag]

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(SPEED_RANGE)

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        return ranged_value_to_percentage(
            SPEED_RANGE, self.coordinator.data[self._ent][self._ed.ventilationStep_tag]
        )

    @property
    def available(self):
        """Return the availability of the entity."""

        if not self.coordinator.last_update_success:
            return False

        return self.coordinator.data[self._ent]["state|status|value_raw"] != 255

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""

        try:
            await self._api.send_action(self._ent, {VENTILATION_STEP: preset_mode})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Turn_off: %s - %s", ex.status, ex.message)

    async def async_turn_on(
        self,
        speed: Optional[str] = None,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        try:
            await self._api.send_action(self._ent, {POWER_ON: True})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Turn_off: %s - %s", ex.status, ex.message)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        try:
            await self._api.send_action(self._ent, {POWER_OFF: True})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Turn_off: %s - %s", ex.status, ex.message)
