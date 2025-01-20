"""Platform for Miele vacuum integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Final

import aiohttp

from homeassistant.components.vacuum import (
    ATTR_STATUS,
    StateVacuumEntity,
    StateVacuumEntityDescription,
    VacuumActivity,
    VacuumEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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
    MieleAppliance,
)
from .entity import MieleEntity

_LOGGER = logging.getLogger(__name__)

FAN_SPEEDS = ["normal", "turbo", "silent"]
PROG_AUTO = 1
PROG_SPOT = 2
PROG_TURBO = 3
PROG_SILENT = 4

PPROGRAM_MAP = {"normal": PROG_AUTO, "turbo": PROG_TURBO, "silent": PROG_SILENT}

SUPPORTED_FEATURES = (
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


@dataclass
class MieleVacuumDescription(StateVacuumEntityDescription):
    """Class describing Miele vacuum entities."""

    data_tag: str | None = None
    type_key: str = "ident|type|value_localized"
    on_value: int = 0
    off_value: int = 0


@dataclass
class MieleVacuumDefinition:
    """Class for defining vacuum entities."""

    types: tuple[MieleAppliance, ...]
    description: MieleVacuumDescription = None


VACUUM_TYPES: Final[tuple[MieleVacuumDefinition, ...]] = (
    MieleVacuumDefinition(
        types=[MieleAppliance.ROBOT_VACUUM_CLEANER],
        description=MieleVacuumDescription(
            key="vacuum",
            data_tag="state|status|value_raw",
            on_value=14,
            translation_key="vacuum",
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

    entities = [
        MieleVacuum(coordinator, idx, ent, definition.description, hass, config_entry)
        for idx, ent in enumerate(coordinator.data)
        for definition in VACUUM_TYPES
        if coordinator.data[ent]["ident|type|value_raw"] in definition.types
    ]

    async_add_entities(entities)


class MieleVacuum(MieleEntity, StateVacuumEntity):
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
        super().__init__(coordinator, idx, ent, description)
        self._api = hass.data[DOMAIN][entry.entry_id][API]
        self._api_data = hass.data[DOMAIN][entry.entry_id]

        self._phase = None
        _LOGGER.debug("init vacuum %s", ent)
        self._attr_supported_features = SUPPORTED_FEATURES
        self._attr_fan_speed_list = FAN_SPEEDS

    @property
    def activity(self) -> VacuumActivity | None:
        """Map state."""
        if self.coordinator.data[self._ent]["state|status|value_raw"] == 6:
            return VacuumActivity.PAUSED

        self._phase = self.coordinator.data[self._ent]["state|programPhase|value_raw"]
        if self._phase in (5903, 5904):
            return VacuumActivity.DOCKED
        if self._phase in (5889, 5892):
            return VacuumActivity.CLEANING
        if self._phase == 5890:
            return VacuumActivity.RETURNING
        if self._phase in (5893, 5894, 5895, 5896, 5897, 5898, 5899, 5900):
            return VacuumActivity.ERROR
        if self._phase in (5891, 5910):
            return VacuumActivity.PAUSED
        if self._phase == 0:
            return VacuumActivity.IDLE

        return self._phase

    @property
    def status(self):
        """Map status text."""
        if self._phase == 5892:
            return "going_to_target_area"
        if self._phase == 5893:
            return "wheel_lifted"
        if self._phase == 5894:
            return "dirty_sensors"
        if self._phase == 5895:
            return "dust_box_missing"
        if self._phase == 5896:
            return "blocked_drive_wheels"
        if self._phase == 5897:
            return "blocked_brushes"
        if self._phase == 5898:
            return "check_dust_box_and_filter"
        if self._phase == 5899:
            return "internal_fault_reboot"
        if self._phase == 5900:
            return "blocked_front_wheel"
        if self._phase == 5910:
            return "remote_controlled"
        return

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the vacuum cleaner."""
        data: dict[str, Any] = {}
        if self.status is not None:
            data[ATTR_STATUS] = self.status
        return data

    @property
    def battery_level(self):
        """Return the battery level."""
        return self.coordinator.data[self._ent]["state|batteryLevel"]

    @property
    def fan_speed(self) -> str:
        """Return the fan speed."""
        if (
            self.coordinator.data[self._ent]["state|ProgramID|value_raw"] == PROG_AUTO
            or self.coordinator.data[self._ent]["state|ProgramID|value_raw"]
            == PROG_SPOT
        ):
            return "normal"
        if self.coordinator.data[self._ent]["state|ProgramID|value_raw"] == PROG_TURBO:
            return "turbo"
        if self.coordinator.data[self._ent]["state|ProgramID|value_raw"] == PROG_SILENT:
            return "silent"
        return None

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
        """Return to base."""
        _LOGGER.debug("return_to_base -> kwargs: %s", kwargs)

    async def async_clean_spot(self, **kwargs):
        """Clean spot."""
        _LOGGER.debug("clean_spot -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROGRAM_ID: PROG_SPOT})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Pause: %s - %s", ex.status, ex.message)

    async def async_start(self, **kwargs):
        """Start cleaning."""
        _LOGGER.debug("start -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROCESS_ACTION: ACT_START})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Pause: %s - %s", ex.status, ex.message)

    async def async_stop(self, **kwargs):
        """Stop cleaning."""
        _LOGGER.debug("stop -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROCESS_ACTION: ACT_STOP})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Pause: %s - %s", ex.status, ex.message)

    async def async_pause(self, **kwargs):
        """Pause cleaning."""
        _LOGGER.debug("pause -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROCESS_ACTION: ACT_PAUSE})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Pause: %s - %s", ex.status, ex.message)

    async def async_set_fan_speed(self, fan_speed: str, **kwargs):
        """Set fan speed."""
        _LOGGER.debug("set_fan_speed -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(
                self._ent, {PROGRAM_ID: PPROGRAM_MAP[fan_speed]}
            )
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Set fan speed: %s - %s", ex.status, ex.message)
