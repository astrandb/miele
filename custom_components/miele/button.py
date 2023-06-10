"""Platform for Miele button integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging
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
    ACT_START,
    ACT_STOP,
    ACTIONS,
    API,
    DIALOG_OVEN,
    DISHWASHER,
    DOMAIN,
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
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class MieleButtonDescription(ButtonEntityDescription):
    """Class describing Miele button entities."""

    type_key: str = "ident|type|value_localized"
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
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
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
            translation_key="start",
            press_data={PROCESS_ACTION: ACT_START},
        ),
    ),
    MieleButtonDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
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
            translation_key="stop",
            press_data={PROCESS_ACTION: ACT_STOP},
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
        self._api = hass.data[DOMAIN][entry.entry_id][API]
        self._api_data = hass.data[DOMAIN][entry.entry_id]

        self._idx = idx
        self._ent = ent
        self.entity_description = description
        _LOGGER.debug("init button %s", ent)
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

    def _action_available(self, action) -> bool:
        """Check if action is available according to API."""
        if PROCESS_ACTION in action:
            value = action.get(PROCESS_ACTION)
            action_data = (
                self._api_data.get(ACTIONS, {})
                .get(self._ent, {})
                .get(PROCESS_ACTION, {})
            )
            return value in action_data

        if POWER_ON in action:
            action_data = (
                self._api_data.get(ACTIONS, {}).get(self._ent, {}).get(POWER_ON, False)
            )
            return action_data

        if POWER_OFF in action:
            action_data = (
                self._api_data.get(ACTIONS, {}).get(self._ent, {}).get(POWER_OFF, False)
            )
            return action_data

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
        _LOGGER.debug("press: %s", self.entity_description.key)
        if self._action_available(self.entity_description.press_data):
            try:
                await self._api.send_action(
                    self._ent, self.entity_description.press_data
                )
            except aiohttp.ClientResponseError as ex:
                _LOGGER.error("Press: %s - %s", ex.status, ex.message)
            # TODO Consider removing accepted action from [ACTIONS] to block
            #      further calls of async_press util API update arrives
        else:
            _LOGGER.warning(
                "Device does not accept this action now: %s / %s",
                self.entity_description.key,
                self.entity_description.press_data,
            )
