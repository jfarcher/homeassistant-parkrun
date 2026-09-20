"""Config flow for parkrun."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    ParkrunApiClient,
    ParkrunApiError,
    ParkrunConnectionError,
    ParkrunNotFoundError,
)
from .const import (
    CONF_ATHLETE_ID,
    CONF_COUNTRY,
    COUNTRY_SITES,
    DEFAULT_COUNTRY,
    DOMAIN,
    LOGGER,
)
from .models import ParkrunAthleteData
from .parser import normalize_athlete_id

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ATHLETE_ID): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        ),
        vol.Required(CONF_COUNTRY, default=DEFAULT_COUNTRY): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    selector.SelectOptionDict(value=key, label=label)
                    for key, (label, _url) in COUNTRY_SITES.items()
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
    }
)


class ParkrunConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for parkrun."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                athlete_id = normalize_athlete_id(user_input[CONF_ATHLETE_ID])
                data = await self._async_validate(
                    athlete_id, user_input[CONF_COUNTRY]
                )
            except ValueError:
                errors[CONF_ATHLETE_ID] = "invalid_athlete_id"
            except ParkrunNotFoundError:
                errors["base"] = "not_found"
            except ParkrunConnectionError:
                errors["base"] = "cannot_connect"
            except ParkrunApiError:
                LOGGER.exception("Unexpected parkrun error during setup")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(data.athlete_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=data.full_name,
                    data={
                        CONF_ATHLETE_ID: data.athlete_id,
                        CONF_COUNTRY: user_input[CONF_COUNTRY],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_DATA_SCHEMA, user_input
            ),
            errors=errors,
        )

    async def _async_validate(
        self, athlete_id: str, country: str
    ) -> ParkrunAthleteData:
        """Confirm the athlete page exists and is parseable."""
        client = ParkrunApiClient(
            athlete_id=athlete_id,
            country=country,
            session=async_get_clientsession(self.hass),
        )
        return await client.async_test_profile()
