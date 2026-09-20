"""Binary sensor platform for parkrun."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import ParkrunEntity
from .models import ParkrunAthleteData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import ParkrunConfigEntry
    from .coordinator import ParkrunCoordinator


@dataclass(frozen=True, kw_only=True)
class ParkrunBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a parkrun binary sensor."""

    value_fn: Callable[[ParkrunAthleteData], bool | None]


BINARY_SENSOR_DESCRIPTIONS: tuple[ParkrunBinarySensorEntityDescription, ...] = (
    ParkrunBinarySensorEntityDescription(
        key="latest_was_pb",
        translation_key="latest_was_pb",
        icon="mdi:trophy-variant",
        value_fn=lambda data: data.latest_was_pb,
    ),
    ParkrunBinarySensorEntityDescription(
        key="latest_first_timer",
        translation_key="latest_first_timer",
        icon="mdi:new-box",
        value_fn=lambda data: data.latest_first_timer,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ParkrunConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up parkrun binary sensors from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        ParkrunBinarySensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class ParkrunBinarySensor(ParkrunEntity, BinarySensorEntity):
    """A parkrun binary sensor."""

    entity_description: ParkrunBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: ParkrunCoordinator,
        description: ParkrunBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.athlete_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the condition is met."""
        return self.entity_description.value_fn(self.coordinator.data)
