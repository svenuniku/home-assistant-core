"""Support for OpenERZ API for Zurich city waste disposal system."""

from __future__ import annotations

import datetime
import logging

from openerz_api.main import OpenERZConnector
import voluptuous as vol

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    PLATFORM_SCHEMA as SENSOR_PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    aiohttp_client,
    config_validation as cv,
    entity_registry as er,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .types import SENSOR_DESCRIPTIONS

from .const import (
    CONF_WASTE_AREA,
    CONF_WASTE_REGION,
    CONF_WASTE_TYPES,
    DEFAULT_NAME,
    DOMAIN,
)

SCAN_INTERVAL = datetime.timedelta(hours=12)

WASTE_SCHEMA = vol.Schema(
    {vol.Required(CONF_WASTE_TYPES): cv.string, vol.Optional(CONF_NAME): cv.string}
)

PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_WASTE_REGION): cv.string,
        vol.Required(CONF_WASTE_AREA, default=None): cv.string,
        vol.Required(CONF_WASTE_TYPES): vol.All(cv.ensure_list, [WASTE_SCHEMA]),
    }
)

_LOGGER = logging.getLogger(__name__)


# This function is called as part of the __init__.async_setup_entry (via the
# hass.config_entries.async_forward_entry_setup call)
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up entity configured via user interface.

    Called via async_forward_entry_setups(, SENSOR) from __init__.py
    """
    config = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.warning(
        f"setup sensor entity: {config_entry} -> {config.get(CONF_WASTE_TYPES)}"
    )
    device = DeviceOpenERZ(
        hass=hass,
        name=config.get(CONF_NAME),
        entity_id=config_entry.entry_id,
        unique_id=f"{config_entry.unique_id}",
        region=config.get(CONF_WASTE_REGION),
        area=config.get(CONF_WASTE_AREA),
        waste_types=config.get(CONF_WASTE_TYPES),
    )

    sensors: list[OpenERZSensor] = [
        OpenERZSensor(device=device, description=SENSOR_DESCRIPTIONS[waste])
        for waste in config.get(CONF_WASTE_TYPES)
    ]
    if sensors:
        async_add_entities(
            sensors,
            update_before_add=True,
        )


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    _LOGGER.warning(f"setup sensor platform: {config}")
    # Single instance of api connector
    api_connector = OpenERZConnector(
        config.get(CONF_WASTE_REGION),
        config.get(CONF_WASTE_AREA),
        config.get(CONF_WASTE_TYPES),
    )
    sensors = [
        OpenERZSensor(api_connector, waste, config.unique_id)
        for waste in config.get(CONF_WASTE_TYPES)
    ]
    async_add_entities(
        sensors,
        update_before_add=True,
    )


class OpenERZSensor(SensorEntity):
    """Representation of a Sensor."""

    # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
    device_class = SensorDeviceClass.DATE

    def __init__(
        self,
        device: DeviceOpenERZ,
        description: SensorEntityDescription,
        is_config_entry: bool = True,
    ) -> None:
        """Initialize the sensor."""

        self._device = device
        self._state = None
        self._waste_type = description.key

        self._attr_has_entity_name = True
        self._attr_name = description.key
        self._attr_unique_id = f"{self._device.unique_id}_{description.key}".lower()
        self._attr_attribution = "Attribution xyz"
        self._attr_device_info = self._device.device_info
        self.entity_description = description
        # self._attr_extra_state_attributes = {}

    @property
    def native_value(self) -> datetime:
        """Return the state of the sensor as datetime.date."""
        return self._state

    # @property
    # def unique_id(self) -> str:
    #    """Return unique id."""
    #    # All entities must have a unique id.  Think carefully what you want this to be as
    #    # changing it later will cause HA to create new entities.
    #    return self._unique_id

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        attrs = {}
        attrs["extra_info"] = "Extra Info"
        return attrs

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        result = await self._device.sensor_value(self._waste_type)
        _LOGGER.warning(f"update {self._attr_unique_id}: {self._attr_name} -> {result}")
        if result is None:
            self._state = None
        else:
            self._state = datetime.date.fromisoformat(result["date"])
            # ToDo: set extra args for "station", "description" if not empty.


class DeviceOpenERZ:
    """Representation of a OpenERZ Sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        entity_id: str,
        unique_id: str,
        region: str,
        area: str | None,
        waste_types: list[str],
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._region = region
        self._area = area
        self._waste_types = waste_types

        self._unique_id = unique_id
        self._entity_id_prefix = unique_id
        # registry = er.async_get(self.hass)
        # registry.async_update_entity(entity_id, new_entity_id=unique_id)
        self._device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=name,
            manufacturer=DEFAULT_NAME,
            # model="Virtual Device",
        )
        self.extra_state_attributes = {}
        self.sensors = []

        websession = aiohttp_client.async_get_clientsession(self.hass)
        self.api_connector = OpenERZConnector(
            self._region, self._area, self._waste_types, websession
        )

    # @property
    # def compute_states(self) -> dict[SensorType, ComputeState]:
    #    """Compute states of configured sensors."""
    #    return self._compute_states

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_info(self) -> dict:
        """Return the device info."""
        return self._device_info

    @property
    def name(self) -> str:
        """Return the name."""
        return self._device_info["name"]

    async def sensor_value(self, waste_type: str) -> dict[str, str]:
        """Get state value for waste type."""
        x = await self.api_connector.find_next_pickup(waste_type, day_offset=31)
        _LOGGER.warning(f"update results in : {x}")
        return x
