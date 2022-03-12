"""Platform for Miele button integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Final

import aiohttp
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
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
class MieleButtonDescription(ButtonEntityDescription):
    """Class describing Miele button entities."""

    data_tag: str | None = None
    type_key: str | None = None
    on_value: int = 0
    off_value: int = 0
    press_data: dict[str, Any] | None = None


@dataclass
class MieleButtonDefinition:
    """Class for defining button entities."""

    types: tuple[int, ...]
    description: MieleButtonDescription = None


BUTTON_TYPES: Final[tuple[MieleButtonDefinition, ...]] = (
    MieleButtonDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
            DISHWASHER,
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
        ],
        description=MieleButtonDescription(
            key="start",
            name="Start",
            press_data={"processAction": 1},
        ),
    ),
    MieleButtonDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
            DISHWASHER,
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            HOOD,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
        ],
        description=MieleButtonDescription(
            key="stop",
            type_key="ident|type|value_localized",
            name="Stop",
            press_data={"processAction": 2},
        ),
    ),
    MieleButtonDefinition(
        types=[
            FREEZER,
        ],
        description=MieleButtonDescription(
            key="stopSuperfreezing",
            type_key="ident|type|value_localized",
            name="Stop Superfreezing",
            press_data={"processAction": 5},
        ),
    ),
    MieleButtonDefinition(
        types=[
            FREEZER,
        ],
        description=MieleButtonDescription(
            key="startSuperfreezing",
            type_key="ident|type|value_localized",
            name="Start Superfreezing",
            press_data={"processAction": 4},
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator = await get_coordinator(hass, config_entry)

    entities = []
    for idx, ent in enumerate(coordinator.data):
        for definition in BUTTON_TYPES:
            if coordinator.data[ent]["ident|type|value_raw"] in definition.types:
                entities.append(
                    MieleButton(
                        coordinator,
                        idx,
                        ent,
                        definition.description,
                        hass,
                        config_entry,
                    )
                )

    async_add_entities(entities)


class MieleButton(CoordinatorEntity, ButtonEntity):
    """Representation of a Button."""

    entity_description: MieleButtonDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleButtonDescription,
        hass: HomeAssistant,
        entry: ConfigType,
    ):
        """Initialize the button."""
        super().__init__(coordinator)
        self._api = hass.data[DOMAIN][entry.entry_id]["api"]
        self._api_data = hass.data[DOMAIN][entry.entry_id]

        self._idx = idx
        self._ent = ent
        self.entity_description = description
        _LOGGER.debug("init button %s", ent)
        self._attr_name = f"{self.coordinator.data[self._ent][self.entity_description.type_key]} {self.entity_description.name}"
        self._attr_unique_id = f"{self.entity_description.key}-{self._ent}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=self.coordinator.data[self._ent][self.entity_description.type_key],
            manufacturer="Miele",
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"],
        )

    def _action_available(self, action) -> bool:
        """Check if action is available according to API."""
        # _LOGGER.debug("%s _action_available: %s", self.entity_description.name, action)
        if "processAction" in action:
            value = action.get("processAction")
            action_data = (
                self._api_data.get("actions", {})
                .get(self._ent, {})
                .get("processAction", {})
            )
            return value in action_data

        _LOGGER.debug("Action not found: %s", action)
        return False

    @property
    def available(self):
        """Return the availability of the entity."""

        if not self.coordinator.last_update_success:
            return False

        return self.coordinator.data[self._ent][
            "state|status|value_raw"
        ] != 255 and self._action_available(self.entity_description.press_data)

    async def async_press(self):
        """Press the button."""
        _LOGGER.debug("press: %s", self._attr_name)
        if self._action_available(self.entity_description.press_data):
            try:
                await self._api.send_action(
                    self._ent, self.entity_description.press_data
                )
            except aiohttp.ClientResponseError as ex:
                _LOGGER.error("Press: %s - %s", ex.status, ex.message)
            # TODO Consider removing accepted action from ["actions"] to block
            #      further calls of async_press util API update arrives
        else:
            _LOGGER.warning(
                "Device does not accept this action now: %s / %s",
                self._attr_name,
                self.entity_description.press_data,
            )
