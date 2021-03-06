"""Helpers for data entry flows for config entries."""
from functools import partial

from homeassistant import config_entries


def register_discovery_flow(domain, title, discovery_function,
                            connection_class):
    """Register flow for discovered integrations that not require auth."""
    config_entries.HANDLERS.register(domain)(
        partial(DiscoveryFlowHandler, domain, title, discovery_function,
                connection_class))


class DiscoveryFlowHandler(config_entries.ConfigFlow):
    """Handle a discovery config flow."""

    VERSION = 1

    def __init__(self, domain, title, discovery_function, connection_class):
        """Initialize the discovery config flow."""
        self._domain = domain
        self._title = title
        self._discovery_function = discovery_function
        self.CONNECTION_CLASS = connection_class  # pylint: disable=C0103

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(
                reason='single_instance_allowed'
            )

        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        """Confirm setup."""
        if user_input is None:
            return self.async_show_form(
                step_id='confirm',
            )

        if self.context and self.context.get('source') != \
                config_entries.SOURCE_DISCOVERY:
            # Get current discovered entries.
            in_progress = self._async_in_progress()

            has_devices = in_progress
            if not has_devices:
                has_devices = await self.hass.async_add_job(
                    self._discovery_function, self.hass)

            if not has_devices:
                return self.async_abort(
                    reason='no_devices_found'
                )

            # Cancel the discovered one.
            for flow in in_progress:
                self.hass.config_entries.flow.async_abort(flow['flow_id'])

        return self.async_create_entry(
            title=self._title,
            data={},
        )

    async def async_step_discovery(self, discovery_info):
        """Handle a flow initialized by discovery."""
        if self._async_in_progress() or self._async_current_entries():
            return self.async_abort(
                reason='single_instance_allowed'
            )

        return await self.async_step_confirm()

    async def async_step_import(self, _):
        """Handle a flow initialized by import."""
        if self._async_in_progress() or self._async_current_entries():
            return self.async_abort(
                reason='single_instance_allowed'
            )

        return self.async_create_entry(
            title=self._title,
            data={},
        )
