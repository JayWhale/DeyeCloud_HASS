"""Config flow for Deye Cloud integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .api import DeyeCloudAuthError, DeyeCloudClient
from .const import (
    CONF_APP_ID,
    CONF_APP_SECRET,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class DeyeCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Deye Cloud."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Test the credentials
                client = DeyeCloudClient(
                    app_id=user_input[CONF_APP_ID],
                    app_secret=user_input[CONF_APP_SECRET],
                )
                
                if await client.test_connection():
                    await client.close()
                    
                    # Create a unique ID based on app_id
                    await self.async_set_unique_id(user_input[CONF_APP_ID])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title="Deye Cloud",
                        data={
                            CONF_APP_ID: user_input[CONF_APP_ID],
                            CONF_APP_SECRET: user_input[CONF_APP_SECRET],
                        },
                        options={
                            CONF_SCAN_INTERVAL: user_input.get(
                                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                            ),
                        },
                    )
                else:
                    errors["base"] = "cannot_connect"
                    
                await client.close()

            except DeyeCloudAuthError:
                errors["base"] = "invalid_auth"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_APP_ID): str,
                vol.Required(CONF_APP_SECRET): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "app_id_help": "Get your App ID from https://developer.deyecloud.com/app",
                "app_secret_help": "Get your App Secret from https://developer.deyecloud.com/app",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "DeyeCloudOptionsFlow":
        """Get the options flow for this handler."""
        return DeyeCloudOptionsFlow(config_entry)


class DeyeCloudOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Deye Cloud."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
                }
            ),
        )


async def validate_input(app_id: str, app_secret: str) -> bool:
    """Validate the user input allows us to connect."""
    client = DeyeCloudClient(app_id=app_id, app_secret=app_secret)
    result = await client.test_connection()
    await client.close()
    return result
