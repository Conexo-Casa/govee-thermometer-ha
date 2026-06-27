"""Sensor platform for Govee thermometers and hygrometers."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_TEMP_UNIT, TEMP_UNIT_FAHRENHEIT
from .coordinator import GoveeCoordinator
from .api import GoveeReading


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: list[GoveeCoordinator] = hass.data[DOMAIN][entry.entry_id]
    temp_unit = (
        UnitOfTemperature.FAHRENHEIT
        if entry.options.get(CONF_TEMP_UNIT) == TEMP_UNIT_FAHRENHEIT
        else UnitOfTemperature.CELSIUS
    )
    entities: list[SensorEntity] = []
    for coord in coordinators:
        entities.append(GoveeTempSensor(coord, temp_unit))
        if coord.has_humidity:
            entities.append(GoveeHumiditySensor(coord))
        entities.append(GoveeOnlineSensor(coord))
    async_add_entities(entities)


# ── shared base ─────────────────────────────────────────────────────────────

class _GoveeBase(CoordinatorEntity[GoveeCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: GoveeCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)},
            name=coordinator.device_name,
            manufacturer="Govee",
            model=coordinator.sku,
        )

    @property
    def _reading(self) -> GoveeReading | None:
        return self.coordinator.data


# ── Temperature ─────────────────────────────────────────────────────────────

class GoveeTempSensor(_GoveeBase):
    _attr_device_class                 = SensorDeviceClass.TEMPERATURE
    _attr_state_class                  = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision  = 1

    def __init__(self, coordinator: GoveeCoordinator, unit: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_temperature"
        self._attr_name      = "Temperature"
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> float | None:
        r = self._reading
        return r.temperature if r else None

    @property
    def available(self) -> bool:
        r = self._reading
        return r is not None and r.online


# ── Humidity ────────────────────────────────────────────────────────────────

class GoveeHumiditySensor(_GoveeBase):
    _attr_device_class                 = SensorDeviceClass.HUMIDITY
    _attr_state_class                  = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement   = PERCENTAGE
    _attr_suggested_display_precision  = 1

    def __init__(self, coordinator: GoveeCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_humidity"
        self._attr_name      = "Humidity"

    @property
    def native_value(self) -> float | None:
        r = self._reading
        return r.humidity if r else None

    @property
    def available(self) -> bool:
        r = self._reading
        return r is not None and r.online


# ── Online / connectivity ────────────────────────────────────────────────────

class GoveeOnlineSensor(_GoveeBase):
    _attr_entity_registry_enabled_default = False   # opt-in only
    _attr_icon = "mdi:cloud-check"

    def __init__(self, coordinator: GoveeCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_online"
        self._attr_name      = "Connection"

    @property
    def native_value(self) -> str:
        r = self._reading
        if r is None:
            return "unknown"
        return "online" if r.online else "offline"
