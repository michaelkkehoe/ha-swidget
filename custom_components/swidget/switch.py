"""Support for TPLink HS100/HS110/HS200 smart switch."""
from __future__ import annotations

import logging
from typing import Any, cast

from pyswidget.device import SwidgetDevice, SwidgetOutlet

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import legacy_device_id
from .const import DOMAIN
from .coordinator import SwidgetDataUpdateCoordinator
from .entity import CoordinatedSwidgetEntity, async_refresh_after

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches."""
    coordinator: SwidgetDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    device = cast(SwidgetOutlet, coordinator.device)
    if not device.is_plug and not device.is_strip and not device.is_dimmer:
        return
    entities: list = []
    if device.is_strip:
        # Historically we only add the children if the device is a strip
        _LOGGER.debug("Initializing strip with %s sockets", len(device.children))
        for child in device.children:
            entities.append(SmartPlugSwitch(child, coordinator))
    elif device.is_plug:
        entities.append(SmartPlugSwitch(device, coordinator))

    async_add_entities(entities)


class SwidgetSwitch(CoordinatedSwidgetEntity, SwitchEntity):
    """Representation of a TPLink Smart Plug switch."""

    def __init__(
        self,
        device: SwidgetDevice,
        coordinator: SwidgetDataUpdateCoordinator,
    ) -> None:
        """Initialize the switch."""
        super().__init__(device, coordinator)
        # For backwards compat with pyHS100
        self._attr_unique_id = legacy_device_id(device)

    @async_refresh_after
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.device.turn_on()

    @async_refresh_after
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.device.turn_off()
