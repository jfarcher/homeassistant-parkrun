"""DataUpdateCoordinator for parkrun."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ParkrunApiError, ParkrunConnectionError, ParkrunNotFoundError
from .const import DEFAULT_SCAN_INTERVAL_HOURS, DOMAIN, LOGGER
from .models import ParkrunAthleteData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .api import ParkrunApiClient


class ParkrunCoordinator(DataUpdateCoordinator[ParkrunAthleteData]):
    """Fetch parkrun athlete statistics."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: ParkrunApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=timedelta(hours=DEFAULT_SCAN_INTERVAL_HOURS),
            always_update=False,
        )
        self.client = client

    async def _async_update_data(self) -> ParkrunAthleteData:
        """Fetch data from parkrun."""
        try:
            return await self.client.async_get_athlete_data()
        except (
            ParkrunConnectionError,
            ParkrunNotFoundError,
            ParkrunApiError,
        ) as err:
            raise UpdateFailed(err) from err
