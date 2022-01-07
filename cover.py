"""Cover platform for Start2Smart integration."""

from homeassistant.helpers import update_coordinator

from homeassistant.components.cover import (
    ATTR_POSITION,
    DEVICE_CLASS_BLIND,
    SUPPORT_CLOSE,
    SUPPORT_STOP,
    SUPPORT_OPEN,
    SUPPORT_SET_POSITION,
    CoverEntity,
)

from .const import (

    DOMAIN as START2SMART_DOMAIN,
    START2SMART_BLIND_STATE_OPEN,
    START2SMART_BLIND_STATE_CLOSE
)

PARALLEL_UPDATES = 0


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up AdvantageAir cover platform."""

    coordinator = hass.data[START2SMART_DOMAIN][config_entry.entry_id]

    entities = []
    for device in coordinator.data["devices"]:
        entities.append(Start2SmartCover(coordinator, device))
    async_add_entities(entities)


class Start2SmartCover(update_coordinator.CoordinatorEntity, CoverEntity):
    """Start2Smart Cover Class."""

    _attr_device_class = DEVICE_CLASS_BLIND
    _attr_supported_features = SUPPORT_OPEN | SUPPORT_STOP |SUPPORT_CLOSE | SUPPORT_SET_POSITION

    def __init__(self, coordinator, device):
        """Initialize an Advantage Air Cover Class."""
        super().__init__(coordinator)
        self._attr_name = f'{device["name"]}'
        self._attr_unique_id = (
            f'{device["deviceNumber"]}-{device["uid"]}'
        )
        self._attr_device_info = {
            "identifiers": {(START2SMART_DOMAIN, device["uid"])},
            "name": device["name"],
            "manufacturer": "Rademacher",
            "model": "Rollotron",
        }
        self._device = device
        self.command = None

    @property
    def is_closed(self):
        """Return if blind is fully closed."""
        return self._device["statusesMap"]["Position"] == START2SMART_BLIND_STATE_CLOSE
    

    @property
    def current_cover_position(self):
        """Return blind current position as a percentage."""
        return 100 - self._device["statusesMap"]["Position"]

    async def async_open_cover(self, **kwargs):
        """Fully open zone vent."""
        
        await self.coordinator._async_send_data(
            {

                    "device": self._device,
                    "command": {"name":"POS_UP_CMD"}
                
                
            }
        )

    async def async_close_cover(self, **kwargs):
        """Fully close zone vent."""
        await self.coordinator._async_send_data(
            {

                    "device": self._device,
                    "command": {"name":"POS_DOWN_CMD"}
                
                
            }
        )

    async def async_stop_cover(self, **kwargs):
        """Fully close zone vent."""
        await self.coordinator._async_send_data(
            {

                    "device": self._device,
                    "command": {"name":"STOP_CMD"}
                
                
            }
        )

    async def async_set_cover_position(self, **kwargs):
        """Change vent position."""
        position = round(kwargs[ATTR_POSITION] / 5) * 5
        if position == 0:
            await self.coordinator._async_send_data(
            {

                    "device": self._device,
                    "command": {"name":"POS_DOWN_CMD"}
                
            }
        )

        elif position == 100:
            await self.coordinator._async_send_data(
            {

                    "device": self._device,
                    "command": {"name":"POS_UP_CMD"}
                
            }
        )
        else:
            await self.coordinator._async_send_data(
            {

                    "device": self._device,
                    "command": {"name":"GOTO_POS_CMD", "value": position}
                
            }
        )
