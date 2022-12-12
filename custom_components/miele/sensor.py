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
    COFFEE_SYSTEM,
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
    MICROWAVE,
    OVEN,
    OVEN_MICROWAVE,
    ROBOT_VACUUM_CLEANER,
    STATE_PROGRAM_ID,
    STATE_PROGRAM_PHASE,
    STATE_PROGRAM_TYPE,
    STATE_STATUS,
    STEAM_OVEN,
    STEAM_OVEN_COMBI,
    STEAM_OVEN_MICRO,
    TUMBLE_DRYER,
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
    """Class describing Weatherlink sensor entities."""

    data_tag: str | None = None
    data_tag1: str | None = None
    data_tag_loc: str | None = None
    type_key: str = "ident|type|value_localized"
    convert: Callable[[Any], Any] | None = None
    decimals: int = 1
    extra_attributes: dict[str, Any] | None = None


@dataclass
class MieleSensorDefinition:
    """Class for defining sensor entities."""

    types: tuple[int, ...]
    description: MieleSensorDescription = None


SENSOR_TYPES: Final[tuple[MieleSensorDefinition, ...]] = (
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
            key="temperature",
            data_tag="state|temperature|0|value_raw",
            device_class=SensorDeviceClass.TEMPERATURE,
            name="Temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            convert=lambda x, t: x / 100.0,
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
            key="temperature2",
            data_tag="state|temperature|1|value_raw",
            device_class=SensorDeviceClass.TEMPERATURE,
            name="Temperature zone 2",
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
            name="Temperature zone 3",
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
            name="Target temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            convert=lambda x, t: x / 100.0,
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
            name="Target temperature zone 2",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
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
            key="targetTemperature3",
            data_tag="state|targetTemperature|2|value_raw",
            device_class=SensorDeviceClass.TEMPERATURE,
            name="Target temperature zone 3",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            convert=lambda x, t: x / 100.0,
            entity_registry_enabled_default=False,
        ),
    ),
    MieleSensorDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
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
            name="Status",
            device_class="miele__state_status",
            icon="mdi:state-machine",
            convert=lambda x, t: STATE_STATUS.get(x, x),
            extra_attributes={"Serial no": 0, "Raw value": 0},
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
            name="Program",
            device_class="miele__state_program_id",
            icon="mdi:state-machine",
            convert=lambda x, t: STATE_PROGRAM_ID.get(t, {}).get(x, x),
            extra_attributes={"Raw value": 0},
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
            ROBOT_VACUUM_CLEANER,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
        ],
        description=MieleSensorDescription(
            key="stateProgramType",
            data_tag="state|programType|value_raw",
            data_tag_loc="state|programType|value_localized",
            name="Program type",
            device_class="miele__state_program_type",
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
            name="Program phase",
            device_class="miele__state_program_phase",
            icon="mdi:state-machine",
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
            name="Spin speed",
            icon="mdi:sync",
            native_unit_of_measurement="rpm",
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
            name="Remaining time",
            icon="mdi:clock-end",
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
        ],
        description=MieleSensorDescription(
            key="stateRemainingTimeAbs",
            data_tag="state|remainingTime|0",
            data_tag1="state|remainingTime|1",
            name="Finish at",
            icon="mdi:clock-end",
            native_unit_of_measurement="",
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
        ],
        description=MieleSensorDescription(
            key="stateStartTime",
            data_tag="state|startTime|0",
            data_tag1="state|startTime|1",
            name="Start time",
            icon="mdi:clock-start",
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
        ],
        description=MieleSensorDescription(
            key="stateStartTimeAbs",
            data_tag="state|startTime|0",
            data_tag1="state|startTime|1",
            name="Start at",
            icon="mdi:clock-start",
            native_unit_of_measurement="",
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
        ],
        description=MieleSensorDescription(
            key="stateElapsedTime",
            data_tag="state|elapsedTime|0",
            data_tag1="state|elapsedTime|1",
            name="Elapsed time",
            icon="mdi:timer-outline",
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
        ],
        description=MieleSensorDescription(
            key="stateElapsedTimeAbs",
            data_tag="state|elapsedTime|0",
            data_tag1="state|elapsedTime|1",
            name="Started at",
            icon="mdi:timer-outline",
            native_unit_of_measurement="",
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
            name="Water consumption",
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
            DISHWASHER,
            WASHER_DRYER,
        ],
        description=MieleSensorDescription(
            key="stateCurrentEnergyConsumption",
            data_tag="state|ecoFeedback|currentEnergyConsumption|value",
            name="Energy consumption",
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
            name="Water forecast",
            icon="mdi:water-percent",
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
            DISHWASHER,
            WASHER_DRYER,
        ],
        description=MieleSensorDescription(
            key="stateEnergyForecast",
            data_tag="state|ecoFeedback|energyForecast",
            name="Energy forecast",
            icon="mdi:label-percent-outline",
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
            name="Battery",
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
            name="Food core temperature",
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
            name="Food core target temperature",
            icon="mdi:thermometer-check",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
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
        # self._attr_name = f"{appl_type} {self.entity_description.name}"
        self._attr_name = self.entity_description.name
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{self.entity_description.key}-{self._ent}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=appl_type,
            manufacturer="Miele",
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"],
            hw_version=self.coordinator.data[self._ent]["ident|xkmIdentLabel|techType"],
            sw_version=self.coordinator.data[self._ent][
                "ident|xkmIdentLabel|releaseVersion"
            ],
        )
        self._last_started_time_reported = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.entity_description.key in [
            "stateRemainingTime",
            "stateStartTime",
            "stateElapsedTime",
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
            if self.coordinator.data[self._ent]["state|status|value_raw"] == 7:
                return self._last_started_time_reported
            self._last_started_time_reported = started_time
            return started_time

        # Log raw and localized values for programID etc
        # Active if logger.level is DEBUG or INFO
        if _LOGGER.getEffectiveLevel() <= logging.INFO:
            if self.entity_description.key in {
                "stateProgramPhase",
                "stateProgramID",
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

        if self.entity_description.convert is None:
            return self.coordinator.data[self._ent][self.entity_description.data_tag]
        else:
            return self.entity_description.convert(
                self.coordinator.data[self._ent][self.entity_description.data_tag],
                self.coordinator.data[self._ent]["ident|type|value_raw"],
            )

    @property
    def available(self):
        """Return the availability of the entity."""

        if self.entity_description.key == "stateStatus":
            return True

        if not self.coordinator.last_update_success:
            return False

        return self.coordinator.data[self._ent]["state|status|value_raw"] != 255

    @property
    def extra_state_attributes(self):
        if self.entity_description.extra_attributes is None:
            return
        attr = self.entity_description.extra_attributes
        if "Raw value" in self.entity_description.extra_attributes:
            attr["Raw value"] = self.coordinator.data[self._ent][
                self.entity_description.data_tag
            ]
            attr["Localized"] = self.coordinator.data[self._ent][
                self.entity_description.data_tag.replace("_raw", "_localized")
            ]
        if "Serial no" in self.entity_description.extra_attributes:
            attr["Serial no"] = self._ent

        return attr
