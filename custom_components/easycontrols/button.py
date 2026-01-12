"""The button module for Helios Easy Controls integration."""

import logging
from typing import Self

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.easycontrols import get_coordinator
from custom_components.easycontrols.const import VARIABLE_RESET_FLAG
from custom_components.easycontrols.coordinator import EasyControlsDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class EasyControlsButton(ButtonEntity):
    """Represents a button to trigger actions on the Helios device."""

    def __init__(
        self: Self,
        coordinator: EasyControlsDataUpdateCoordinator,
        description: ButtonEntityDescription,
    ):
        """
        Initialize a new instance of `EasyControlsButton` class.

        Args:
            coordinator:
                The coordinator instance.
            description:
                The button entity description.

        """
        self.entity_description = description
        self._coordinator = coordinator
        self._attr_unique_id = self._coordinator.mac + self.name
        self._attr_should_poll = False
        self._attr_device_info = DeviceInfo(
            connections={(device_registry.CONNECTION_NETWORK_MAC, self._coordinator.mac)}
        )

    async def async_press(self: Self) -> None:
        """Handle button press to reset errors."""
        _LOGGER.info("Resetting errors on device %s.", self._coordinator.device_name)
        success = await self._coordinator.set_variable(VARIABLE_RESET_FLAG, 1)
        if not success:
            _LOGGER.warning("Failed to reset errors on device %s.", self._coordinator.device_name)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Setup of Helios Easy Controls button entities for the specified config_entry.

    Args:
        hass:
            The Home Assistant instance.
        config_entry:
            The config entry which is used to create button entities.
        async_add_entities:
            The callback which can be used to add new entities to Home Assistant.

    Returns:
        The value indicates whether the setup succeeded.

    """
    _LOGGER.info("Setting up Helios EasyControls button entities.")

    coordinator = get_coordinator(hass, config_entry.data[CONF_MAC])

    async_add_entities(
        [
            EasyControlsButton(
                coordinator,
                ButtonEntityDescription(
                    key="reset_errors",
                    name=f"{coordinator.device_name} reset errors",
                    icon="mdi:restart",
                    device_class=ButtonDeviceClass.RESTART,
                ),
            ),
        ]
    )

    _LOGGER.info("Setting up Helios EasyControls button entities completed.")
