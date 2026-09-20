"""Shared parkrun entity helpers."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import ParkrunCoordinator


class ParkrunEntity(CoordinatorEntity[ParkrunCoordinator]):
    """Base entity for a parkrun athlete."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: ParkrunCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        athlete_id = coordinator.data.athlete_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, athlete_id)},
            manufacturer="parkrun",
            model="Athlete",
            name=coordinator.data.full_name,
            configuration_url=coordinator.data.profile_url,
        )
