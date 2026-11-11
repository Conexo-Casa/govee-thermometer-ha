"""DataUpdateCoordinator — one per Govee sensor device."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GoveeApi, GoveeApiError, GoveeAuthError, GoveeReading
from .const import DOMAIN, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class GoveeCoordinator(DataUpdateCoordinator[GoveeReading]):
    """Polls one Govee thermometer/hygrometer once per minute."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: GoveeApi,
        device_id: str,
        sku: str,
        device_name: str,
        has_humidity: bool,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_id}",
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.api          = api
        self.device_id    = device_id
        self.sku          = sku
        self.device_name  = device_name
        self.has_humidity = has_humidity

    async def _async_update_data(self) -> GoveeReading:
        try:
            return await self.api.async_get_reading(self.device_id, self.sku)
        except GoveeAuthError as err:
            raise UpdateFailed(f"Govee auth error: {err}") from err
        except GoveeApiError as err:
            raise UpdateFailed(f"Govee API error: {err}") from err
