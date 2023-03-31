"""Platform for Miele number entity."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable, Final

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
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
from .const import API, DOMAIN, HOB_INDUCT_EXTR, MANUFACTURER

_LOGGER = logging.getLogger(__name__)

PLATE_MAP = {
    0: 0,
    110: 0.5,
    1: 1,
    2: 1.5,
    3: 2,
    4: 2.5,
    5: 3,
    6: 3.5,
    7: 4,
    8: 4.5,
    9: 5,
    10: 5.5,
    11: 6,
    12: 6.5,
    13: 7,
    14: 7.5,
    15: 8,
    16: 8.5,
    17: 9,
    117: 10,
}


@dataclass
class MieleNumberDescriptionMixin:
    """Required values when describing Miele number entities."""

    data_tag: str


@dataclass
class MieleNumberDescription(NumberEntityDescription, MieleNumberDescriptionMixin):
    """Class describing Miele number entities."""

    type_key: str = "ident|type|value_localized"

    convert: Callable[[Any], Any] | None = None
    zone: int = 0


@dataclass
class MieleNumberDefinition:
    """Class for defining number entities."""

    types: tuple[int, ...]
    description: MieleNumberDescription = None


NUMBER_TYPES: Final[tuple[MieleNumberDefinition, ...]] = (
    MieleNumberDefinition(
        types=[
            HOB_INDUCT_EXTR,
        ],
        description=MieleNumberDescription(
            key="plate",
            data_tag="state|plateStep|0|value_raw",
            icon="mdi:stove",
            translation_key="plate_0",
            zone=0,
            native_min_value=0.0,
            native_max_value=10.0,
            native_step=0.5,
        ),
    ),
    MieleNumberDefinition(
        types=[
            HOB_INDUCT_EXTR,
        ],
        description=MieleNumberDescription(
            key="plate",
            data_tag="state|plateStep|1|value_raw",
            icon="mdi:stove",
            translation_key="plate_1",
            zone=1,
            native_min_value=0.0,
            native_max_value=10.0,
            native_step=0.5,
        ),
    ),
    MieleNumberDefinition(
        types=[
            HOB_INDUCT_EXTR,
        ],
        description=MieleNumberDescription(
            key="plate",
            data_tag="state|plateStep|2|value_raw",
            icon="mdi:stove",
            translation_key="plate_2",
            zone=2,
            native_min_value=0.0,
            native_max_value=10.0,
            native_step=0.5,
        ),
    ),
    MieleNumberDefinition(
        types=[
            HOB_INDUCT_EXTR,
        ],
        description=MieleNumberDescription(
            key="plate",
            data_tag="state|plateStep|3|value_raw",
            icon="mdi:stove",
            translation_key="plate_3",
            zone=3,
            native_min_value=0.0,
            native_max_value=10.0,
            native_step=0.5,
        ),
    ),
    MieleNumberDefinition(
        types=[
            HOB_INDUCT_EXTR,
        ],
        description=MieleNumberDescription(
            key="plate",
            data_tag="state|plateStep|4|value_raw",
            icon="mdi:stove",
            translation_key="plate_4",
            zone=4,
            native_min_value=0.0,
            native_max_value=10.0,
            native_step=0.5,
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator = await get_coordinator(hass, config_entry)

    entities = []
    for idx, ent in enumerate(coordinator.data):
        for definition in NUMBER_TYPES:
            if coordinator.data[ent]["ident|type|value_raw"] in definition.types and (
                coordinator.data[ent].get(definition.description.data_tag) is not None
            ):
                entities.append(
                    MieleNumber(
                        coordinator,
                        idx,
                        ent,
                        definition.description,
                        hass,
                        config_entry,
                    )
                )

    async_add_entities(entities)


class MieleNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Number."""

    entity_description: MieleNumberDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        idx,
        ent,
        description: MieleNumberDescription,
        hass: HomeAssistant,
        entry: ConfigType,
    ):
        """Initialize the number."""
        super().__init__(coordinator)
        self._api = hass.data[DOMAIN][entry.entry_id][API]

        self._idx = idx
        self._ent = ent
        self.entity_description = description
        self._ed = description
        _LOGGER.debug("Init number %s", ent)
        appl_type = self.coordinator.data[self._ent][self._ed.type_key]
        if appl_type == "":
            appl_type = self.coordinator.data[self._ent][
                "ident|deviceIdentLabel|techType"
            ]
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{self._ed.key}-{self._ed.zone}{self._ent}"
        # _LOGGER.debug("icon: %s | %s", self._ed.icon, self._ed.icon)
        # self._attr_icon = self._ed.icon
        self._attr_mode = NumberMode.SLIDER
        # self._attr_max_value = self._ed.max_value
        # self._attr_min_value = self._ed.min_value
        # self._attr_step = self._ed.step
        # self._attr_supported_features = self._ed.supported_features
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ent)},
            name=appl_type,
            manufacturer=MANUFACTURER,
            model=self.coordinator.data[self._ent]["ident|deviceIdentLabel|techType"],
        )

    @property
    def native_value(self):
        if self.coordinator.data[self._ent].get(self._ed.data_tag) is None:
            return
        return PLATE_MAP[self.coordinator.data[self._ent][self._ed.data_tag]]

    @property
    def available(self):
        """Return the availability of the entity."""

        if not self.coordinator.last_update_success:
            return False

        return self.coordinator.data[self._ent]["state|status|value_raw"] != 255

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        self.async_write_ha_state()
