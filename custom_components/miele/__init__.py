"""The Miele integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from http import HTTPStatus

import async_timeout
import flatdict
import voluptuous as vol
from aiohttp import ClientResponseError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.config_entry_oauth2_flow import LocalOAuth2Implementation
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    DataUpdateCoordinator,
)

from . import config_flow
from .api import AsyncConfigEntryAuth
from .const import DOMAIN, OAUTH2_AUTHORIZE, OAUTH2_TOKEN
from .devcap import TEST_DATA_7, TEST_DATA_24
from .services import async_setup_services

# from .pymiele import MieleAuthException

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID): cv.string,
                vol.Required(CONF_CLIENT_SECRET): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = ["sensor", "binary_sensor", "climate", "switch"]


class MieleLocalOAuth2Implementation(LocalOAuth2Implementation):
    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        client_id: str,
        client_secret: str,
        authorize_url: str,
        token_url: str,
        name: str,
    ) -> None:
        super().__init__(
            hass, domain, client_id, client_secret, authorize_url, token_url
        )
        self._name = name

    @property
    def name(self) -> str:
        """Name of the implementation"""
        return self._name


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Miele component."""
    hass.data[DOMAIN] = {}

    if DOMAIN not in config:
        return True

    config_flow.OAuth2FlowHandler.async_register_implementation(
        hass,
        # config_entry_oauth2_flow.LocalOAuth2Implementation(
        MieleLocalOAuth2Implementation(
            hass,
            DOMAIN,
            config[DOMAIN][CONF_CLIENT_ID],
            config[DOMAIN][CONF_CLIENT_SECRET],
            OAUTH2_AUTHORIZE,
            OAUTH2_TOKEN,
            "Miele",
        ),
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Miele from a config entry."""
    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )

    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)
    try:
        await session.async_ensure_token_valid()
    except ClientResponseError as ex:
        _LOGGER.debug("API error: %s (%s)", ex.code, ex.message)
        if ex.code in (
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.UNAUTHORIZED,
            HTTPStatus.FORBIDDEN,
        ):
            raise ConfigEntryAuthFailed("Token not valid, trigger renewal") from ex
        raise ConfigEntryNotReady from ex

    hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN]["id_log"] = []
    hass.data[DOMAIN][entry.entry_id]["listener"] = None
    hass.data[DOMAIN][entry.entry_id]["api"] = AsyncConfigEntryAuth(
        aiohttp_client.async_get_clientsession(hass), session
    )

    coordinator = await get_coordinator(hass, entry)
    if not coordinator.last_update_success:
        await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("First data - flat: %s", coordinator.data)

    async def _callback_update_data(data) -> None:
        # _LOGGER.debug("Callback data: %s", data)
        # data["1223007"] = TEST_DATA_7
        # data["1223024"] = TEST_DATA_24
        flat_result: dict = {}
        for idx, ent in enumerate(data):
            flat_result[ent] = dict(flatdict.FlatterDict(data[ent], delimiter="|"))
        coordinator.async_set_updated_data(flat_result)

    async def _callback_update_actions(data) -> None:
        hass.data[DOMAIN][entry.entry_id]["actions"] = data

    hass.data[DOMAIN][entry.entry_id]["listener"] = asyncio.create_task(
        hass.data[DOMAIN][entry.entry_id]["api"].listen_events(
            data_callback=_callback_update_data,
            actions_callback=_callback_update_actions,
        )
    )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    await async_setup_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN][entry.entry_id]["listener"].cancel()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def get_coordinator(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> DataUpdateCoordinator:
    """Get the data update coordinator."""
    if "coordinator" in hass.data[DOMAIN][entry.entry_id]:
        return hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async def async_fetch():
        miele_api = hass.data[DOMAIN][entry.entry_id]["api"]
        async with async_timeout.timeout(10):
            res = await miele_api.request("GET", "/devices")
            # _LOGGER.debug("Data: %s", await res.json())
        if res.status == 401:
            # raise MieleAuthException("Authentication failure when fetching data")
            raise ConfigEntryAuthFailed("Authentication failure when fetching data")
        result = await res.json()
        flat_result: dict = {}
        # result["1223007"] = TEST_DATA_7
        # result["1223024"] = TEST_DATA_24

        for idx, ent in enumerate(result):
            flat_result[ent] = dict(flatdict.FlatterDict(result[ent], delimiter="|"))
        # _LOGGER.debug("Data: %s", flat_result)
        return flat_result

    hass.data[DOMAIN][entry.entry_id]["coordinator"] = DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_method=async_fetch,
        update_interval=timedelta(seconds=60),
    )
    await hass.data[DOMAIN][entry.entry_id]["coordinator"].async_refresh()
    return hass.data[DOMAIN][entry.entry_id]["coordinator"]
