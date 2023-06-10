"""Platform for Miele sensor integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any, Callable, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    TIME_MINUTES,
    UnitOfEnergy,
    UnitOfTemperature,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util import dt as dt_util

from . import get_coordinator
from .const import (
    APPLIANCE_ICONS,
    COFFEE_SYSTEM,
    CONF_PROGRAM_IDS,
    CONF_SENSORS,
    DIALOG_OVEN,
    DISH_WARMER,
    DISHWASHER,
    DOMAIN,
    FREEZER,
    FRIDGE,
    FRIDGE_FREEZER,
    HOB_HIGHLIGHT,
    HOB_INDUCT_EXTR,
    HOB_INDUCTION,
    HOOD,
    MANUFACTURER,
    MICROWAVE,
    OVEN,
    OVEN_MICROWAVE,
    ROBOT_VACUUM_CLEANER,
    STATE_DRYING_STEP,
    STATE_PROGRAM_ID,
    STATE_PROGRAM_PHASE,
    STATE_PROGRAM_TYPE,
    STATE_STATUS,
    STATE_STATUS_IDLE,
    STATE_STATUS_NOT_CONNECTED,
    STATE_STATUS_OFF,
    STATE_STATUS_ON,
    STATE_STATUS_PROGRAM_ENDED,
    STATE_STATUS_PROGRAMMED,
    STATE_STATUS_SERVICE,
    STATE_STATUS_WAITING_TO_START,
    STEAM_OVEN,
    STEAM_OVEN_COMBI,
    STEAM_OVEN_MICRO,
    TUMBLE_DRYER,
    TUMBLE_DRYER_SEMI_PROFESSIONAL,
    WASHER_DRYER,
    WASHING_MACHINE,
    WINE_CABINET,
    WINE_CABINET_FREEZER,
    WINE_CONDITIONING_UNIT,
    WINE_STORAGE_CONDITIONING_UNIT,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class MieleSensorDescription(SensorEntityDescription):
    """Class describing Miele sensor entities."""

    data_tag: str | None = None
    data_tag1: str | None = None
    data_tag_loc: str | None = None
    type_key: str = "ident|type|value_localized"
    type_key_raw: str = "ident|type|value_raw"
    status_key_raw: str = "state|status|value_raw"
    convert: Callable[[Any], Any] | None = None
    convert_icon: Callable[[Any], Any] | None = None
    available_states: Callable[[Any], Any] | None = None
    extra_attributes: dict[str, Any] | None = None


@dataclass
class MieleSensorDefinition:
    """Class for defining sensor entities."""

    types: tuple[int, ...]
    description: MieleSensorDescription = None


SENSOR_TYPES: Final[tuple[MieleSensorDefinition, ...]] = (
    MieleSensorDefinition(
        types=[
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            FRIDGE,
            FREEZER,
            FRIDGE_FREEZER,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            WINE_CABINET_FREEZER,
        ],
        description=MieleSensorDescription(
            key="temperature",
            data_tag="state|temperature|0|value_raw",
            device_class=SensorDeviceClass.TEMPERATURE,
            translation_key="temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            convert=lambda x, t: x / 100.0,
        ),
    ),
    MieleSensorDefinition(
        types=[
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            FRIDGE,
            FREEZER,
            FRIDGE_FREEZER,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            WINE_CABINET_FREEZER,
        ],
        description=MieleSensorDescription(
            key="temperature2",
            data_tag="state|temperature|1|value_raw",
            device_class=SensorDeviceClass.TEMPERATURE,
            translation_key="temperature_zone_2",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            convert=lambda x, t: x / 100.0,
            entity_registry_enabled_default=False,
        ),
    ),
    MieleSensorDefinition(
        types=[
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            FRIDGE,
            FREEZER,
            FRIDGE_FREEZER,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            WINE_CABINET_FREEZER,
        ],
        description=MieleSensorDescription(
            key="temperature3",
            data_tag="state|temperature|2|value_raw",
            device_class=SensorDeviceClass.TEMPERATURE,
            translation_key="temperature_zone_3",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            convert=lambda x, t: x / 100.0,
            entity_registry_enabled_default=False,
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            FRIDGE,
            FREEZER,
            FRIDGE_FREEZER,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            WINE_CABINET_FREEZER,
        ],
        description=MieleSensorDescription(
            key="targetTemperature",
            data_tag="state|targetTemperature|0|value_raw",
            device_class=SensorDeviceClass.TEMPERATURE,
            translation_key="target_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=EntityCategory.DIAGNOSTIC,
            convert=lambda x, t: int(x / 100.0),
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            FRIDGE,
            FREEZER,
            FRIDGE_FREEZER,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            WINE_CABINET_FREEZER,
        ],
        description=MieleSensorDescription(
            key="targetTemperature2",
            data_tag="state|targetTemperature|1|value_raw",
            device_class=SensorDeviceClass.TEMPERATURE,
            translation_key="target_temperature_zone_2",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=EntityCategory.DIAGNOSTIC,
            convert=lambda x, t: int(x / 100.0),
            entity_registry_enabled_default=False,
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            FRIDGE,
            FREEZER,
            FRIDGE_FREEZER,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            WINE_CABINET_FREEZER,
        ],
        description=MieleSensorDescription(
            key="targetTemperature3",
            data_tag="state|targetTemperature|2|value_raw",
            device_class=SensorDeviceClass.TEMPERATURE,
            translation_key="target_temperature_zone_3",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=EntityCategory.DIAGNOSTIC,
            convert=lambda x, t: int(x / 100.0),
            entity_registry_enabled_default=False,
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
            DISHWASHER,
            OVEN,
            OVEN_MICROWAVE,
            HOB_HIGHLIGHT,
            STEAM_OVEN,
            MICROWAVE,
            COFFEE_SYSTEM,
            HOOD,
            FRIDGE,
            FREEZER,
            FRIDGE_FREEZER,
            ROBOT_VACUUM_CLEANER,
            WASHER_DRYER,
            DISH_WARMER,
            HOB_INDUCTION,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            WINE_CABINET_FREEZER,
            HOB_INDUCT_EXTR,
        ],
        description=MieleSensorDescription(
            key="stateStatus",
            data_tag="state|status|value_raw",
            translation_key="status",
            convert=lambda x, t: STATE_STATUS.get(x, x),
            convert_icon=lambda t: APPLIANCE_ICONS.get(t, "mdi:state-machine"),
            extra_attributes={
                "serial_no": 0,
                "Raw value": 0,
                "appliance": 0,
                "manufacturer": 0,
                "model": 0,
                "HW version": 0,
                "SW version": 0,
            },
        ),
    ),
    MieleSensorDefinition(
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
            ROBOT_VACUUM_CLEANER,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
        ],
        description=MieleSensorDescription(
            key="stateProgramId",
            data_tag="state|ProgramID|value_raw",
            data_tag_loc="state|ProgramID|value_localized",
            translation_key="program_id",
            icon="mdi:selection-ellipse-arrow-inside",
            convert=lambda x, t: STATE_PROGRAM_ID.get(t, {}).get(x, x),
            available_states=lambda t: STATE_PROGRAM_ID.get(t, {}).values(),
            extra_attributes={"Raw value": 0},
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
            DISHWASHER,
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            ROBOT_VACUUM_CLEANER,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            COFFEE_SYSTEM,
        ],
        description=MieleSensorDescription(
            key="stateProgramType",
            data_tag="state|programType|value_raw",
            data_tag_loc="state|programType|value_localized",
            translation_key="program_type",
            icon="mdi:state-machine",
            convert=lambda x, t: STATE_PROGRAM_TYPE.get(x, x),
            extra_attributes={"Raw value": 0},
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
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
            ROBOT_VACUUM_CLEANER,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
        ],
        description=MieleSensorDescription(
            key="stateProgramPhase",
            data_tag="state|programPhase|value_raw",
            data_tag_loc="state|programPhase|value_localized",
            translation_key="program_phase",
            icon="mdi:tray-full",
            convert=lambda x, t: STATE_PROGRAM_PHASE.get(x, x),
            extra_attributes={"Raw value": 0},
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            WASHER_DRYER,
        ],
        description=MieleSensorDescription(
            key="stateSpinningSpeed",
            data_tag="state|spinningSpeed|value_raw",
            translation_key="spin_speed",
            icon="mdi:sync",
            native_unit_of_measurement="rpm",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHER_DRYER,
            TUMBLE_DRYER,
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
        ],
        description=MieleSensorDescription(
            key="stateDryingStep",
            data_tag="state|dryingStep|value_raw",
            data_tag_loc="state|dryingStep|value_localized",
            translation_key="drying_step",
            icon="mdi:water-outline",
            convert=lambda x, t: STATE_DRYING_STEP.get(x, x),
            extra_attributes={"Raw value": 0},
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
            DISHWASHER,
            OVEN,
            OVEN_MICROWAVE,
            STEAM_OVEN,
            MICROWAVE,
            ROBOT_VACUUM_CLEANER,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
        ],
        description=MieleSensorDescription(
            key="stateRemainingTime",
            data_tag="state|remainingTime|0",
            data_tag1="state|remainingTime|1",
            translation_key="remaining_time",
            icon="mdi:clock-end",
            native_unit_of_measurement=TIME_MINUTES,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
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
            ROBOT_VACUUM_CLEANER,
        ],
        description=MieleSensorDescription(
            key="stateRemainingTimeAbs",
            data_tag="state|remainingTime|0",
            data_tag1="state|remainingTime|1",
            translation_key="finish_at",
            icon="mdi:clock-end",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
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
        description=MieleSensorDescription(
            key="stateStartTime",
            data_tag="state|startTime|0",
            data_tag1="state|startTime|1",
            translation_key="start_time",
            icon="mdi:clock-start",
            native_unit_of_measurement=TIME_MINUTES,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
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
        description=MieleSensorDescription(
            key="stateStartTimeAbs",
            data_tag="state|startTime|0",
            data_tag1="state|startTime|1",
            translation_key="start_at",
            icon="mdi:calendar-clock",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
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
            ROBOT_VACUUM_CLEANER,
        ],
        description=MieleSensorDescription(
            key="stateElapsedTime",
            data_tag="state|elapsedTime|0",
            data_tag1="state|elapsedTime|1",
            translation_key="elapsed_time",
            icon="mdi:timelapse",
            native_unit_of_measurement=TIME_MINUTES,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
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
            ROBOT_VACUUM_CLEANER,
        ],
        description=MieleSensorDescription(
            key="stateElapsedTimeAbs",
            data_tag="state|elapsedTime|0",
            data_tag1="state|elapsedTime|1",
            translation_key="started_at",
            icon="mdi:clock-start",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            DISHWASHER,
            WASHER_DRYER,
        ],
        description=MieleSensorDescription(
            key="stateCurrentWaterConsumption",
            data_tag="state|ecoFeedback|currentWaterConsumption|value",
            translation_key="water_consumption",
            device_class=SensorDeviceClass.WATER,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfVolume.LITERS,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
            DISHWASHER,
            WASHER_DRYER,
        ],
        description=MieleSensorDescription(
            key="stateCurrentEnergyConsumption",
            data_tag="state|ecoFeedback|currentEnergyConsumption|value",
            translation_key="energy_consumption",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            DISHWASHER,
            WASHER_DRYER,
        ],
        description=MieleSensorDescription(
            key="stateWaterForecast",
            data_tag="state|ecoFeedback|waterForecast",
            translation_key="water_forecast",
            icon="mdi:water-outline",
            native_unit_of_measurement=PERCENTAGE,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            convert=lambda x, t: x * 100.0,
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
            DISHWASHER,
            WASHER_DRYER,
        ],
        description=MieleSensorDescription(
            key="stateEnergyForecast",
            data_tag="state|ecoFeedback|energyForecast",
            translation_key="energy_forecast",
            icon="mdi:lightning-bolt-outline",
            native_unit_of_measurement=PERCENTAGE,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            convert=lambda x, t: x * 100.0,
        ),
    ),
    MieleSensorDefinition(
        types=[
            ROBOT_VACUUM_CLEANER,
        ],
        description=MieleSensorDescription(
            key="batteryLevel",
            data_tag="state|batteryLevel",
            translation_key="battery",
            device_class=SensorDeviceClass.BATTERY,
            native_unit_of_measurement=PERCENTAGE,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
        types=[OVEN, OVEN_MICROWAVE, STEAM_OVEN_COMBI],
        description=MieleSensorDescription(
            key="coreTemperature",
            data_tag="state|coreTemperature|0|value_raw",
            translation_key="food_core_temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            convert=lambda x, t: x / 100.0,
        ),
    ),
    MieleSensorDefinition(
        types=[OVEN, OVEN_MICROWAVE, STEAM_OVEN_COMBI],
        description=MieleSensorDescription(
            key="coreTargetTemperature",
            data_tag="state|coreTargetTemperature|0|value_raw",
            translation_key="food_core_target_temperature",
            icon="mdi:thermometer-check",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            convert=lambda x, t: x / 100.0,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = await get_coordinator(hass, config_entry)

    entities = []
    for idx, ent in enumerate(coordinator.data):
        for definition in SENSOR_TYPES:
            if coordinator.data[ent]["ident|type|value_raw"] in definition.types:
                entities.append(
                    MieleSensor(coordinator, idx, ent, definition.description)
                )

    async_add_entities(entities)


class MieleSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    entity_description: MieleSensorDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleSensorDescription,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._idx = idx
        self._ent = ent
        self.entity_description = description
        _LOGGER.debug("init sensor %s", ent)
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
            hw_version=self.coordinator.data[self._ent]["ident|xkmIdentLabel|techType"],
            sw_version=self.coordinator.data[self._ent][
                "ident|xkmIdentLabel|releaseVersion"
            ],
        )
        if self.entity_description.convert_icon is not None:
            self._attr_icon = self.entity_description.convert_icon(
                self.coordinator.data[self._ent][self.entity_description.type_key_raw],
            )
        self._available_states = []
        if self.entity_description.available_states is not None:
            self._available_states = self.entity_description.available_states(
                self.coordinator.data[self._ent][self.entity_description.type_key_raw],
            )
        self._last_elapsed_time_reported = None
        self._last_started_time_reported = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.entity_description.key in [
            "stateRemainingTime",
            "stateStartTime",
        ]:
            return (
                self.coordinator.data[self._ent][self.entity_description.data_tag] * 60
                + self.coordinator.data[self._ent][self.entity_description.data_tag1]
            )

        if self.entity_description.key in [
            "stateRemainingTimeAbs",
            "stateStartTimeAbs",
        ]:
            now = dt_util.now()
            mins = (
                self.coordinator.data[self._ent][self.entity_description.data_tag] * 60
                + self.coordinator.data[self._ent][self.entity_description.data_tag1]
            )
            if mins == 0:
                return None
            # _LOGGER.debug(
            #     "Key:  %s | Dev: %s | Mins: %s | Now: %s | State: %s",
            #     self.entity_description.key,
            #     self._ent,
            #     mins,
            #     now,
            #     (now + timedelta(minutes=mins)).strftime("%H:%M"),
            # )
            return (now + timedelta(minutes=mins)).strftime("%H:%M")

        if self.entity_description.key in [
            "stateElapsedTime",
        ]:
            mins = (
                self.coordinator.data[self._ent][self.entity_description.data_tag] * 60
                + self.coordinator.data[self._ent][self.entity_description.data_tag1]
            )
            # Don't update sensor if state == program_ended
            if (
                self.coordinator.data[self._ent][self.entity_description.status_key_raw]
                == STATE_STATUS_PROGRAM_ENDED
            ):
                return self._last_elapsed_time_reported
            self._last_elapsed_time_reported = mins
            return mins

        if self.entity_description.key in [
            "stateElapsedTimeAbs",
        ]:
            now = dt_util.now()
            mins = (
                self.coordinator.data[self._ent][self.entity_description.data_tag] * 60
                + self.coordinator.data[self._ent][self.entity_description.data_tag1]
            )
            if mins == 0:
                return None
            _LOGGER.debug(
                "Key:  %s | Dev: %s | Mins: %s | Now: %s | State: %s",
                self.entity_description.key,
                self._ent,
                mins,
                now,
                (now + timedelta(minutes=mins)).strftime("%H:%M"),
            )
            started_time = (now - timedelta(minutes=mins)).strftime("%H:%M")
            # Don't update sensor if state == program_ended
            if (
                self.coordinator.data[self._ent][self.entity_description.status_key_raw]
                == STATE_STATUS_PROGRAM_ENDED
            ):
                return self._last_started_time_reported
            self._last_started_time_reported = started_time
            return started_time

        # Log raw and localized values for programID etc
        # Active if logger.level is DEBUG or INFO
        if _LOGGER.getEffectiveLevel() <= logging.INFO:
            if self.entity_description.key in {
                "stateProgramPhase",
                "stateProgramId",
                "stateProgramType",
            }:
                while len(self.hass.data[DOMAIN]["id_log"]) >= 500:
                    self.hass.data[DOMAIN]["id_log"].pop()

                self.hass.data[DOMAIN]["id_log"].append(
                    {
                        "appliance": self.coordinator.data[self._ent][
                            self.entity_description.type_key
                        ],
                        "key": self.entity_description.key,
                        "raw": self.coordinator.data[self._ent][
                            self.entity_description.data_tag
                        ],
                        "localized": self.coordinator.data[self._ent][
                            self.entity_description.data_tag_loc
                        ],
                    }
                )

        # Show 0 consumption when the appliance is not running,
        # to correctly reset utility meter cycle. Ignore this when
        # appliance is not connected (it may disconnect while a program
        # is running causing problems in energy stats).
        state = self.coordinator.data[self._ent][self.entity_description.status_key_raw]
        if self.entity_description.key in [
            "stateCurrentEnergyConsumption",
            "stateCurrentWaterConsumption",
        ] and state in [
            STATE_STATUS_ON,
            STATE_STATUS_OFF,
            STATE_STATUS_PROGRAMMED,
            STATE_STATUS_WAITING_TO_START,
            STATE_STATUS_IDLE,
            STATE_STATUS_SERVICE,
        ]:
            return 0

        if (
            self.coordinator.data[self._ent].get(self.entity_description.data_tag)
            is None
        ):
            return None
        if (
            self.coordinator.data[self._ent][self.entity_description.data_tag] == -32766
            or self.coordinator.data[self._ent][self.entity_description.data_tag]
            == -32768
        ):
            return None
        if (
            self.entity_description.key in ["stateProgramId", "stateProgramPhase"]
            and self.coordinator.data[self._ent][self.entity_description.data_tag] <= 0
        ):
            return None

        if self.entity_description.convert is None:
            return self.coordinator.data[self._ent][self.entity_description.data_tag]

        # If configuration.yaml contains an overridden mapping, use that value if available
        custom_mapped_value = self._get_custom_mapped_value(
            self.coordinator.data[self._ent][self.entity_description.data_tag]
        )
        if (
            custom_mapped_value is not None
            and custom_mapped_value in self._available_states
        ):
            return custom_mapped_value

        # Otherwise use converter specified in entity description
        return self.entity_description.convert(
            self.coordinator.data[self._ent][self.entity_description.data_tag],
            self.coordinator.data[self._ent][self.entity_description.type_key_raw],
        )

    @property
    def available(self):
        """Return the availability of the entity."""

        if self.entity_description.key == "stateStatus":
            return True

        if not self.coordinator.last_update_success:
            return False

        return (
            self.coordinator.data[self._ent][self.entity_description.status_key_raw]
            != STATE_STATUS_NOT_CONNECTED
        )

    @property
    def extra_state_attributes(self):
        if self.entity_description.extra_attributes is None:
            return None
        attr = self.entity_description.extra_attributes
        if "Raw value" in self.entity_description.extra_attributes:
            attr["Raw value"] = self.coordinator.data[self._ent][
                self.entity_description.data_tag
            ]
            attr["Localized"] = self.coordinator.data[self._ent][
                self.entity_description.data_tag.replace("_raw", "_localized")
            ]
        if "serial_no" in self.entity_description.extra_attributes:
            attr["serial_no"] = self._ent

        if "appliance" in self.entity_description.extra_attributes:
            attr["appliance"] = self.coordinator.data[self._ent][
                self.entity_description.type_key
            ]

        if "manufacturer" in self.entity_description.extra_attributes:
            attr["manufacturer"] = MANUFACTURER

        if "model" in self.entity_description.extra_attributes:
            attr["model"] = self.coordinator.data[self._ent][
                "ident|deviceIdentLabel|techType"
            ]

        if "HW version" in self.entity_description.extra_attributes:
            attr["HW version"] = self.coordinator.data[self._ent][
                "ident|xkmIdentLabel|techType"
            ]

        if "SW version" in self.entity_description.extra_attributes:
            attr["SW version"] = self.coordinator.data[self._ent][
                "ident|xkmIdentLabel|releaseVersion"
            ]

        return attr

    def _get_sensor_config(self):
        """Return sensor config for current entity."""
        return self.hass.data[DOMAIN].get(CONF_SENSORS, {}).get(self.entity_id, {})

    def _get_custom_mapped_value(self, raw_value):
        """Return sensor value mapping for current entity."""
        return self._get_sensor_config().get(CONF_PROGRAM_IDS, {}).get(raw_value, None)
