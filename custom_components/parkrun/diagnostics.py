"""Diagnostics for parkrun."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data

from .const import CONF_ATHLETE_ID, CONF_COUNTRY

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from . import ParkrunConfigEntry

# Diagnostics get attached to public issues, so strip anything that names or
# identifies the athlete. The entry title is the athlete's full name, the
# unique ID is their athlete ID, and the profile URL embeds the athlete ID.
TO_REDACT = {
    CONF_ATHLETE_ID,
    "avatar_url",
    "first_name",
    "full_name",
    "last_name",
    "profile_url",
    "title",
    "unique_id",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ParkrunConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "country": entry.data.get(CONF_COUNTRY),
        "data": async_redact_data(asdict(coordinator.data), TO_REDACT),
    }
