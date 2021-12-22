"""Config flow for Miele."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components import persistent_notification
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle Miele OAuth2 authentication."""

    DOMAIN = DOMAIN

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    @property
    def extra_authorize_data(self) -> dict:
        """Extra data that needs to be appended to the authorize url."""
        return {
            "vg": "sv_SE",
        }

    async def async_step_reauth(
        self, entry: dict[str, Any] | None = None
    ) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        persistent_notification.async_create(
            self.hass,
            f"Miele integration for account {entry['id']} needs to be re-authenticated. Please go to the integrations page to re-configure it.",
            "Miele re-authentication",
            "miele_reauth",
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                description_placeholders={"account": self.entry["id"]},
                data_schema=vol.Schema({}),
                errors={},
            )

        persistent_notification.async_dismiss(self.hass, "miele_reauth")
        return await self.async_step_user()
