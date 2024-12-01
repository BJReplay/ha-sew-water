"""Constants for the SEW Water integration."""

from __future__ import annotations

from typing import Final

# Integration constants
ATTR_ENTRY_TYPE: Final = "entry_type"
ATTRIBUTION: Final = "Data retrieved from South East Water"
COLLECTOR: Final = "collector"
DOMAIN = "SEW_water_usage"
ENTRY_TYPE_SERVICE: Final = "service"
COORDINATOR: Final = "coordinator"
UPDATE_LISTENER: Final = "update_listener"
TIME_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT_UTC = "%Y-%m-%d %H:%M:%S UTC"
INIT_MSG = """This is a custom integration. When troubleshooting a problem, after
reviewing open and closed issues, and the discussions.

Beta versions may also have addressed issues so look at those.

If all else fails, then open an issue and our community will try to
help: https://github.com/BJReplay/ha-sew-water/issues"""
MANUFACTURER = "BJReplay"
TITLE = "SEW Water Usage"
SENSOR_MAINS = "water_usage_mains"
SENSOR_MAINS_UNIQUEID = "current_water_mains_usage"
SENSOR_RECYCLED = "water_usage_recycled"
SENSOR_RECYCLED_UNIQUEID = "current_water_recycled_usage"
SCAN_INTERVAL = 24
MAINS_WATER_SERIAL = "mains_water_serial"
RECYCLED_WATER_SERIAL = "recycled_water_serial"
SEW_USERNAME = "sew_username"
SEW_PASSWORD = "sew_password"
BROWSERLESS = "browserless"
TOKEN = "token"
INSTALL_DATE = "install_date"
