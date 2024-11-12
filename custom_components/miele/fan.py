"""Platform for Miele fan entity."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
import math
from typing import Any, Final, Optional

import aiohttp

from homeassistant.components.fan import (
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from . import get_coordinator
from .const import (
    API,
    DOMAIN,
    POWER_OFF,
    POWER_ON,
    VENTILATION_STEP,
    MieleAppliance,
)
from .entity import MieleEntity

_LOGGER = logging.getLogger(__name__)

SPEED_RANGE = (1, 4)

FAN_READ_ONLY = [MieleAppliance.HOB_INDUCT_EXTR]


@dataclass
class MieleFanDescription(FanEntityDescription):
    """Class describing Miele fan entities."""

    ventilation_step_tag: str | None = None
    type_key: str = "ident|type|value_localized"
    convert: Callable[[Any], Any] | None = None
    preset_modes: list | None = None
    supported_features: FanEntityFeature = FanEntityFeature(0)


@dataclass
class MieleFanDefinition:
    """Class for defining fan entities."""

    types: tuple[MieleAppliance, ...]
    description: MieleFanDescription = None


FAN_TYPES: Final[tuple[MieleFanDefinition, ...]] = (
    MieleFanDefinition(
        types=[
            MieleAppliance.HOOD,
        ],
        description=MieleFanDescription(
            key="fan",
            ventilation_step_tag="state|ventilationStep|value_raw",
            translation_key="fan",
            preset_modes=list(range(SPEED_RANGE[0], SPEED_RANGE[1] + 1)),
            supported_features=FanEntityFeature.SET_SPEED
            | FanEntityFeature.TURN_ON
            | FanEntityFeature.TURN_OFF,
        ),
    ),
    MieleFanDefinition(
        types=[
            MieleAppliance.HOB_INDUCT_EXTR,
        ],
        description=MieleFanDescription(
            key="fan",
            ventilation_step_tag="state|ventilationStep|value_raw",
            translation_key="fan",
            preset_modes=list(range(SPEED_RANGE[0], SPEED_RANGE[1] + 1)),
            supported_features=FanEntityFeature.SET_SPEED
            | FanEntityFeature.TURN_ON
            | FanEntityFeature.TURN_OFF,
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

    entities = [
        MieleFan(coordinator, idx, ent, definition.description, hass, config_entry)
        for idx, ent in enumerate(coordinator.data)
        for definition in FAN_TYPES
        if coordinator.data[ent]["ident|type|value_raw"] in definition.types
    ]

    async_add_entities(entities)


class MieleFan(MieleEntity, FanEntity):
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
        super().__init__(coordinator, idx, ent, description)
        self._api = hass.data[DOMAIN][entry.entry_id][API]

        _LOGGER.debug("Init fan %s", ent)
        self._attr_supported_features = self.entity_description.supported_features

    @property
    def is_on(self):
        """Return current on/off state."""
        return (
            self.coordinator.data[self._ent][
                self.entity_description.ventilation_step_tag
            ]
            in self.entity_description.preset_modes
        )

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset_mode of the fan."""
        pmode = self.coordinator.data[self._ent][
            self.entity_description.ventilation_step_tag
        ]
        return None if pmode == 0 else pmode

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(SPEED_RANGE)

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        return ranged_value_to_percentage(
            SPEED_RANGE,
            (
                self.coordinator.data[self._ent][
                    self.entity_description.ventilation_step_tag
                ]
                or 0
            ),
        )

    @property
    def available(self):
        """Return the availability of the entity."""

        if not self.coordinator.last_update_success:
            return False

        return self.coordinator.data[self._ent]["state|status|value_raw"] != 255

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        if self.coordinator.data[self._ent]["ident|type|value_raw"] in FAN_READ_ONLY:
            return
        if preset_mode is None or preset_mode == 0:
            return
        if (
            self.entity_description.preset_modes is None
            or preset_mode not in self.entity_description.preset_modes
        ):
            raise ValueError(
                f"{preset_mode} is not a valid preset_mode: {self.entity_description.preset_modes}"
            )
        try:
            await self._api.send_action(self._ent, {VENTILATION_STEP: preset_mode})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Set_preset_mode: %s - %s", ex.status, ex.message)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if self.coordinator.data[self._ent]["ident|type|value_raw"] in FAN_READ_ONLY:
            return
        _LOGGER.debug("Set_percentage: %s", percentage)
        preset_mode = math.ceil(percentage_to_ranged_value(SPEED_RANGE, percentage))
        _LOGGER.debug("Calc preset_mode: %s", preset_mode)
        if preset_mode == 0:
            await self.async_turn_off()
        else:
            self.coordinator.data[self._ent][
                self.entity_description.ventilation_step_tag
            ] = preset_mode
            await self.async_set_preset_mode(preset_mode)
            self.async_write_ha_state()

    async def async_turn_on(
        self,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        if self.coordinator.data[self._ent]["ident|type|value_raw"] in FAN_READ_ONLY:
            return
        _LOGGER.debug(
            "Turn_on -> percentage: %s, preset_mode: %s", percentage, preset_mode
        )
        try:
            await self._api.send_action(self._ent, {POWER_ON: True})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Turn_on: %s - %s", ex.status, ex.message)
        if percentage is not None:
            await self.async_set_percentage(percentage)
            return
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        if self.coordinator.data[self._ent]["ident|type|value_raw"] in FAN_READ_ONLY:
            return
        _LOGGER.debug("Turn_off:")
        try:
            await self._api.send_action(self._ent, {POWER_OFF: True})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Turn_off: %s - %s", ex.status, ex.message)
        self.coordinator.data[self._ent][
            self.entity_description.ventilation_step_tag
        ] = None
        self.async_write_ha_state()
