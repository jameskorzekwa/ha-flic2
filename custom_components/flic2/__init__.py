"""The Flic 2 Bluetooth integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .const import PLATFORMS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .runtime import Flic2Device


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry[Flic2Device]
) -> bool:
    """Set up a paired Flic 2 button."""
    from .runtime import Flic2Device

    device = Flic2Device(hass, entry)
    entry.runtime_data = device
    await device.async_start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ConfigEntry[Flic2Device]
) -> bool:
    """Unload a Flic 2 button."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await entry.runtime_data.async_stop()
    return unload_ok
