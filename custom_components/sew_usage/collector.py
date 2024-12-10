"""SEW API data collector that downloads the observation data."""

import datetime
from datetime import datetime as dt
import logging
import traceback

import aiohttp

from homeassistant.util import Throttle

# from .const import (
#     ATTR_CONFIDENCE,
#     ATTR_CONFIDENCE_24H,
#     ATTR_DATA_SOURCE,
#     ATTR_TOTAL_SAMPLE,
#     ATTR_TOTAL_SAMPLE_24H,
#     AVERAGE_VALUE,
#     CONFIDENCE,
#     COORDINATES,
#     DISTANCE,
#     GEOMETRY,
#     HEALTH_ADVICE,
#     HEALTH_PARAMETER,
#     PARAMETERS,
#     READINGS,
#     RECORDS,
#     SITE_HEALTH_ADVICES,
#     SITE_ID,
#     SITE_NAME,
#     SITE_TYPE,
#     SITE_TYPE_SENSOR,
#     SITE_TYPE_STANDARD,
#     TIME_SERIES_NAME,
#     TIME_SERIES_READINGS,
#     TOTAL_SAMPLE,
#     TYPE_AQI,
#     TYPE_AQI_24H,
#     TYPE_AQI_PM25,
#     TYPE_AQI_PM25_24H,
#     TYPE_PM25,
#     TYPE_PM25_24H,
#     UNTIL,
#     URL_BASE,
#     URL_FIND_SITE,
#     URL_LIST_SITE,
#     URL_PARAMETERS,
# )

_LOGGER = logging.getLogger(__name__)


class Collector:
    """Collector for PySEW."""

    def __init__(
        self,
        mains_water_serial: str,
        sew_username: str,
        sew_password: str,
        browserless: str,
        token: str,
        recycled_water_serial: str = "",
        install_date: dt.date = dt.today,
    ) -> None:
        """Init collector."""
        self.location_data: dict = {}
        self.observation_data: dict = {}
        self.mains_water_serial: str = mains_water_serial
        self.sew_username: str = sew_username
        self.sew_password: str = sew_password
        self.browserless: str = browserless
        self.token: str = token
        self.recycled_water_serial: str = recycled_water_serial
        self.install_date: dt.date = install_date
        self.last_updated: dt = dt.fromtimestamp(0)
        self.site_found: bool = False

        if self.browserless[-1:] != "/":
            self.browserless += "/"

    async def valid_browserless(self) -> bool:
        """Return true if a valid browserless has been found and logged into.

        Returns:
            bool: True if a valid browserless has been found

        """
        return self.site_found

    def get_browserless(self) -> str:
        """Return the browserless URL.

        Returns:
            str:  the browserless URL

        """
        if self.valid_browserless:
            return self.browserless
        return ""

    def get_mains_water_serial(self) -> str:
        """Return the Mains Water Meter Serial Number.

        Returns:
            str: Mains Water Meter Serial Number

        """
        return self.mains_water_serial

    def get_recycled_water_serial(self) -> str | None:
        """Return the Recycled Water Meter Serial Number.

        Returns:
            str: Recycled Water Meter Serial Number

        """
        if self.recycled_water_serial == "":
            return None
        return self.recycled_water_serial

    def get_sew_username(self) -> str:
        """Return the SEW Username.

        Returns:
            str: SEW Username

        """
        return self.sew_username

    def get_sew_password(self) -> str:
        """Return the SEW Password.

        Returns:
            str: SEW Password

        """
        return self.sew_password

    def get_until(self) -> str:
        """Return the SEW Reading Validity.

        Returns:
            str: SEW Site Reading Validity Time

        """
        if self.site_found:
            return self.until
        return 0

    def get_sensor(self, key: str):
        """Return A sensor.

        Returns:
            Any: SEW Site Sensor

        """
        if self.site_found:
            try:
                return self.observation_data.get(key)
            except KeyError:
                return "Sensor %s Not Found!"
        return None

    @Throttle(datetime.timedelta(minutes=5))
    async def async_update(self):
        """Refresh the data on the collector object."""
        try:
            if self.site_found:
                self.observation_data = {}

        except ConnectionRefusedError as e:
            _LOGGER.error("Connection error in async_update, connection refused: %s", e)
        except Exception:  # noqa: BLE001
            _LOGGER.debug(
                "Exception in async_update(): %s",
                traceback.format_exc(),
            )

    async def async_setup(self):
        """Check that browserless is running for the collector object."""
        try:
            if not self.site_found:
                async with aiohttp.ClientSession() as session:
                    url = f"{self.browserless}active?token={self.token}"
                    response = await session.get(url)
                    if response is not None and response.status == 204:
                        self.site_found = True
        except ConnectionRefusedError as e:
            _LOGGER.error("Connection error in async_setup, connection refused: %s", e)
        except Exception:  # noqa: BLE001
            _LOGGER.debug(
                "Exception in async_setup(): %s",
                traceback.format_exc(),
            )
