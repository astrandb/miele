"""Platform for Miele vacuum integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Final

import aiohttp
from homeassistant.components.vacuum import (
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_IDLE,
    STATE_ON,
    STATE_PAUSED,
    STATE_RETURNING,
    StateVacuumEntity,
    VacuumEntityDescription,
    VacuumEntityFeature,
)
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
    ACT_PAUSE,
    ACT_START,
    ACT_STOP,
    ACTIONS,
    API,
    DOMAIN,
    POWER_OFF,
    POWER_ON,
    PROCESS_ACTION,
    PROGRAM_ID,
    ROBOT_VACUUM_CLEANER,
)

_LOGGER = logging.getLogger(__name__)

FAN_SPEEDS = ["normal", "turbo", "silent"]
PROG_AUTO = 1
PROG_SPOT = 2
PROG_TURBO = 3
PROG_SILENT = 4

PPROGRAM_MAP = {"normal": PROG_AUTO, "turbo": PROG_TURBO, "silent": PROG_SILENT}

@dataclass
class MieleVacuumDescription(VacuumEntityDescription):
    """Class describing Miele vacuum entities."""

    data_tag: str | None = None
    type_key: str = "ident|type|value_localized"
    on_value: int = 0
    off_value: int = 0


@dataclass
class MieleVacuumDefinition:
    """Class for defining vacuum entities."""

    types: tuple[int, ...]
    description: MieleVacuumDescription = None


VACUUM_TYPES: Final[tuple[MieleVacuumDefinition, ...]] = (
    MieleVacuumDefinition(
        types=[ROBOT_VACUUM_CLEANER],
        description=MieleVacuumDescription(
            key="vacuum",
            data_tag="state|status|value_raw",
            on_value=14,
            name="Vacuum",
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the vacuum platform."""
    coordinator = await get_coordinator(hass, config_entry)

    entities = []
    for idx, ent in enumerate(coordinator.data):
        for definition in VACUUM_TYPES:
            if coordinator.data[ent]["ident|type|value_raw"] in definition.types:
                entities.append(
                    MieleVacuum(
                        coordinator,
                        idx,
                        ent,
                        definition.description,
                        hass,
                        config_entry,
                    )
                )

    async_add_entities(entities)


class MieleVacuum(CoordinatorEntity, StateVacuumEntity):
    """Representation of a Vacuum."""

    entity_description: MieleVacuumDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleVacuumDescription,
        hass: HomeAssistant,
        entry: ConfigType,
    ):
        """Initialize the vacuum."""
        super().__init__(coordinator)
        self._api = hass.data[DOMAIN][entry.entry_id][API]
        self._api_data = hass.data[DOMAIN][entry.entry_id]

        self._idx = idx
        self._ent = ent
        self.entity_description = description
        _LOGGER.debug("init vacuum %s", ent)
        appl_type = self.coordinator.data[self._ent][self.entity_description.type_key]
        if appl_type == "":
            appl_type = self.coordinator.data[self._ent][
                "ident|deviceIdentLabel|techType"
            ]
        self._attr_supported_features = (
            VacuumEntityFeature.TURN_ON
            | VacuumEntityFeature.TURN_OFF
            | VacuumEntityFeature.STATUS
            | VacuumEntityFeature.STATE
            | VacuumEntityFeature.BATTERY
            | VacuumEntityFeature.FAN_SPEED
            | VacuumEntityFeature.START
            | VacuumEntityFeature.STOP
            | VacuumEntityFeature.PAUSE
            | VacuumEntityFeature.CLEAN_SPOT
        )
        self._attr_fan_speed_list = FAN_SPEEDS
        self._attr_name = None
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{self.entity_description.key}-{self._ent}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=appl_type,
            manufacturer="Miele",
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"],
        )

    @property
    def state(self):
        if self.coordinator.data[self._ent]["state|status|value_raw"] == 2:  # On
            if (
                self.coordinator.data[self._ent]["state|programPhase|value_raw"] == 5904
            ):  # in the base station
                return STATE_DOCKED
        if self.coordinator.data[self._ent]["state|status|value_raw"] == 6:  # pause
            return STATE_PAUSED
        return STATE_ERROR

    @property
    def error(self):
        return "Dummy error message"

    @property
    def battery_level(self):
        return self.coordinator.data[self._ent]["state|batteryLevel"]

    @property
    def fan_speed(self):
        if self.coordinator.data[self._ent]["state|ProgramID|value_raw"] == PROG_AUTO:
            return "normal"
        elif self.coordinator.data[self._ent]["state|ProgramId|value_raw"] == PROG_SPOT:
            return "normal"
        elif (
            self.coordinator.data[self._ent]["state|ProgramId|value_raw"] == PROG_TURBO
        ):
            return "turbo"
        elif (
            self.coordinator.data[self._ent]["state|ProgramId|value_raw"] == PROG_SILENT
        ):
            return "silent"
        return None

    # @property
    # def is_on(self):
    #     """Return the state of the vacuum."""
    #     if self.entity_description.key in {"supercooling", "superfreezing"}:
    #         return (
    #             self.coordinator.data[self._ent][self.entity_description.data_tag]
    #             == self.entity_description.on_value
    #         )

    #     elif self.entity_description.key in {"poweronoff"}:
    #         power_data = (
    #             self._api_data.get(ACTIONS, {}).get(self._ent, {}).get(POWER_OFF, True)
    #         )
    #         return power_data

    #     return False

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
            await self._api.send_action(self._ent, {PROCESS_ACTION: ACT_START})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Turn_on: %s - %s", ex.status, ex.message)

        # await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn off the device."""
        _LOGGER.debug("turn_off -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROCESS_ACTION: ACT_STOP})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Turn_off: %s - %s", ex.status, ex.message)

        # await self.coordinator.async_request_refresh()

    async def async_return_to_base(self, **kwargs):
        _LOGGER.debug("return_to_base -> kwargs: %s", kwargs)

    async def async_clean_spot(self, **kwargs):
        _LOGGER.debug("clean_spot -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROGRAM_ID: PROG_SPOT})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Pause: %s - %s", ex.status, ex.message)

    async def async_start(self, **kwargs):
        _LOGGER.debug("start -> kwargs: %s", kwargs)

    async def async_stop(self, **kwargs):
        _LOGGER.debug("stop -> kwargs: %s", kwargs)

    async def async_pause(self, **kwargs):
        _LOGGER.debug("pause -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROCESS_ACTION: ACT_PAUSE})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Pause: %s - %s", ex.status, ex.message)

    async def async_set_fan_speed(self, **kwargs):
        _LOGGER.debug("set_fan_speed -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROGRAM_ID: PPROGRAM_MAP[kwargs["fan_speed"]]})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Set fan speed: %s - %s", ex.status, ex.message)
