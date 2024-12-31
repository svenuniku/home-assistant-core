"""Config flow to configure the Open ERZ integration."""

from __future__ import annotations

import logging
from typing import Any

from openerz_api.main import OpenERZParameters
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import aiohttp_client, config_validation as cv
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelectorMode,
    selector,
)

from .const import (
    CONF_WASTE_AREA,
    CONF_WASTE_REGION,
    CONF_WASTE_TYPES,
    DEFAULT_NAME,
    DOMAIN,
)
from .types import SENSOR_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)


def to_camel_case(text: str | None):
    """String to Camel case for areas/regions."""

    replace_map = {"-": " ", "_": " ", "ae": "ä", "ue": "ü", "oe": "ö"}
    if not isinstance(text, str):
        return text
    for search, replace in replace_map.items():
        text = text.replace(search, replace)
    if text == "stgallen":
        text.replace("st", "st. ")
    s = text.split()
    return " ".join(i.capitalize() for i in s)


class OpenERZConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Open ERZ."""

    VERSION = 1

    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    data: dict[str, Any]

    async def _async_query(self, step_id: str) -> list[str]:
        websession = aiohttp_client.async_get_clientsession(self.hass)
        match step_id:
            case "user":
                # get all regions to select from
                return await OpenERZParameters(websession).get_regions()
            case "area":
                return await OpenERZParameters(websession).get_areas(
                    self.data[CONF_WASTE_REGION]
                )
            case "types":
                return await OpenERZParameters(websession).get_types(
                    self.data[CONF_WASTE_REGION]
                )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial user invoked step."""
        # Invoked when a user initiates a flow via the user interface.
        placeholders = {
            "name": DEFAULT_NAME,
        }
        self.context["title_placeholders"] = placeholders
        errors: dict[str, str] = {}
        if user_input is not None:
            _LOGGER.warning(f"user_input: {user_input}.")
            # Set valid data
            self.data = user_input
            # self.data[CONF_WASTE_REGION] = user_input[CONF_WASTE_REGION]
            # Return the form of the next step.
            return await self.async_step_area()

        try:
            options = await self._async_query(step_id="user")
        except ValueError:
            errors = {"base": "unknown"}

        options: list[SelectOptionDict] = [
            SelectOptionDict(label=to_camel_case(o), value=o) for o in options
        ]
        # Build schema
        schema = vol.Schema(
            {
                vol.Required(CONF_WASTE_REGION): selector(
                    {
                        "select": {
                            "options": options,
                            "multiple": False,
                            "mode": SelectSelectorMode.DROPDOWN,
                            # "translation_key": ,
                            "sort": True,
                        }
                    }
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_area(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the second step selecting the area."""

        placeholders = {
            "name": DEFAULT_NAME,
            "region": to_camel_case(self.data[CONF_WASTE_REGION]),
        }
        self.context["title_placeholders"] = placeholders
        errors: dict[str, str] = {}
        if user_input is not None:
            _LOGGER.warning(f"user_input: {user_input}.")
            # Set valid data
            self.data.update(user_input)
            # Return the form of the next step.
            return await self.async_step_types()

        try:
            options = await self._async_query(step_id="area")
        except ValueError:
            errors = {"base": "unknown"}
        if len(options) == 0:
            # skip this step
            self.data[CONF_WASTE_AREA] = None
            return await self.async_step_types()

        options: list[SelectOptionDict] = [
            SelectOptionDict(label=to_camel_case(o), value=o) for o in options
        ]
        # Build schema
        schema = vol.Schema(
            {
                vol.Required(CONF_WASTE_AREA): selector(
                    {
                        "select": {
                            "options": options,
                            "multiple": False,
                            "mode": SelectSelectorMode.DROPDOWN,
                            # "translation_key": ,
                            "sort": True,
                        }
                    }
                )
            }
        )
        return self.async_show_form(step_id="area", data_schema=schema, errors=errors)

    async def async_step_types(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the third step selecting the waste types."""
        errors: dict[str, str] = {}

        placeholders = {
            "name": DEFAULT_NAME,
            "region": to_camel_case(self.data[CONF_WASTE_REGION]),
            "area": to_camel_case(self.data[CONF_WASTE_AREA]),
        }
        self.context["title_placeholders"] = placeholders

        if user_input is not None:
            _LOGGER.warning(f"user_input: {user_input}.")
            waste_list = user_input.get(CONF_WASTE_TYPES, [])
            if len(waste_list) == 0:
                errors = {"base": "Please select at least one waste type."}
            else:
                # Add all enabled waste types
                self.data[CONF_WASTE_TYPES] = waste_list
                # User is done, create the config entry.
                return self.async_create_entry(
                    title=self.data[CONF_NAME],
                    data=self.data,
                )
        else:
            # create unique id
            unique_list = list(
                filter(
                    None,
                    [
                        self.data[CONF_WASTE_REGION],
                        self.data[CONF_WASTE_AREA],
                    ],
                )
            )
            unique_id = "-".join(unique_list).lower()
            # check if unique id is already in use
            entry = await self.async_set_unique_id(unique_id)
            if entry is not None:
                _LOGGER.debug(
                    "An entry with the unique_id %s already exists: %s",
                    unique_id,
                    entry.data,
                )
                self._abort_if_unique_id_configured()
            self.data[CONF_NAME] = " ".join([to_camel_case(a) for a in unique_list])
        # get wastetypes
        try:
            options = await self._async_query(step_id="types")
        except ValueError:
            errors = {"base": "unknown"}

        # translation would be preferred...
        options: list[SelectOptionDict] = [
            SelectOptionDict(label=to_camel_case(o), value=o) for o in options
        ]
        # Build schema
        schema = vol.Schema(
            {
                vol.Required(CONF_WASTE_TYPES): selector(
                    {
                        "select": {
                            "options": options,
                            "multiple": True,
                            "mode": SelectSelectorMode.LIST,
                            # "translation_key": ,
                            "sort": True,
                        }
                    }
                )
            }
        )
        return self.async_show_form(step_id="types", data_schema=schema, errors=errors)
