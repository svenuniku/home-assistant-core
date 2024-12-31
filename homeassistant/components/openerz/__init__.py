"""The Open ERZ API integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, UPDATE_LISTENER

# List of platforms to support. There should be a matching .py file for each.
PLATFORMS = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Open ERZ from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    _LOGGER.warning(f"Entry: {entry}")
    hass_data = dict(entry.data)
    # Registers update listener to update config entry when options are updated.
    update_listener = entry.add_update_listener(async_update_options)
    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    hass_data[UPDATE_LISTENER] = update_listener

    hass.data[DOMAIN][entry.entry_id] = hass_data

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options from user interface."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok
