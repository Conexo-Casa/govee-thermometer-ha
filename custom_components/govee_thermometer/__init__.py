"""Govee Thermometer / Hygrometer — Home Assistant integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GoveeApi, GoveeApiError
from .const import CONF_API_KEY, DOMAIN
from .coordinator import GoveeCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api     = GoveeApi(entry.data[CONF_API_KEY], session)

    try:
        devices = await api.async_list_sensors()
    except GoveeApiError as err:
        raise ConfigEntryNotReady(f"Govee API unavailable: {err}") from err

    coordinators: list[GoveeCoordinator] = []
    for dev in devices:
        coord = GoveeCoordinator(
            hass,
            api,
            dev.device_id,
            dev.sku,
            dev.name,
            dev.has_humidity,
        )
        await coord.async_config_entry_first_refresh()
        coordinators.append(coord)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinators
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
