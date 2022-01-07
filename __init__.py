"""The Rademacher start2smart integration."""
from datetime import timedelta
import logging
import requests
import json

from urllib.parse import ParseResult, urlparse

from requests.exceptions import HTTPError, Timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import update_coordinator
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["cover"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry for start2smart."""
    coordinator = SmartBridgeData(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class SmartBridgeData(update_coordinator.DataUpdateCoordinator):
    """Get and update the latest data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the data object."""
        super().__init__(
            hass, _LOGGER, name="Start2Smart", update_interval=timedelta(seconds=60)
        )

        host_entry = entry.data[CONF_HOST]
        url = f"{host_entry}/v4/devices?devtype=Actuator"
        url = urlparse(url, "http")
        netloc = url.netloc or url.path
        path = url.path
        #url = ParseResult("http", netloc, path, *url[3:])
        self.unique_id = entry.entry_id
        self.name = entry.title
        self.host = url.geturl()
        self._request = requests.Request("GET", self.host).prepare()

    async def _async_update_data(self):
        """Update the data from the Start2Smart Bridge."""

        try:
            with requests.Session() as sess:

                data = await self.hass.async_add_executor_job(sess.send, self._request)
                json_data = json.loads(data.text)

        except (OSError, Timeout, HTTPError, json.JSONDecodeError) as err:
            raise update_coordinator.UpdateFailed(err)

        _LOGGER.debug(
            "Connection to Start2Smart Bridge successful. Retrieving latest update from %s",
            data.url,
        )

        return json_data

    async def _async_send_data(self, data):
        """Send the data to the start2smart bride."""
 

        host_entry = self.config_entry.data[CONF_HOST]
        url = f"{host_entry}/devices/{data['device']['did']}"
        

        data = json.dumps(data["command"])
        request = requests.Request("PUT", url, data=data).prepare()
        request.headers["Content-Type"] = "text/plain"

        try:
            with requests.Session() as sess:

                data = await self.hass.async_add_executor_job(sess.send, request)
                await SmartBridgeData.async_config_entry_first_refresh(self)
            

        except (OSError, Timeout, HTTPError) as err:
            raise update_coordinator.UpdateFailed(err)

        _LOGGER.info(
            "Connection to start2smart bridge successful. Sending command to %s",
            data.url,
        )