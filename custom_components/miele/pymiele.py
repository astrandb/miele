"""Library for Miele API."""

# TODO
# Should be moved to pypi.org when reasonably stable

import json
import logging
from abc import ABC, abstractmethod

import async_timeout
from aiohttp import ClientResponse, ClientSession

CONTENT_TYPE = "application/json-patch+json"

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

    async def set_target_temperature(self, serial: str, temperature: int):
        """Set target temperature"""

        async with async_timeout.timeout(10):
            data = {"serialNumber": serial, "temperature": temperature}
            res = await self.request(
                "PUT",
                "/Mode/manual",
                data=json.dumps(data),
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Accept": "application/json",
                },
            )
        return res

    async def set_mode_auto(self, serial: str):
        """Set auto mode"""

        async with async_timeout.timeout(10):
            data = {"serialNumber": serial}
            res = await self.request(
                "PUT",
                "/Mode/auto",
                data=json.dumps(data),
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Accept": "application/json",
                },
            )
        return res

    async def set_mode_manual(self, serial: str):
        """Set heat/manual mode"""

        async with async_timeout.timeout(10):
            data = {"serialNumber": serial}
            res = await self.request(
                "PUT",
                "/Mode/manual",
                data=json.dumps(data),
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Accept": "application/json",
                },
            )
        return res

    async def set_mode_hold(self, serial: str, temperature: int, hold_until: str):
        """Set hold mode"""

        async with async_timeout.timeout(10):
            data = {
                "serialNumber": serial,
                "temperature": temperature,
                "holdUntil": hold_until,
            }
            res = await self.request(
                "PUT",
                "/Mode/hold",
                data=json.dumps(data),
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Accept": "application/json",
                },
            )
        return res

    async def set_mode_off(self, serial: str):
        """Set mode to off/standby."""
        """The API does not support off mode so we simulate it by setting temp to 5C."""

        async with async_timeout.timeout(10):
            data = {"serialNumber": serial, "temperature": 500}
            res = await self.request(
                "PUT",
                "/Mode/manual",
                data=json.dumps(data),
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Accept": "application/json",
                },
            )
        return res


class MieleException(Exception):
    """Generic miele exception."""


class MieleAuthException(MieleException):
    """Authentication failure."""
