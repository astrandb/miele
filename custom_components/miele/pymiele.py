"""Library for Miele API."""

# TODO
# Should be moved to pypi.org when reasonably stable
from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from json.decoder import JSONDecodeError
from typing import Any, Callable, Coroutine

import async_timeout
from aiohttp import ClientError, ClientResponse, ClientSession, ClientTimeout

from .const import MIELE_API

CONTENT_TYPE = "application/json"

_LOGGER = logging.getLogger(__name__)


class AbstractAuth(ABC):
    """Abstract class to make authenticated requests."""

    def __init__(self, websession: ClientSession, host: str):
        """Initialize the auth."""
        self.websession = websession
        self.host = host

    @abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid access token."""

    async def request(self, method, url, **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)
            kwargs.pop("headers")

        access_token = await self.async_get_access_token()
        headers["authorization"] = f"Bearer {access_token}"

        return await self.websession.request(
            method,
            f"{self.host}{url}",
            **kwargs,
            headers=headers,
        )

    async def set_target_temperature(
        self, serial: str, temperature: float, zone: int = 1
    ):
        """Set target temperature."""
        temp = round(temperature)
        async with async_timeout.timeout(10):
            data = {"targetTemperature": [{"zone": zone, "value": temp}]}
            res = await self.request(
                "PUT",
                f"/devices/{serial}/actions",
                data=json.dumps(data),
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Accept": "application/json",
                },
            )
        _LOGGER.debug("set_target res: %s", res.status)
        return res

    async def send_action(self, serial: str, data):
        """Send action command."""

        _LOGGER.debug("send_action serial: %s, data: %s", serial, data)
        async with async_timeout.timeout(10):
            res = await self.request(
                "PUT",
                f"/devices/{serial}/actions",
                data=json.dumps(data),
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Accept": "application/json",
                },
            )
            res.raise_for_status()
        _LOGGER.debug("send-action res: %s", res.status)
        return res

    async def listen_events(
        self,
        data_callback: Callable[[dict[str, Any]], Any] | None = None,
        actions_callback: Callable[[dict[str, Any]], Any] | None = None,
    ) -> Callable[[], Coroutine[Any, Any, None]]:
        """Listen to events, apply changes to object and call callback with event."""
        while True:
            try:
                access_token = await self.async_get_access_token()
                async with self.websession.get(
                    f"{MIELE_API}/devices/all/events",
                    timeout=ClientTimeout(total=None, sock_connect=5, sock_read=None),
                    headers={
                        "Accept": "text/event-stream; char-set=utf-8",
                        "Authorization": f"Bearer {access_token}",
                    },
                ) as resp:
                    # _LOGGER.debug("Response: %s", resp.status)
                    while True:
                        id_line = await resp.content.readline()
                        data_line = await resp.content.readline()
                        await resp.content.readline()  # Empty line
                        if resp.closed:
                            return
                        event_type = bytearray(id_line).decode().strip()
                        if event_type == "event: devices":
                            data = json.loads(data_line[6:])
                            if data_callback is not None:
                                asyncio.create_task(data_callback(data))
                        elif event_type == "event: actions":
                            data = json.loads(data_line[6:])
                            if actions_callback is not None:
                                asyncio.create_task(actions_callback(data))
                        elif event_type == "event: ping":
                            pass
                        else:
                            _LOGGER.error("Unknown event type: %s", event_type)

            except ClientError as ex:
                _LOGGER.error("SSE: %s - %s", ex.status, ex.message)
                await asyncio.sleep(5)
            except JSONDecodeError as ex:
                _LOGGER.error(
                    "JSON decode error: %s, Pos: %s, Doc: %s", ex.msg, ex.pos, ex.doc
                )
                await asyncio.sleep(5)
            except Exception as ex:
                _LOGGER.error("Listen_event: %s - %s", ex.status, ex.message)
                await asyncio.sleep(5)


class MieleException(Exception):
    """Generic miele exception."""


class MieleAuthException(MieleException):
    """Authentication failure."""
