"""Config flow for Miele."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import persistent_notification
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow
import voluptuous as vol

from .const import DOMAIN


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle Miele OAuth2 authentication."""

    DOMAIN = DOMAIN

    entry = None

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
        self.entry = entry
        persistent_notification.async_create(
            self.hass,
            (
                f"Miele integration for account {entry['auth_implementation']} needs to ",
                "be re-authenticated. Please go to the integrations page to re-configure it.",
            ),
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
                description_placeholders={"account": self.entry["auth_implementation"]},
                data_schema=vol.Schema({}),
                errors={},
            )

        persistent_notification.async_dismiss(self.hass, "miele_reauth")
        return await self.async_step_user()

    async def async_oauth_create_entry(self, data: dict) -> FlowResult:
        """Create an oauth config entry or update existing entry for reauth."""
        existing_entry = await self.async_set_unique_id(DOMAIN)
        if existing_entry:
            self.hass.config_entries.async_update_entry(existing_entry, data=data)
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")
        return await super().async_oauth_create_entry(data)
