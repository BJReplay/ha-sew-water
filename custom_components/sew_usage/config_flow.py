"""Config flow for SEW Water integration."""

from __future__ import annotations

from datetime import date
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector

from .collector import Collector
from .const import (
    BROWSERLESS,
    DOMAIN,
    INSTALL_DATE,
    MAINS_WATER_SERIAL,
    RECYCLED_WATER_SERIAL,
    TITLE,
    TOKEN,
)
from .coordinator import SEWDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class SEWConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle the config flow."""

    def __init__(self) -> None:
        """Initialise the config flow."""
        self.data = {}
        self.collector: Collector = None

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def _create_entry(
        self,
        mains_water_serial: str,
        sew_username: str,
        sew_password: str,
        browserless: str,
        token: str,
        install_date: date | None,
        recycled_water_serial: str | None,
    ) -> FlowResult:
        """Register new entry."""
        return self.async_create_entry(
            title=f"Water Readings for {mains_water_serial}",
            data={
                MAINS_WATER_SERIAL: mains_water_serial,
                CONF_USERNAME: sew_username,
                CONF_PASSWORD: sew_password,
                BROWSERLESS: browserless,
                TOKEN: token,
                INSTALL_DATE: install_date,
                RECYCLED_WATER_SERIAL: recycled_water_serial,
            },
        )

    async def _create_device(
        self,
        mains_water_serial: str,
        sew_username: str,
        sew_password: str,
        browserless: str,
        token: str,
        install_date: date | None,
        recycled_water_serial: str | None,
    ) -> FlowResult:
        """Create device."""

        self.collector = Collector(
            mains_water_serial=mains_water_serial,
            sew_username=sew_username,
            sew_password=sew_password,
            browserless=browserless,
            token=token,
            recycled_water_serial=recycled_water_serial,
            install_date=install_date,
        )

        try:
            device = SEWDataUpdateCoordinator(
                hass=self.hass,
                collector=Collector,
            )
            await device.async_init()

            # check that we found cars
            # if not len(device.get_version()):
            #     return self.async_abort(reason="No cars found")

            # # check if we have a token, otherwise throw exception
            # if device.polestar_api.auth.access_token is None:
            #     _LOGGER.exception(
            #         "No token, Could be wrong credentials (invalid email or password))"
            #     )
            #     return self.async_abort(reason="No API token")

        except TimeoutError:
            return self.async_abort(reason="API timeout")
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected error creating device")
            return self.async_abort(reason="API unexpected failure")

        return await self._create_entry(
            mains_water_serial,
            sew_username,
            sew_password,
            browserless,
            token,
            install_date,
            recycled_water_serial,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> SEWOptionFlowHandler:
        """Get the options flow for this handler.

        Arguments:
            config_entry (ConfigEntry): The integration entry instance, contains the configuration.

        Returns:
            SEWOptionFlowHandler: The config flow handler instance.

        """
        return SEWOptionFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user.

        Arguments:
            user_input: dict[str, Any] | None = None: The config submitted by a user. Defaults to None.

        Returns:
            FlowResult: The form to show.

        """
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(MAINS_WATER_SERIAL, default=""): str,
                        vol.Required(CONF_USERNAME, default=""): str,
                        vol.Required(CONF_PASSWORD, default=""): str,
                        vol.Required(BROWSERLESS, default=""): str,
                        vol.Required(TOKEN, default=""): str,
                        vol.Optional(INSTALL_DATE, default=date.today): selector(
                            {"text": {"type": "date"}}
                        ),
                        vol.Optional(RECYCLED_WATER_SERIAL, default=""): str,
                    }
                ),
            )
        return await self._create_device(
            mains_water_serial=user_input[MAINS_WATER_SERIAL],
            sew_username=user_input[CONF_USERNAME],
            sew_password=user_input[CONF_PASSWORD],
            browserless=user_input[BROWSERLESS],
            token=user_input[TOKEN],
            install_date=user_input[INSTALL_DATE],
            recycled_water_serial=user_input[RECYCLED_WATER_SERIAL],
        )

    async def async_step_import(self, user_input: dict) -> FlowResult:
        """Import a config entry."""
        return await self._create_device(
            mains_water_serial=user_input[MAINS_WATER_SERIAL],
            sew_username=user_input[CONF_USERNAME],
            sew_password=user_input[CONF_PASSWORD],
            browserless=user_input[BROWSERLESS],
            token=user_input[TOKEN],
            install_date=user_input[INSTALL_DATE],
            recycled_water_serial=user_input[RECYCLED_WATER_SERIAL],
        )


class SEWOptionFlowHandler(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._entry: ConfigEntry = config_entry
        self._options = dict(config_entry.options)

    async def async_step_init(self, user_input: dict | None = None) -> Any:
        """Initialise main dialogue step.

        Arguments:
            user_input (dict, optional): The input provided by the user. Defaults to None.

        Returns:
            Any: Either an error, or the configuration dialogue results.

        """

        errors = {}
        mains_water_serial = self._options.get(MAINS_WATER_SERIAL)
        recycled_water_serial = self._options.get(RECYCLED_WATER_SERIAL)
        sew_username = self._options.get(CONF_USERNAME)
        sew_password = self._options.get(CONF_PASSWORD)
        browserless = self._options.get(BROWSERLESS)
        token = self._options.get(TOKEN)
        install_date = self._options.get(INSTALL_DATE)
        collector: Collector = Collector(
            mains_water_serial=mains_water_serial,
            sew_username=sew_username,
            sew_password=sew_password,
            browserless=browserless,
            token=token,
        )
        await collector.async_setup()
        if not collector.site_found:
            _LOGGER.debug("Unable to retrieve location list from SEW")
            errors["base"] = "bad_api"

        if user_input is not None:
            all_config_data = {**self._options}

            browserless = user_input[BROWSERLESS].replace(" ", "")
            all_config_data[BROWSERLESS] = browserless

            mains_water_serial = user_input[MAINS_WATER_SERIAL].replace(" ", "")
            all_config_data[MAINS_WATER_SERIAL] = mains_water_serial

            recycled_water_serial = user_input[RECYCLED_WATER_SERIAL].replace(" ", "")
            all_config_data[RECYCLED_WATER_SERIAL] = recycled_water_serial

            token = user_input[TOKEN]
            all_config_data[TOKEN] = token

            sew_password = user_input[CONF_PASSWORD]
            all_config_data[CONF_PASSWORD] = sew_password

            sew_username = user_input[CONF_USERNAME]
            all_config_data[CONF_USERNAME] = sew_username

            install_date = user_input[INSTALL_DATE]
            all_config_data[INSTALL_DATE] = install_date

            token = user_input[TOKEN]
            all_config_data[TOKEN] = token

            self.data = user_input

            self.hass.config_entries.async_update_entry(
                self._entry,
                title=TITLE,
                options=all_config_data,
            )
            await collector.async_update()

            return self.async_create_entry(title=TITLE, data=None)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(MAINS_WATER_SERIAL, default=""): str,
                    vol.Required(CONF_USERNAME, default=""): str,
                    vol.Required(CONF_PASSWORD, default=""): str,
                    vol.Required(BROWSERLESS, default=""): str,
                    vol.Required(TOKEN, default=""): str,
                    vol.Optional(INSTALL_DATE, default=date.today): selector(
                        {"text": {"type": "date"}}
                    ),
                    vol.Optional(RECYCLED_WATER_SERIAL, default=""): str,
                }
            ),
            errors=errors,
        )
