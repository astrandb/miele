"""Platform for Miele binary_sensor integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable, Final

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
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
class MieleBinarySensorDescription(BinarySensorEntityDescription):
    """Class describing Miele binary sensor entities."""

    data_tag: str | None = None
    type_key: str = "ident|type|value_localized"
    convert: Callable[[Any], Any] | None = None


@dataclass
class MieleBinarySensorDefinition:
    """Class for defining binary sensor entities."""

    types: tuple[int, ...]
    description: MieleBinarySensorDescription = None


BINARY_SENSOR_TYPES: Final[tuple[MieleBinarySensorDefinition, ...]] = (
    MieleBinarySensorDefinition(
        types=[
            WASHING_MACHINE,
            TUMBLE_DRYER,
            TUMBLE_DRYER_SEMI_PROFESSIONAL,
            DISHWASHER,
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
            WINE_CABINET_FREEZER,
        ],
        description=MieleBinarySensorDescription(
            key="door",
            data_tag="state|signalDoor",
            device_class=BinarySensorDeviceClass.DOOR,
            translation_key="door",
        ),
    ),
    MieleBinarySensorDefinition(
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
            HOOD,
            FRIDGE,
            FREEZER,
            FRIDGE_FREEZER,
            ROBOT_VACUUM_CLEANER,
            WASHER_DRYER,
            DISH_WARMER,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            WINE_CABINET_FREEZER,
            HOB_INDUCT_EXTR,
        ],
        description=MieleBinarySensorDescription(
            key="info",
            data_tag="state|signalInfo",
            device_class=BinarySensorDeviceClass.PROBLEM,
            translation_key="info",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleBinarySensorDefinition(
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
        description=MieleBinarySensorDescription(
            key="failure",
            data_tag="state|signalFailure",
            device_class=BinarySensorDeviceClass.PROBLEM,
            translation_key="failure",
            icon="mdi:alert",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleBinarySensorDefinition(
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
            HOOD,
            FRIDGE,
            FREEZER,
            FRIDGE_FREEZER,
            ROBOT_VACUUM_CLEANER,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            WINE_CABINET_FREEZER,
            HOB_INDUCT_EXTR,
        ],
        description=MieleBinarySensorDescription(
            key="remoteEnable",
            data_tag="state|remoteEnable|fullRemoteControl",
            translation_key="remote_control",
            icon="mdi:remote",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ),
    MieleBinarySensorDefinition(
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
            HOOD,
            FRIDGE,
            FREEZER,
            FRIDGE_FREEZER,
            ROBOT_VACUUM_CLEANER,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            WINE_CABINET_FREEZER,
            HOB_INDUCT_EXTR,
        ],
        description=MieleBinarySensorDescription(
            key="smartGrid",
            data_tag="state|remoteEnable|smartGrid",
            translation_key="smart_grid",
            icon="mdi:view-grid-plus-outline",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
        ),
    ),
    MieleBinarySensorDefinition(
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
            HOOD,
            FRIDGE,
            FREEZER,
            FRIDGE_FREEZER,
            ROBOT_VACUUM_CLEANER,
            WASHER_DRYER,
            STEAM_OVEN_COMBI,
            WINE_CABINET,
            WINE_CONDITIONING_UNIT,
            WINE_STORAGE_CONDITIONING_UNIT,
            STEAM_OVEN_MICRO,
            DIALOG_OVEN,
            WINE_CABINET_FREEZER,
            HOB_INDUCT_EXTR,
        ],
        description=MieleBinarySensorDescription(
            key="mobileStart",
            data_tag="state|remoteEnable|mobileStart",
            translation_key="mobile_start",
            icon="mdi:cellphone-wireless",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
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
        for definition in BINARY_SENSOR_TYPES:
            if coordinator.data[ent]["ident|type|value_raw"] in definition.types:
                entities.append(
                    MieleBinarySensor(coordinator, idx, ent, definition.description)
                )

    async_add_entities(entities)


class MieleBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Binary Sensor."""

    entity_description: MieleBinarySensorDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleBinarySensorDescription,
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
        )

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._ent][self.entity_description.data_tag]

    @property
    def available(self):
        """Return the availability of the entity."""

        if not self.coordinator.last_update_success:
            return False

        return self.coordinator.data[self._ent]["state|status|value_raw"] != 255
