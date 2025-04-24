"""Platform for Miele sensor integration."""
# pylint: disable=too-many-lines

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from . import get_coordinator
from .const import (
    APPLIANCE_ICONS,
    CONF_PROGRAM_IDS,
    CONF_SENSORS,
    DOMAIN,
    MANUFACTURER,
    STATE_DRYING_STEP,
    STATE_PROGRAM_ID,
    STATE_PROGRAM_PHASE,
    STATE_PROGRAM_TYPE,
    STATE_STATUS,
    STATE_STATUS_IDLE,
    STATE_STATUS_NOT_CONNECTED,
    STATE_STATUS_OFF,
    STATE_STATUS_ON,
    STATE_STATUS_PAUSE,
    STATE_STATUS_PROGRAM_ENDED,
    STATE_STATUS_PROGRAMMED,
    STATE_STATUS_RUNNING,
    STATE_STATUS_SERVICE,
    STATE_STATUS_WAITING_TO_START,
    MieleAppliance,
)
from .entity import MieleEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class MieleSensorDescription(SensorEntityDescription):
    """Class describing Miele sensor entities."""

    data_tag: str | None = None
    data_tag1: str | None = None
    data_tag2: str | None = None
    data_tag3: str | None = None
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

    types: tuple[MieleAppliance, ...]
    description: MieleSensorDescription = None


SENSOR_TYPES: Final[tuple[MieleSensorDefinition, ...]] = (
    MieleSensorDefinition(
        types=[
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.DISH_WARMER,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.WINE_CABINET_FREEZER,
            MieleAppliance.STEAM_OVEN_MK2,
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
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.WINE_CABINET_FREEZER,
            MieleAppliance.STEAM_OVEN_MK2,
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
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.WINE_CABINET_FREEZER,
            MieleAppliance.STEAM_OVEN_MK2,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.DISH_WARMER,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.WINE_CABINET_FREEZER,
            MieleAppliance.STEAM_OVEN_MK2,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.WINE_CABINET_FREEZER,
            MieleAppliance.STEAM_OVEN_MK2,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.WINE_CABINET_FREEZER,
            MieleAppliance.STEAM_OVEN_MK2,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.DISHWASHER,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.HOB_HIGHLIGHT,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.COFFEE_SYSTEM,
            MieleAppliance.HOOD,
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.ROBOT_VACUUM_CLEANER,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.DISH_WARMER,
            MieleAppliance.HOB_INDUCTION,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.WINE_CABINET_FREEZER,
            MieleAppliance.STEAM_OVEN_MK2,
            MieleAppliance.HOB_INDUCT_EXTR,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.DISHWASHER,
            MieleAppliance.DISH_WARMER,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.COFFEE_SYSTEM,
            MieleAppliance.ROBOT_VACUUM_CLEANER,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.STEAM_OVEN_MK2,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.DISHWASHER,
            MieleAppliance.DISH_WARMER,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.ROBOT_VACUUM_CLEANER,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.COFFEE_SYSTEM,
            MieleAppliance.STEAM_OVEN_MK2,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.DISHWASHER,
            MieleAppliance.DISH_WARMER,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.COFFEE_SYSTEM,
            MieleAppliance.ROBOT_VACUUM_CLEANER,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.STEAM_OVEN_MK2,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.WASHER_DRYER,
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
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.DISHWASHER,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.ROBOT_VACUUM_CLEANER,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.STEAM_OVEN_MK2,
        ],
        description=MieleSensorDescription(
            key="stateRemainingTime",
            data_tag="state|remainingTime|0",
            data_tag1="state|remainingTime|1",
            translation_key="remaining_time",
            icon="mdi:clock-end",
            native_unit_of_measurement=UnitOfTime.MINUTES,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
        types=[
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.DISHWASHER,
            MieleAppliance.DISH_WARMER,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.ROBOT_VACUUM_CLEANER,
            MieleAppliance.STEAM_OVEN_MK2,
        ],
        description=MieleSensorDescription(
            key="stateRemainingTimeAbs",
            data_tag="state|remainingTime|0",
            data_tag1="state|remainingTime|1",
            # also account for time until start in finish time (delayed start)
            data_tag2="state|startTime|0",
            data_tag3="state|startTime|1",
            translation_key="finish_at",
            icon="mdi:clock-end",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
        types=[
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.DISHWASHER,
            MieleAppliance.DISH_WARMER,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.STEAM_OVEN_MK2,
        ],
        description=MieleSensorDescription(
            key="stateStartTime",
            data_tag="state|startTime|0",
            data_tag1="state|startTime|1",
            translation_key="start_time",
            icon="mdi:clock-start",
            native_unit_of_measurement=UnitOfTime.MINUTES,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
        types=[
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.DISHWASHER,
            MieleAppliance.DISH_WARMER,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.STEAM_OVEN_MK2,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.DISHWASHER,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.ROBOT_VACUUM_CLEANER,
            MieleAppliance.STEAM_OVEN_MK2,
        ],
        description=MieleSensorDescription(
            key="stateElapsedTime",
            data_tag="state|elapsedTime|0",
            data_tag1="state|elapsedTime|1",
            translation_key="elapsed_time",
            icon="mdi:timelapse",
            native_unit_of_measurement=UnitOfTime.MINUTES,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleSensorDefinition(
        types=[
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.DISHWASHER,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.ROBOT_VACUUM_CLEANER,
            MieleAppliance.STEAM_OVEN_MK2,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.DISHWASHER,
            MieleAppliance.WASHER_DRYER,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.DISHWASHER,
            MieleAppliance.WASHER_DRYER,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.DISHWASHER,
            MieleAppliance.WASHER_DRYER,
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
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.DISHWASHER,
            MieleAppliance.WASHER_DRYER,
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
            MieleAppliance.ROBOT_VACUUM_CLEANER,
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
        types=[
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.STEAM_OVEN_MK2,
        ],
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
        types=[
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.STEAM_OVEN_MK2,
        ],
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

    entities = [
        MieleSensor(coordinator, idx, ent, definition.description)
        for idx, ent in enumerate(coordinator.data)
        for definition in SENSOR_TYPES
        if coordinator.data[ent]["ident|type|value_raw"] in definition.types
    ]

    async_add_entities(entities)


class MieleSensor(MieleEntity, SensorEntity):
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
        super().__init__(coordinator, idx, ent, description)
        _LOGGER.debug("init sensor %s", ent)
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
        self._last_abs_time = {}
        self._last_consumption_valid = True

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.entity_description.key in [
            "stateRemainingTime",
            "stateStartTime",
        ]:
            return self._get_minutes()

        if self.entity_description.key in [
            "stateElapsedTime",
        ]:
            mins = self._get_minutes()
            # Keep value when program ends
            if (
                self.coordinator.data[self._ent][self.entity_description.status_key_raw]
                == STATE_STATUS_PROGRAM_ENDED
            ):
                return self._last_elapsed_time_reported
            # Force 0 when appliance is off
            if (
                self.coordinator.data[self._ent][self.entity_description.status_key_raw]
                == STATE_STATUS_OFF
            ):
                return 0
            self._last_elapsed_time_reported = mins
            return mins

        if self.entity_description.key in [
            "stateRemainingTimeAbs",
            "stateStartTimeAbs",
        ]:
            return self._get_absolute_time()

        if self.entity_description.key in [
            "stateElapsedTimeAbs",
        ]:
            started_time = self._get_absolute_time(sub=True)
            # Don't update sensor if state == program_ended
            if (
                self.coordinator.data[self._ent][self.entity_description.status_key_raw]
                == STATE_STATUS_PROGRAM_ENDED
            ):
                return self._last_started_time_reported
            # Force no state when appliance is off
            if (
                self.coordinator.data[self._ent][self.entity_description.status_key_raw]
                == STATE_STATUS_OFF
            ):
                return None
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

        state = self.coordinator.data[self._ent][self.entity_description.status_key_raw]
        if self.entity_description.key in [
            "stateCurrentEnergyConsumption",
            "stateCurrentWaterConsumption",
        ]:
            current_consumption = self.coordinator.data[self._ent].get(self.entity_description.data_tag)
            # Show 0 consumption when the appliance is not running,
            # to correctly reset utility meter cycle. Ignore this when
            # appliance is not connected (it may disconnect while a program
            # is running causing problems in energy stats).
            if state in [
                STATE_STATUS_ON,
                STATE_STATUS_OFF,
                STATE_STATUS_PROGRAMMED,
                STATE_STATUS_WAITING_TO_START,
                STATE_STATUS_IDLE,
                STATE_STATUS_SERVICE,
            ]:
                self._last_consumption_valid = False
                return 0
            # If running or paused, instead, mark valid the consumption and 
            # report it only if it starts from 0, otherwise it results as a 
            # spike due to a glitch in API that is reporting the consumption 
            # of last cycle for a couple of seconds immediately after starting 
            # the program
            elif state in [
                STATE_STATUS_RUNNING,
                STATE_STATUS_PAUSE,
            ] and current_consumption == 0:
                self._last_consumption_valid = True
            elif state in [
                STATE_STATUS_RUNNING,
                STATE_STATUS_PAUSE,
            ] and current_consumption is not None and current_consumption > 0 and not self._last_consumption_valid:
                return 0

        if (
            self.coordinator.data[self._ent].get(self.entity_description.data_tag)
            is None
        ):
            return None
        if self.coordinator.data[self._ent].get(
            self.entity_description.data_tag, -32768
        ) in (
            -32766,
            -32768,
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

    def _get_minutes(self):
        mins = (
            self.coordinator.data[self._ent][self.entity_description.data_tag] * 60
            + self.coordinator.data[self._ent][self.entity_description.data_tag1]
        )
        if (
            self.entity_description.data_tag2 is not None
            and self.entity_description.data_tag2 is not None
        ):
            mins = mins + (
                self.coordinator.data[self._ent][self.entity_description.data_tag2] * 60
                + self.coordinator.data[self._ent][self.entity_description.data_tag3]
            )
        return mins

    def _get_absolute_time(self, sub=False):
        now = dt_util.now().replace(second=0, microsecond=0)
        mins = self._get_minutes()
        if mins == 0:
            return None
        if sub:
            val = now - timedelta(minutes=mins)
        else:
            val = now + timedelta(minutes=mins)
        formatted = val.strftime("%H:%M")
        _LOGGER.debug(
            "Key:  %s | Dev: %s | Mins: %s | Now: %s | State: %s",
            self.entity_description.key,
            self._ent,
            mins,
            now,
            formatted,
        )
        # check for previous value and return it if differning of +/-1 min
        if self.entity_description.key in self._last_abs_time:
            previous_value = self._last_abs_time[self.entity_description.key]
            prev_minute = previous_value - timedelta(seconds=120)
            next_minute = previous_value + timedelta(seconds=120)
            if prev_minute <= val <= next_minute:
                return previous_value.strftime("%H:%M")
        self._last_abs_time[self.entity_description.key] = val
        return formatted

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
        """Return extra_state_attributes."""
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
