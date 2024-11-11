"""Platform for Miele light entity."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any, Final

import aiohttp

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
    LightEntityDescription,
    LightEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import get_coordinator
from .const import (
    AMBIENT_LIGHT,
    API,
    DOMAIN,
    LIGHT,
    LIGHT_OFF,
    LIGHT_ON,
    MieleAppliance,
)
from .entity import MieleEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class MieleLightDescription(LightEntityDescription):
    """Class describing Miele light entities."""

    light_tag: str | None = None
    type_key: str = "ident|type|value_localized"
    convert: Callable[[Any], Any] | None = None
    preset_modes: list | None = None
    supported_features = LightEntityFeature(0)


@dataclass
class MieleLightDefinition:
    """Class for defining light entities."""

    types: tuple[MieleAppliance, ...]
    description: MieleLightDescription = None


LIGHT_TYPES: Final[tuple[MieleLightDefinition, ...]] = (
    MieleLightDefinition(
        types=[
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.COFFEE_SYSTEM,
            MieleAppliance.HOOD,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.WINE_CABINET_FREEZER,
            MieleAppliance.STEAM_OVEN_MK2,
        ],
        description=MieleLightDescription(
            key="light",
            light_tag="state|light",
            translation_key="light",
        ),
    ),
    MieleLightDefinition(
        types=[
            MieleAppliance.HOOD,
        ],
        description=MieleLightDescription(
            key="ambientlight",
            light_tag="state|ambientLight",
            translation_key="ambient_light",
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light platform."""
    coordinator = await get_coordinator(hass, config_entry)

    entities = [
        MieleLight(coordinator, idx, ent, definition.description, hass, config_entry)
        for idx, ent in enumerate(coordinator.data)
        for definition in LIGHT_TYPES
        if coordinator.data[ent]["ident|type|value_raw"] in definition.types
    ]

    async_add_entities(entities)


class MieleLight(MieleEntity, LightEntity):
    """Representation of a Light."""

    entity_description: MieleLightDescription
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleLightDescription,
        hass: HomeAssistant,
        entry: ConfigType,
    ):
        """Initialize the light."""
        super().__init__(coordinator, idx, ent, description)
        self._api = hass.data[DOMAIN][entry.entry_id][API]

        _LOGGER.debug("Init light %s", ent)
        self._attr_supported_features = self.entity_description.supported_features

    @property
    def is_on(self):
        """Return current on/off state."""
        return (
            self.coordinator.data[self._ent][self.entity_description.light_tag]
            == LIGHT_ON
        )

    @property
    def available(self):
        """Return the availability of the entity."""

        if not self.coordinator.last_update_success:
            return False

        return self.coordinator.data[self._ent]["state|status|value_raw"] != 255

    async def async_turn_on(
        self,
        **kwargs: Any,
    ) -> None:
        """Turn on the light."""
        light_type = (
            AMBIENT_LIGHT if self.entity_description.key == "ambientlight" else LIGHT
        )
        try:
            await self._api.send_action(self._ent, {light_type: LIGHT_ON})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Turn_on: %s - %s", ex.status, ex.message)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        light_type = (
            AMBIENT_LIGHT if self.entity_description.key == "ambientlight" else LIGHT
        )
        try:
            await self._api.send_action(self._ent, {light_type: LIGHT_OFF})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Turn_off: %s - %s", ex.status, ex.message)
