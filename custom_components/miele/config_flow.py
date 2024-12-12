"""Config flow for Miele."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components import persistent_notification, zeroconf
from homeassistant.config_entries import (
    SOURCE_REAUTH,
    SOURCE_RECONFIGURE,
    ConfigFlowResult,
)
from homeassistant.const import CONF_NAME
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle Miele OAuth2 authentication."""

    DOMAIN = DOMAIN

    name = None

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    @property
    def extra_authorize_data(self) -> dict:
        """Extra data that needs to be appended to the authorize url."""
        return {
            "vg": "sv-SE",
        }

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""
        persistent_notification.async_create(
            self.hass,
            (
                f"Miele integration for account {entry_data['auth_implementation']} needs to ",
                "be re-authenticated. Please go to the integrations page to re-configure it.",
            ),
            "Miele re-authentication",
            "miele_reauth",
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                description_placeholders={
                    "account": self._get_reauth_entry().data["auth_implementation"]
                },
                data_schema=vol.Schema({}),
                errors={},
            )

        persistent_notification.async_dismiss(self.hass, "miele_reauth")
        return await self.async_step_user()

    async def async_step_reconfigure(
        self, user_input: Mapping[str, Any] | None = None
    ) -> ConfigFlowResult:
        """User initiated reconfiguration."""
        return await self.async_step_user()

    async def async_oauth_create_entry(self, data: dict) -> ConfigFlowResult:
        """Create an oauth config entry or update existing entry for reauth."""
        await self.async_set_unique_id(DOMAIN)

        if self.source == SOURCE_REAUTH:
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                self._get_reauth_entry(), data_updates=data
            )
        if self.source == SOURCE_RECONFIGURE:
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(), data_updates=data
            )

        self._abort_if_unique_id_configured()
        return await super().async_oauth_create_entry(data)

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Prepare configuration for a Zeroconf discovered Miele device."""
        self.name = discovery_info.name.split(".", 1)[0]
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by zeroconf."""

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            try:
                return await self.async_step_user()
            except Exception:  # pylint: disable=broad-exception-caught]
                # Device became network unreachable after discovery.
                # Abort and let discovery find it again later.
                return self.async_abort(reason="cannot_connect")
        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={CONF_NAME: self.name},
        )
