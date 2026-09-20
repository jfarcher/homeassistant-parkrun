"""Client for public parkrun athlete result pages."""

from __future__ import annotations

import asyncio
from http import HTTPStatus

import aiohttp

from .const import COUNTRY_SITES, DEFAULT_COUNTRY, LOGGER, USER_AGENT
from .models import ParkrunAthleteData
from .parser import (
    ParkrunParseError,
    looks_like_challenge,
    normalize_athlete_id,
    parse_athlete_pages,
)


class ParkrunApiError(Exception):
    """Base parkrun error."""


class ParkrunNotFoundError(ParkrunApiError):
    """Athlete ID was not found."""


class ParkrunConnectionError(ParkrunApiError):
    """Unable to communicate with parkrun."""


class ParkrunApiClient:
    """Fetch statistics from public parkrun athlete pages."""

    def __init__(
        self,
        athlete_id: str,
        country: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the client."""
        self.athlete_id = normalize_athlete_id(athlete_id)
        if country not in COUNTRY_SITES:
            country = DEFAULT_COUNTRY
        self.country = country
        self.base_url = COUNTRY_SITES[country][1]
        self._session = session

    @property
    def profile_url(self) -> str:
        """Public athlete profile URL."""
        return f"{self.base_url}/parkrunner/{self.athlete_id}/"

    async def async_test_profile(self) -> ParkrunAthleteData:
        """Fetch once during config flow."""
        return await self.async_get_athlete_data()

    async def async_get_athlete_data(self) -> ParkrunAthleteData:
        """Return aggregated athlete statistics."""
        profile_html = await self._async_get_text(self.profile_url)
        all_html: str | None = None
        try:
            all_html = await self._async_get_text(f"{self.profile_url}all/")
        except ParkrunNotFoundError:
            LOGGER.debug("No /all/ results page for athlete %s", self.athlete_id)

        try:
            return parse_athlete_pages(
                self.athlete_id,
                profile_html,
                all_html,
                self.profile_url,
            )
        except ParkrunParseError as err:
            raise ParkrunApiError(str(err)) from err

    async def _async_get_text(self, url: str) -> str:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-GB,en;q=0.9",
        }
        try:
            async with asyncio.timeout(30):
                response = await self._session.get(url, headers=headers)
        except TimeoutError as err:
            msg = "Timeout talking to parkrun"
            raise ParkrunConnectionError(msg) from err
        except aiohttp.ClientError as err:
            msg = "Error talking to parkrun"
            raise ParkrunConnectionError(msg) from err

        if response.status == HTTPStatus.NOT_FOUND:
            msg = f"No parkrun athlete found for A{self.athlete_id}"
            raise ParkrunNotFoundError(msg)
        if response.status >= HTTPStatus.BAD_REQUEST:
            msg = f"parkrun returned HTTP {response.status}"
            raise ParkrunApiError(msg)

        html = await response.text()
        if looks_like_challenge(html):
            msg = "parkrun blocked the request with a bot check"
            raise ParkrunConnectionError(msg)
        return html
