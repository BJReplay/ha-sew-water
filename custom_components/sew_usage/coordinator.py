"""Support for South East Water Usage, initialisation."""

import logging

from aiohttp.client_exceptions import ClientConnectorError

from homeassistant import loader
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.loader import async_get_loaded_integration

from .collector import Collector
from .const import (
    BROWSERLESS,
    DOMAIN,
    INSTALL_DATE,
    MAINS_WATER_SERIAL,
    RECYCLED_WATER_SERIAL,
    TOKEN,
)
from .coordinator import SEWDataUpdateCoordinator
from .data import SEWConfigEntry, SEWData

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_migrate_entry(hass: HomeAssistant, entry: SEWConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", entry.version)

    if entry.version == 0:
        new = {**entry.data}
        if MAINS_WATER_SERIAL in new:
            new[MAINS_WATER_SERIAL] = entry.data[MAINS_WATER_SERIAL]

        entry.version = 1
        hass.config_entries.async_update_entry(entry, data=new)

    _LOGGER.info("Migration to version %s successful", entry.version)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SEWConfigEntry) -> bool:
    """Set up the integration.

    * Get and sanitise options.
    * Instantiate the main class.
    * Instantiate the coordinator.

    Arguments:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The integration entry instance, contains the configuration.

    Raises:
        ConfigEntryNotReady: Instructs Home Assistant that the integration is not yet ready when a load failure occurs.

    Returns:
        bool: Whether setup has completed successfully.

    """

    # version = await get_version(hass)

    options = entry.options
    mains_water_serial = options.get(MAINS_WATER_SERIAL)
    recycled_water_serial = options.get(RECYCLED_WATER_SERIAL)
    sew_username = options.get(CONF_USERNAME)
    sew_password = options.get(CONF_PASSWORD)
    browserless = options.get(BROWSERLESS)
    token = options.get(TOKEN)
    install_date = options.get(INSTALL_DATE)
    collector: Collector = Collector(
        mains_water_serial=mains_water_serial,
        sew_username=sew_username,
        sew_password=sew_password,
        browserless=browserless,
        token=token,
        recycled_water_serial=recycled_water_serial,
        install_date=install_date,
    )
    coordinator: SEWDataUpdateCoordinator = SEWDataUpdateCoordinator(
        hass=hass, collector=collector
    )

    entry.runtime_data = SEWData(
        coordinator=coordinator,
        integration=async_get_loaded_integration(hass, entry.domain),
        other_data=entry,
    )

    _LOGGER.debug("Successful init")

    opt = {**entry.options}
    hass.config_entries.async_update_entry(entry, options=opt)

    try:
        await collector.async_update()
    except ClientConnectorError as ex:
        raise ConfigEntryNotReady from ex
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def get_version(hass: HomeAssistant) -> str:
    """Get trimmed version string for use in User Agent String.

    Args:
        hass (HomeAssistant): hass Reference

    Returns:
        str: Trimmed Version String

    """
    try:
        version = ""
        integration = await loader.async_get_integration(hass, DOMAIN)
        version = str(integration.version)
    except loader.IntegrationNotFound:
        pass

    return version


def get_ua_version(version: str) -> str:
    """Get trimmed version string for use in User Agent String.

    Args:
        version (str): version string

    Returns:
        str: Trimmed Version String

    """

    raw_version = version.replace("v", "")

    return raw_version[: raw_version.rfind(".")]


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Handle config entry updates."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    This also removes the services available.

    Arguments:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The integration entry instance, contains the configuration.

    Returns:
        bool: Whether the unload completed successfully.

    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: ConfigEntry, device
) -> bool:
    """Remove a device.

    Arguments:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): Not used.
        device: The device instance.

    Returns:
        bool: Whether the removal completed successfully.

    """
    dr(hass).async_remove_device(device.id)
    return True
