"""The number module for Helios Easy Controls integration."""

from logging import getLogger

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from typing_extensions import Self

from custom_components.easycontrols import get_coordinator
from custom_components.easycontrols.const import (
    VARIABLE_BYPASS_EXTRACT_AIR_TEMPERATURE,
    VARIABLE_BYPASS_FROM_DAY,
    VARIABLE_BYPASS_FROM_MONTH,
    VARIABLE_BYPASS_OUTDOOR_AIR_TEMPERATURE,
    VARIABLE_BYPASS_TO_DAY,
    VARIABLE_BYPASS_TO_MONTH,
)
from custom_components.easycontrols.coordinator import EasyControlsDataUpdateCoordinator
from custom_components.easycontrols.modbus_variable import IntModbusVariable

_LOGGER = getLogger(__name__)


class EasyControlsNumberEntity(NumberEntity):
    """Represents a number entity which is attached to a IntModBusVariable"""

    def __init__(
        self: Self,
        coordinator: EasyControlsDataUpdateCoordinator,
        variable: IntModbusVariable,
        description: NumberEntityDescription,
    ):
        """
        Initialize a new instance of `EasyControlsNumberEntity` class.

        Args:
            coordinator: The coordinator instance.
            variable: The ModBus variable to get and set by the number entity.
            description: The entity description of the number.
        """
        super().__init__()
        self.entity_description = description
        self._coordinator = coordinator
        self._variable = variable
        self._attr_native_value = None
        self._attr_available = False
        self._attr_unique_id = self._coordinator.mac + description.name
        self._attr_should_poll = False
        self._attr_device_info = DeviceInfo(
            connections={(device_registry.CONNECTION_NETWORK_MAC, self._coordinator.mac)}
        )

        def update_listener(variable: IntModbusVariable, value: int) -> None:  # noqa: ARG001
            self._value_updated(value)

        self._update_listener = update_listener

    async def async_added_to_hass(self: Self) -> None:
        """Run when entity is added to Home Assistant."""
        self._coordinator.add_listener(self._variable, self._update_listener)
        return await super().async_added_to_hass()

    async def async_will_remove_from_hass(self: Self) -> None:
        """Run when entity will be removed from Home Assistant."""
        self._coordinator.remove_listener(self._variable, self._update_listener)
        return await super().async_will_remove_from_hass()

    def _value_updated(self: Self, value: int) -> None:
        """
        Handle value updates from the coordinator.

        Args:
            value: The new value from the ModBus variable.

        """
        self._attr_native_value = value
        self._attr_available = self._attr_native_value is not None
        self.schedule_update_ha_state(False)

    async def async_set_native_value(self, value: float) -> None:
        """
        Update the current value.

        Args:
            value: The new value to set (will be converted to int).

        """
        await self._coordinator.set_variable(self._variable, int(value))


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Setup of Helios Easy Controls numbers for the specified config_entry.

    Args:
        hass:
            The Home Assistant instance.
        config_entry:
            The config entry which is used to create number entities.
        async_add_entities:
            The callback which can be used to add new entities to Home Assistant.

    """
    _LOGGER.info("Setting up Helios EasyControls numbers.")

    coordinator = get_coordinator(hass, config_entry.data[CONF_MAC])

    async_add_entities(
        [
            EasyControlsNumberEntity(
                coordinator,
                VARIABLE_BYPASS_FROM_MONTH,
                NumberEntityDescription(
                    key="bypass_from_month",
                    name=f"{coordinator.device_name} bypass activated from month",
                    icon="mdi:calendar-month",
                    entity_category=EntityCategory.CONFIG,
                    native_min_value=1,
                    native_max_value=12,
                    native_step=1,
                ),
            ),
            EasyControlsNumberEntity(
                coordinator,
                VARIABLE_BYPASS_FROM_DAY,
                NumberEntityDescription(
                    key="bypass_from_day",
                    name=f"{coordinator.device_name} bypass activated from day",
                    icon="mdi:calendar-outline",
                    entity_category=EntityCategory.CONFIG,
                    native_min_value=1,
                    native_max_value=31,
                    native_step=1,
                ),
            ),
            EasyControlsNumberEntity(
                coordinator,
                VARIABLE_BYPASS_TO_MONTH,
                NumberEntityDescription(
                    key="bypass_to_month",
                    name=f"{coordinator.device_name} bypass activated to month",
                    icon="mdi:calendar-month",
                    entity_category=EntityCategory.CONFIG,
                    native_min_value=1,
                    native_max_value=12,
                    native_step=1,
                ),
            ),
            EasyControlsNumberEntity(
                coordinator,
                VARIABLE_BYPASS_TO_DAY,
                NumberEntityDescription(
                    key="bypass_to_day",
                    name=f"{coordinator.device_name} bypass activated to day",
                    icon="mdi:calendar-outline",
                    entity_category=EntityCategory.CONFIG,
                    native_min_value=1,
                    native_max_value=31,
                    native_step=1,
                ),
            ),
            EasyControlsNumberEntity(
                coordinator,
                VARIABLE_BYPASS_EXTRACT_AIR_TEMPERATURE,
                NumberEntityDescription(
                    key="bypass_extract_air_temperature",
                    name=f"{coordinator.device_name} bypass min. extract air temperature",
                    icon="mdi:thermometer",
                    device_class="temperature",
                    entity_category=EntityCategory.CONFIG,
                    native_min_value=10,
                    native_max_value=40,
                    native_step=1,
                    native_unit_of_measurement="°C",
                ),
            ),
            EasyControlsNumberEntity(
                coordinator,
                VARIABLE_BYPASS_OUTDOOR_AIR_TEMPERATURE,
                NumberEntityDescription(
                    key="bypass_outside_air_temperature",
                    name=f"{coordinator.device_name} bypass min. outside air temperature",
                    icon="mdi:thermometer",
                    device_class="temperature",
                    entity_category=EntityCategory.CONFIG,
                    native_min_value=5,
                    native_max_value=20,
                    native_step=1,
                    native_unit_of_measurement="°C",
                ),
            ),
        ]
    )

    _LOGGER.info("Setting up Helios EasyControls numbers completed.")
