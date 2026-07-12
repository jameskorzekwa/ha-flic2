"""Flic 2 battery sensor."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricPotential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import Flic2Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the battery voltage sensor."""
    async_add_entities([Flic2BatterySensor(entry)])


class Flic2BatterySensor(Flic2Entity, SensorEntity):
    """Expose the last battery voltage reported by a Flic."""

    _attr_name = "Battery voltage"
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_suggested_display_precision = 2

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_battery_voltage"

    @property
    def native_value(self) -> float | None:
        """Return the latest voltage."""
        return self.device.battery_voltage

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self.device.async_add_state_listener(self.async_write_ha_state)
        )
