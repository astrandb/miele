"""Platform for Miele number entity."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.core import HomeAssistant

# from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import get_coordinator
from .const import (
    API,
    DOMAIN,
    MieleAppliance,
)
from .entity import MieleEntity

_LOGGER = logging.getLogger(__name__)

HOB_TYPES = (
    MieleAppliance.HOB_INDUCT_EXTR,
    MieleAppliance.HOB_HIGHLIGHT,
    MieleAppliance.HOB_INDUCTION,
)

PLATE_MAP = {
    0: 0,
    110: 0.5,
    220: 0.5,
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
    18: 9.5,
    117: 10,
    118: 10,
    217: 110,
}

DEFAULT_PLATE_COUNT = 4

PLATE_COUNT = {
    "KM7678": 6,
    "KM7697": 6,
    "KM7878": 6,
    "KM7897": 6,
    "KMDA7633": 5,
    "KMDA7634": 5,
    "KMX": 6,
}


def get_plate_count(tech_type):
    """Get number of zones."""
    stripped = tech_type.replace(" ", "")
    for prefix, plates in PLATE_COUNT.items():
        if stripped.startswith(prefix):
            return plates
    return DEFAULT_PLATE_COUNT


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

    types: tuple[MieleAppliance, ...]
    description: MieleNumberDescription = None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator = await get_coordinator(hass, config_entry)

    entities = []
    for idx, ent in enumerate(coordinator.data):
        if coordinator.data[ent]["ident|type|value_raw"] in HOB_TYPES:
            tech_type = coordinator.data[ent]["ident|deviceIdentLabel|techType"]
            api_plates = 0
            for i in range(8):
                if f"state|plateStep|{i}|value_raw" in coordinator.data[ent]:
                    api_plates = i
            if api_plates == 0:
                plates = get_plate_count(tech_type)
            else:
                plates = api_plates + 1

            if plates < api_plates + 1:
                _LOGGER.warning(
                    "Inconsistent number of zones - API %s reports %s zones",
                    tech_type,
                    api_plates + 1,
                )
            for plate_no in range(plates):
                description = MieleNumberDescription(
                    key="plate",
                    data_tag=f"state|plateStep|{plate_no}|value_raw",
                    icon="mdi:stove",
                    translation_key="plate",
                    translation_placeholders={"plate_no": f"{plate_no + 1}"},
                    zone=plate_no,
                    native_min_value=0.0,
                    native_max_value=10.0,
                    native_step=0.5,
                )
                entities.append(
                    MieleNumber(coordinator, idx, ent, description, hass, config_entry)
                )

    async_add_entities(entities)


class MieleNumber(MieleEntity, NumberEntity):
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
        super().__init__(coordinator, idx, ent, description)
        self._api = hass.data[DOMAIN][entry.entry_id][API]
        self._ed = description
        _LOGGER.debug("Init number %s", ent)
        # deviates from MieleEntity
        self._attr_unique_id = f"{self._ed.key}-{self._ed.zone}{self._ent}"
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self):
        """Return native value."""
        if self.coordinator.data[self._ent].get(self._ed.data_tag) is None:
            return 0
        try:
            retval = PLATE_MAP[self.coordinator.data[self._ent][self._ed.data_tag]]
        except KeyError:
            _LOGGER.debug(
                "Unknown state for %s => %s",
                self._ent,
                self.coordinator.data[self._ent][self._ed.data_tag],
            )
            return None
        return retval

    @property
    def available(self):
        """Return the availability of the entity."""

        if not self.coordinator.last_update_success:
            return False

        if self.coordinator.data[self._ent].get(self._ed.data_tag) is None:
            return False

        return self.coordinator.data[self._ent]["state|status|value_raw"] != 255

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        self.async_write_ha_state()
