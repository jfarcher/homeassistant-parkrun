"""Diagnostics for parkrun."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data

from .const import CONF_ATHLETE_ID, CONF_COUNTRY

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from . import ParkrunConfigEntry

TO_REDACT = {"avatar_url"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ParkrunConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "athlete_id": entry.data.get(CONF_ATHLETE_ID),
        "country": entry.data.get(CONF_COUNTRY),
        "data": async_redact_data(asdict(coordinator.data), TO_REDACT),
    }
