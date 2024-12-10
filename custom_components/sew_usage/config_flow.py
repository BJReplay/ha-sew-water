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

        errors = {}

        if user_input is not None:
            try:
                device = SEWDataUpdateCoordinator(
                    hass=self.hass,
                    collector=Collector,
                )
                await device.async_init()

                # Create the collector object with the given parameters
                self.collector = Collector(
                    mains_water_serial=user_input[MAINS_WATER_SERIAL],
                    sew_username=user_input[CONF_USERNAME],
                    sew_password=user_input[CONF_PASSWORD],
                    browserless=user_input[BROWSERLESS],
                    token=user_input[TOKEN],
                    recycled_water_serial=user_input[RECYCLED_WATER_SERIAL],
                    install_date=user_input[INSTALL_DATE],
                )

                # Save the user input into self.data so it's retained
                self.data = user_input

                # Check if location is valid
                await self.collector.async_setup()
                if not self.collector.valid_browserless():
                    _LOGGER.debug("Unable to retrieve location list from EPA")
                    errors["base"] = "bad_api"

                options = {
                    MAINS_WATER_SERIAL: user_input[MAINS_WATER_SERIAL],
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    BROWSERLESS: user_input[BROWSERLESS],
                    TOKEN: user_input[TOKEN],
                    INSTALL_DATE: user_input[INSTALL_DATE],
                    RECYCLED_WATER_SERIAL: user_input[RECYCLED_WATER_SERIAL],
                }

            except TimeoutError:
                return self.async_abort(reason="API timeout")

            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            return self.async_create_entry(
                title=TITLE,
                data={},
                options=options,
            )

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
            errors=errors,
            description_placeholders={
                MAINS_WATER_SERIAL: "Enter your Meter Serial Number provided by South East Water.",
            },
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
                    vol.Required(
                        MAINS_WATER_SERIAL,
                        default=self._options.get(MAINS_WATER_SERIAL, vol.UNDEFINED),
                    ): str,
                    vol.Required(
                        CONF_USERNAME,
                        default=self._options.get(CONF_USERNAME, vol.UNDEFINED),
                    ): str,
                    vol.Required(
                        CONF_PASSWORD,
                        default=self._options.get(CONF_PASSWORD, vol.UNDEFINED),
                    ): str,
                    vol.Required(
                        BROWSERLESS,
                        default=self._options.get(BROWSERLESS, vol.UNDEFINED),
                    ): str,
                    vol.Required(
                        TOKEN, default=self._options.get(TOKEN, vol.UNDEFINED)
                    ): str,
                    vol.Optional(
                        INSTALL_DATE,
                        default=self._options.get(INSTALL_DATE, date.today),
                    ): selector({"text": {"type": "date"}}),
                    vol.Optional(
                        RECYCLED_WATER_SERIAL,
                        default=self._options.get(RECYCLED_WATER_SERIAL, vol.UNDEFINED),
                    ): str,
                }
            ),
            errors=errors,
        )
