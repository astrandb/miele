"""Platform for Miele light entity."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable, Final

import aiohttp
from homeassistant.components.light import LightEntity, LightEntityDescription
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
    AMBIENT_LIGHT,
    API,
    COFFEE_SYSTEM,
    DOMAIN,
    HOOD,
    LIGHT,
    LIGHT_OFF,
    LIGHT_ON,
    MANUFACTURER,
    MICROWAVE,
    OVEN,
    OVEN_MICROWAVE,
    STEAM_OVEN,
    STEAM_OVEN_COMBI,
    STEAM_OVEN_MICRO,
    WINE_CABINET,
    WINE_CABINET_FREEZER,
    WINE_CONDITIONING_UNIT,
    WINE_STORAGE_CONDITIONING_UNIT,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class MieleLightDescription(LightEntityDescription):
    """Class describing Miele light entities."""

    light_tag: str | None = None
    type_key: str = "ident|type|value_localized"
    convert: Callable[[Any], Any] | None = None
    preset_modes: list | None = None
    supported_features: int = 0


@dataclass
class MieleLightDefinition:
    """Class for defining light entities."""

    types: tuple[int, ...]
    description: MieleLightDescription = None


LIGHT_TYPES: Final[tuple[MieleLightDefinition, ...]] = (
    MieleLightDefinition(
        types=[
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            COFFEE_SYSTEM,
            HOOD,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            WINE_CABINET_FREEZER,
        ],
        description=MieleLightDescription(
            key="light",
            light_tag="state|light",
            translation_key="light",
        ),
    ),
    MieleLightDefinition(
        types=[
            HOOD,
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

    entities = []
    for idx, ent in enumerate(coordinator.data):
        for definition in LIGHT_TYPES:
            if coordinator.data[ent]["ident|type|value_raw"] in definition.types:
                entities.append(
                    MieleLight(
                        coordinator,
                        idx,
                        ent,
                        definition.description,
                        hass,
                        config_entry,
                    )
                )

    async_add_entities(entities)


class MieleLight(CoordinatorEntity, LightEntity):
    """Representation of a Light."""

    entity_description: MieleLightDescription

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
        super().__init__(coordinator)
        self._api = hass.data[DOMAIN][entry.entry_id][API]

        self._idx = idx
        self._ent = ent
        self.entity_description = description
        _LOGGER.debug("Init light %s", ent)
        appl_type = self.coordinator.data[self._ent][self.entity_description.type_key]
        if appl_type == "":
            appl_type = self.coordinator.data[self._ent][
                "ident|deviceIdentLabel|techType"
            ]
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{self.entity_description.key}-{self._ent}"
        self._attr_supported_features = self.entity_description.supported_features
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=appl_type,
            manufacturer=MANUFACTURER,
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"],
        )

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
