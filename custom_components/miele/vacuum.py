"""Platform for Miele vacuum integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Final

import aiohttp
from homeassistant.components.vacuum import (
    ATTR_STATUS,
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_IDLE,
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
    MANUFACTURER,
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
        self._phase = None
        self.entity_description = description
        _LOGGER.debug("init vacuum %s", ent)
        appl_type = self.coordinator.data[self._ent][self.entity_description.type_key]
        if appl_type == "":
            appl_type = self.coordinator.data[self._ent][
                "ident|deviceIdentLabel|techType"
            ]
        self._attr_supported_features = SUPPORTED_FEATURES
        self._attr_fan_speed_list = FAN_SPEEDS
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{self.entity_description.key}-{self._ent}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=appl_type,
            manufacturer=MANUFACTURER,
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"],
        )

    @property
    def state(self):
        """Map state."""
        if self.coordinator.data[self._ent]["state|status|value_raw"] == 6:
            return STATE_PAUSED

        self._phase = self.coordinator.data[self._ent]["state|programPhase|value_raw"]
        if self._phase in (5903, 5904):
            return STATE_DOCKED
        elif self._phase in (5889, 5892):
            return STATE_CLEANING
        elif self._phase == 5890:
            return STATE_RETURNING
        elif self._phase in (5893, 5894, 5895, 5896, 5897, 5898, 5899, 5900):
            return STATE_ERROR
        elif self._phase in (5891, 5910):
            return STATE_PAUSED
        elif self._phase == 0:
            return STATE_IDLE

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
        return self.coordinator.data[self._ent]["state|batteryLevel"]

    @property
    def fan_speed(self):
        if self.coordinator.data[self._ent]["state|ProgramID|value_raw"] == PROG_AUTO:
            return "normal"
        elif self.coordinator.data[self._ent]["state|ProgramID|value_raw"] == PROG_SPOT:
            return "normal"
        elif (
            self.coordinator.data[self._ent]["state|ProgramID|value_raw"] == PROG_TURBO
        ):
            return "turbo"
        elif (
            self.coordinator.data[self._ent]["state|ProgramID|value_raw"] == PROG_SILENT
        ):
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
        _LOGGER.debug("return_to_base -> kwargs: %s", kwargs)

    async def async_clean_spot(self, **kwargs):
        _LOGGER.debug("clean_spot -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROGRAM_ID: PROG_SPOT})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Pause: %s - %s", ex.status, ex.message)

    async def async_start(self, **kwargs):
        _LOGGER.debug("start -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROCESS_ACTION: ACT_START})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Pause: %s - %s", ex.status, ex.message)

    async def async_stop(self, **kwargs):
        _LOGGER.debug("stop -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROCESS_ACTION: ACT_STOP})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Pause: %s - %s", ex.status, ex.message)

    async def async_pause(self, **kwargs):
        _LOGGER.debug("pause -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(self._ent, {PROCESS_ACTION: ACT_PAUSE})
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Pause: %s - %s", ex.status, ex.message)

    async def async_set_fan_speed(self, fan_speed: str, **kwargs):
        _LOGGER.debug("set_fan_speed -> kwargs: %s", kwargs)
        try:
            await self._api.send_action(
                self._ent, {PROGRAM_ID: PPROGRAM_MAP[fan_speed]}
            )
        except aiohttp.ClientResponseError as ex:
            _LOGGER.error("Set fan speed: %s - %s", ex.status, ex.message)
