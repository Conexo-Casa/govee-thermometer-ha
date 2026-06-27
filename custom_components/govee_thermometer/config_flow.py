"""Config flow for Govee Thermometer integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GoveeApi, GoveeAuthError, GoveeApiError
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_TEMP_UNIT,
    TEMP_UNIT_CELSIUS,
    TEMP_UNIT_FAHRENHEIT,
)

_LOGGER = logging.getLogger(__name__)

STEP_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})


class GoveeThermometerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Single-step config flow: enter Govee API key."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            session = async_get_clientsession(self.hass)
            api     = GoveeApi(api_key, session)
            try:
                await api.async_validate_key()
            except GoveeAuthError:
                errors["base"] = "invalid_api_key"
            except (GoveeApiError, aiohttp.ClientError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"govee_{api_key[-8:]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Govee Thermometer / Hygrometer",
                    data={CONF_API_KEY: api_key},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_SCHEMA,
            errors=errors,
            description_placeholders={
                "api_docs": "https://developer.govee.com/docs/getting-started"
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> GoveeThermometerOptionsFlow:
        return GoveeThermometerOptionsFlow(config_entry)


class GoveeThermometerOptionsFlow(config_entries.OptionsFlow):
    """Options flow to configure temperature unit."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_unit = self.config_entry.options.get(
            CONF_TEMP_UNIT, TEMP_UNIT_CELSIUS
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TEMP_UNIT, default=current_unit): vol.In(
                        {
                            TEMP_UNIT_CELSIUS: "Celsius (°C)",
                            TEMP_UNIT_FAHRENHEIT: "Fahrenheit (°F)",
                        }
                    ),
                }
            ),
        )
