"""Async client for the Govee OpenAPI v1."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import aiohttp

from .const import (
    GOVEE_API_DEVICES,
    GOVEE_API_STATE,
    CAP_TEMPERATURE,
    CAP_HUMIDITY,
    CAP_ONLINE,
    GOVEE_SENSOR_SKUS,
    SCALE_THRESHOLD,
    SCALE_DIVISOR,
)

_LOGGER = logging.getLogger(__name__)


# ── Exceptions ──────────────────────────────────────────────────────────────

class GoveeAuthError(Exception):
    """Invalid or expired API key."""

class GoveeApiError(Exception):
    """Any other API-level error."""


# ── Data classes ────────────────────────────────────────────────────────────

@dataclass
class GoveeDevice:
    device_id: str        # MAC-style identifier, e.g. "AB:CD:EF:01:23:45:67:89"
    sku: str
    name: str
    has_humidity: bool


@dataclass
class GoveeReading:
    online: bool            = False
    temperature: float | None = None   # °C
    humidity:    float | None = None   # %RH


# ── API client ──────────────────────────────────────────────────────────────

class GoveeApi:
    """Wraps Govee's OpenAPI /router/api/v1 endpoints."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        self._key     = api_key
        self._session = session

    # ── helpers ─────────────────────────────────────────────────────────

    @property
    def _headers(self) -> dict[str, str]:
        return {"Govee-API-Key": self._key, "Content-Type": "application/json"}

    async def _get(self, url: str) -> dict:
        async with self._session.get(url, headers=self._headers) as r:
            if r.status == 401:
                raise GoveeAuthError("Invalid Govee API key")
            if r.status != 200:
                raise GoveeApiError(f"HTTP {r.status}: {await r.text()}")
            data = await r.json()
            if data.get("code", 200) != 200:
                raise GoveeApiError(f"API error {data.get('code')}: {data.get('msg')}")
            return data

    async def _post(self, url: str, body: dict) -> dict:
        async with self._session.post(url, json=body, headers=self._headers) as r:
            if r.status == 401:
                raise GoveeAuthError("Invalid Govee API key")
            if r.status != 200:
                raise GoveeApiError(f"HTTP {r.status}: {await r.text()}")
            data = await r.json()
            if data.get("code", 200) != 200:
                raise GoveeApiError(f"API error {data.get('code')}: {data.get('msg')}")
            return data

    # ── public API ───────────────────────────────────────────────────────

    async def async_validate_key(self) -> None:
        """Raise GoveeAuthError if the key is invalid."""
        await self._get(GOVEE_API_DEVICES)

    async def async_list_sensors(self) -> list[GoveeDevice]:
        """Return all thermometer/hygrometer devices for this API key."""
        data = await self._get(GOVEE_API_DEVICES)
        devices: list[GoveeDevice] = []
        for dev in data.get("data", []):
            sku = dev.get("sku", "")
            if sku not in GOVEE_SENSOR_SKUS:
                continue
            info = GOVEE_SENSOR_SKUS[sku]
            devices.append(GoveeDevice(
                device_id    = dev["device"],
                sku          = sku,
                name         = dev.get("deviceName") or info["label"],
                has_humidity = info["has_humidity"],
            ))
        return devices

    async def async_get_reading(self, device_id: str, sku: str) -> GoveeReading:
        """Fetch the latest sensor reading for one device."""
        body = {
            "requestId": f"ha-{device_id[-8:].replace(':', '')}",
            "payload":   {"sku": sku, "device": device_id},
        }
        data = await self._post(GOVEE_API_STATE, body)
        caps: list[dict] = data.get("payload", {}).get("capabilities", [])

        reading = GoveeReading()
        for cap in caps:
            instance = cap.get("instance", "")
            value    = cap.get("state", {}).get("value")

            if instance == CAP_ONLINE:
                reading.online = bool(value)
            elif instance == CAP_TEMPERATURE and value is not None:
                reading.temperature = _normalise(float(value))
            elif instance == CAP_HUMIDITY and value is not None:
                reading.humidity = _normalise(float(value))

        return reading


def _normalise(value: float) -> float:
    """Divide by 100 if Govee returned the value scaled (e.g. 2560 → 25.60)."""
    if value > SCALE_THRESHOLD:
        return round(value / SCALE_DIVISOR, 2)
    return round(value, 2)
