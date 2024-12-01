"""SEW API data collector that downloads the observation data."""

import datetime
from datetime import datetime as dt
import logging
import traceback

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
        api_key: str,
        version_string: str = "1.0",
        SEW_site_id: str = "",
        latitude: float = 0,
        longitude: float = 0,
    ) -> None:
        """Init collector."""
        self.location_data: dict = {}
        self.observation_data: dict = {}
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.api_key: str = api_key
        self.version_string: str = version_string
        self.until: str = ""
        self.site_id: str = ""
        self.site_name: str = ""
        self.aqi: float = 0
        self.aqi_24h: float = 0
        self.aqi_pm25: str = ""
        self.aqi_pm25_24h: str
        self.confidence: float = 0
        self.confidence_24h: float = 0
        self.data_source_1h: str = ""
        self.pm25: float = 0
        self.pm25_24h: float = 0
        self.total_sample: float = 0
        self.total_sample_24h: float = 0
        self.last_updated: dt = dt.fromtimestamp(0)
        self.site_found: bool = False
        self.sites_found: bool = False
        self.headers: dict = {
            "Accept": "application/json",
            "User-Agent": "ha-SEW-integration/" + self.version_string,
            "X-API-Key": self.api_key,
        }

        if SEW_site_id != "":
            self.site_id = SEW_site_id
            self.site_found = True

    async def get_location_data(self):
        """Get JSON location name from SEW API endpoint."""
        try:
            if self.location_data is None:
                self.observation_data = {}
                self.site_found = True
        except KeyError:
            _LOGGER.debug(
                "Exception in get_location_data(): %s",
                traceback.format_exc(),
            )
            self.site_found = False

    async def get_locations_list(self):
        """Get JSON location list from SEW API endpoint."""
        self.sites_found = True

    def valid_location(self) -> bool:
        """Return true if a valid location has been found from the latitude and longitude.

        Returns:
            bool: True if a valid SEW location has been found

        """
        return self.site_found

    def valid_location_list(self) -> bool:
        """Return true if a valid location list has been loaded.

        Returns:
            bool: True if a valid SEW location list has been loaded

        """
        return self.sites_found

    def get_location(self) -> str:
        """Return the SEW Site Location GUID.

        Returns:
            str: SEW Site Location GUID

        """
        if self.site_found:
            return self.site_id
        return ""

    def get_location_list(self) -> list:
        """Return the SEW Site Location GUID.

        Returns:
            str: SEW Site Location GUID

        """
        if self.sites_found:
            return self.locations_list
        return []

    def get_aqi(self) -> float:
        """Return the SEW Site aqi.

        Returns:
            float: SEW Site Calculated API

        """
        if self.site_found:
            return self.aqi
        return 0

    def get_aqi_24h(self) -> float:
        """Return the SEW Site aqi_24h.

        Returns:
            float: SEW Site Calculated API 24h Average

        """
        if self.site_found:
            return self.aqi_24h
        return 0

    def get_aqi_pm25(self) -> str:
        """Return the SEW Site aqi_pm25.

        Returns:
            str: SEW Site aqi_pm25

        """
        if self.site_found:
            return self.aqi_pm25
        return ""

    def get_aqi_pm25_24h(self) -> str:
        """Return the SEW Site aqi_pm25_24h.

        Returns:
            str: SEW Site aqi_pm25_24h

        """
        if self.site_found:
            return self.aqi_pm25_24h
        return ""

    def get_confidence(self) -> float:
        """Return the SEW reading confidence.

        Returns:
            float: SEW reading confidence

        """
        if self.site_found:
            return self.confidence
        return 0

    def get_confidence_24h(self) -> float:
        """Return the SEW reading confidence over 24 hours.

        Returns:
            float: SEW reading confidence over 24 hours

        """
        if self.site_found:
            return self.confidence_24h
        return 0

    def get_data_source(self) -> str:
        """Return the SEW Reading Data Source.

        Returns:
            str: SEW Site Reading Data Source for the 1 Hour Reading

        """
        if self.site_found:
            return self.data_source_1h
        return ""

    def get_pm25(self) -> float:
        """Return the SEW Site pm25.

        Returns:
            str: SEW Site pm25

        """
        if self.site_found:
            return self.pm25
        return 0

    def get_pm25_24h(self) -> float:
        """Return the SEW Site pm25_24h.

        Returns:
            str: SEW Site pm25_24h

        """
        if self.site_found:
            return self.pm25_24h
        return 0

    def get_total_sample(self) -> float:
        """Return the SEW reading total samples.

        Returns:
            float: SEW reading total samples

        """
        if self.site_found:
            return self.total_sample
        return 0

    def get_total_sample_24h(self) -> float:
        """Return the SEW reading total samples over 24 hours.

        Returns:
            float: SEW reading total samples over 24 hours

        """
        if self.site_found:
            return self.total_sample_24h
        return 0

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

    async def extract_observation_data(self):
        """Extract Observation Data to individual fields."""
        self.observation_data = {}


    @Throttle(datetime.timedelta(minutes=5))
    async def async_update(self):
        """Refresh the data on the collector object."""
        try:
            if self.location_data is None:
                self.observation_data = {}

        except ConnectionRefusedError as e:
            _LOGGER.error("Connection error in async_update, connection refused: %s", e)
        except Exception:  # noqa: BLE001
            _LOGGER.debug(
                "Exception in async_update(): %s",
                traceback.format_exc(),
            )

    async def async_setup(self):
        """Set up the location list for the collector object."""
        try:
            if self.location_data is None:
                self.observation_data = {}

        except ConnectionRefusedError as e:
            _LOGGER.error("Connection error in async_setup, connection refused: %s", e)
        except Exception:  # noqa: BLE001
            _LOGGER.debug(
                "Exception in async_setup(): %s",
                traceback.format_exc(),
            )
