"""Constants for the parkrun integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "parkrun"
ATTRIBUTION = "Data provided by parkrun"

CONF_ATHLETE_ID = "athlete_id"
CONF_COUNTRY = "country"

DEFAULT_COUNTRY = "uk"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

DEFAULT_SCAN_INTERVAL_HOURS = 6

ADULT_MILESTONES = (25, 50, 100, 250, 500, 1000)
JUNIOR_MILESTONES = (10, 25, 50, 100, 250, 500)
VOLUNTEER_MILESTONES = (5, 10, 25, 50, 100, 250, 500)

# Athlete result pages live on the country websites, not api.parkrun.com.
COUNTRY_SITES: dict[str, tuple[str, str]] = {
    "uk": ("United Kingdom", "https://www.parkrun.org.uk"),
    "australia": ("Australia", "https://www.parkrun.com.au"),
    "austria": ("Austria", "https://www.parkrun.co.at"),
    "canada": ("Canada", "https://www.parkrun.ca"),
    "denmark": ("Denmark", "https://www.parkrun.dk"),
    "finland": ("Finland", "https://www.parkrun.fi"),
    "france": ("France", "https://www.parkrun.fr"),
    "germany": ("Germany", "https://www.parkrun.com.de"),
    "ireland": ("Ireland", "https://www.parkrun.ie"),
    "italy": ("Italy", "https://www.parkrun.it"),
    "japan": ("Japan", "https://www.parkrun.jp"),
    "malaysia": ("Malaysia", "https://www.parkrun.my"),
    "netherlands": ("Netherlands", "https://www.parkrun.co.nl"),
    "new_zealand": ("New Zealand", "https://www.parkrun.co.nz"),
    "norway": ("Norway", "https://www.parkrun.no"),
    "poland": ("Poland", "https://www.parkrun.pl"),
    "singapore": ("Singapore", "https://www.parkrun.sg"),
    "south_africa": ("South Africa", "https://www.parkrun.co.za"),
    "sweden": ("Sweden", "https://www.parkrun.se"),
    "usa": ("United States", "https://www.parkrun.us"),
}
