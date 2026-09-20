"""Sensor platform for parkrun."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTime

from .entity import ParkrunEntity
from .models import ParkrunAthleteData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType

    from . import ParkrunConfigEntry
    from .coordinator import ParkrunCoordinator


@dataclass(frozen=True, kw_only=True)
class ParkrunSensorEntityDescription(SensorEntityDescription):
    """Describes a parkrun sensor."""

    value_fn: Callable[[ParkrunAthleteData], StateType | date]


SENSOR_DESCRIPTIONS: tuple[ParkrunSensorEntityDescription, ...] = (
    ParkrunSensorEntityDescription(
        key="total_runs",
        translation_key="total_runs",
        icon="mdi:run",
        native_unit_of_measurement="parkruns",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.total_runs,
    ),
    ParkrunSensorEntityDescription(
        key="junior_runs",
        translation_key="junior_runs",
        icon="mdi:human-child",
        native_unit_of_measurement="parkruns",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.junior_runs,
    ),
    ParkrunSensorEntityDescription(
        key="volunteer_count",
        translation_key="volunteer_count",
        icon="mdi:account-heart",
        native_unit_of_measurement="credits",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.volunteer_count,
    ),
    ParkrunSensorEntityDescription(
        key="events_attended",
        translation_key="events_attended",
        icon="mdi:map-marker-multiple",
        native_unit_of_measurement="events",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.events_attended,
    ),
    ParkrunSensorEntityDescription(
        key="personal_best",
        translation_key="personal_best",
        icon="mdi:trophy",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: data.personal_best_seconds,
    ),
    ParkrunSensorEntityDescription(
        key="best_age_grade",
        translation_key="best_age_grade",
        icon="mdi:percent",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.best_age_grade,
    ),
    ParkrunSensorEntityDescription(
        key="latest_event",
        translation_key="latest_event",
        icon="mdi:map-marker",
        value_fn=lambda data: data.latest_event_name,
    ),
    ParkrunSensorEntityDescription(
        key="latest_event_date",
        translation_key="latest_event_date",
        icon="mdi:calendar",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: data.latest_event_date,
    ),
    ParkrunSensorEntityDescription(
        key="latest_time",
        translation_key="latest_time",
        icon="mdi:timer",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: data.latest_time_seconds,
    ),
    ParkrunSensorEntityDescription(
        key="latest_position",
        translation_key="latest_position",
        icon="mdi:order-numeric-ascending",
        value_fn=lambda data: data.latest_position,
    ),
    ParkrunSensorEntityDescription(
        key="latest_gender_position",
        translation_key="latest_gender_position",
        icon="mdi:account-group",
        value_fn=lambda data: data.latest_gender_position,
    ),
    ParkrunSensorEntityDescription(
        key="latest_age_grade",
        translation_key="latest_age_grade",
        icon="mdi:percent-outline",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.latest_age_grade,
    ),
    ParkrunSensorEntityDescription(
        key="latest_age_category",
        translation_key="latest_age_category",
        icon="mdi:card-account-details",
        value_fn=lambda data: data.latest_age_category,
    ),
    ParkrunSensorEntityDescription(
        key="first_event",
        translation_key="first_event",
        icon="mdi:map-marker-outline",
        value_fn=lambda data: data.first_event_name,
    ),
    ParkrunSensorEntityDescription(
        key="first_event_date",
        translation_key="first_event_date",
        icon="mdi:calendar-start",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: data.first_event_date,
    ),
    ParkrunSensorEntityDescription(
        key="run_club",
        translation_key="run_club",
        icon="mdi:tshirt-crew",
        value_fn=lambda data: data.run_club,
    ),
    ParkrunSensorEntityDescription(
        key="next_run_milestone",
        translation_key="next_run_milestone",
        icon="mdi:flag-checkered",
        value_fn=lambda data: data.next_run_milestone,
    ),
    ParkrunSensorEntityDescription(
        key="runs_to_next_milestone",
        translation_key="runs_to_next_milestone",
        icon="mdi:counter",
        value_fn=lambda data: data.runs_to_next_milestone,
    ),
    ParkrunSensorEntityDescription(
        key="volunteer_club",
        translation_key="volunteer_club",
        icon="mdi:tshirt-crew-outline",
        value_fn=lambda data: data.volunteer_club,
    ),
    ParkrunSensorEntityDescription(
        key="next_volunteer_milestone",
        translation_key="next_volunteer_milestone",
        icon="mdi:flag-outline",
        value_fn=lambda data: data.next_volunteer_milestone,
    ),
    ParkrunSensorEntityDescription(
        key="volunteer_to_next_milestone",
        translation_key="volunteer_to_next_milestone",
        icon="mdi:counter",
        value_fn=lambda data: data.volunteer_to_next_milestone,
    ),
    ParkrunSensorEntityDescription(
        key="home_run",
        translation_key="home_run",
        icon="mdi:home",
        value_fn=lambda data: data.home_run_name,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ParkrunConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up parkrun sensors from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        ParkrunSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class ParkrunSensor(ParkrunEntity, SensorEntity):
    """A parkrun statistic sensor."""

    entity_description: ParkrunSensorEntityDescription

    def __init__(
        self,
        coordinator: ParkrunCoordinator,
        description: ParkrunSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.athlete_id}_{description.key}"

    @property
    def native_value(self) -> StateType | date:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
