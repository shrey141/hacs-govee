"""Govee API rate limit diagnostic sensor."""

from datetime import datetime
import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Govee diagnostic sensors."""
    hub = hass.data[DOMAIN]["hub"]
    async_add_entities(
        [GoveeApiRateLimitSensor(hub, entry.title)],
        update_before_add=False,
    )


class GoveeApiRateLimitSensor(SensorEntity):
    """Diagnostic sensor exposing Govee API rate limit information."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:speedometer"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, hub, title):
        """Initialize the rate limit sensor."""
        self._hub = hub
        self._title = title

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return f"govee_{self._title}_rate_limit"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Govee API Rate Limit"

    @property
    def native_value(self):
        """Return the remaining rate limit as the primary state."""
        remaining = self._hub.rate_limit_remaining
        if isinstance(remaining, str):
            return None
        return remaining

    @property
    def extra_state_attributes(self):
        """Return rate limit details as attributes."""
        attrs = {}

        total = self._hub.rate_limit_total
        if not isinstance(total, str):
            attrs["rate_limit_total"] = total

        remaining = self._hub.rate_limit_remaining
        if not isinstance(remaining, str):
            attrs["rate_limit_remaining"] = remaining

        reset_seconds = self._hub.rate_limit_reset_seconds
        if not isinstance(reset_seconds, str):
            attrs["rate_limit_reset_seconds"] = round(reset_seconds, 2)

        reset = self._hub.rate_limit_reset
        if not isinstance(reset, str):
            try:
                attrs["rate_limit_reset"] = datetime.fromtimestamp(
                    reset
                ).isoformat()
            except (OSError, ValueError, OverflowError):
                pass

        rate_limit_on = self._hub.rate_limit_on
        if not isinstance(rate_limit_on, str):
            attrs["rate_limit_on"] = rate_limit_on

        return attrs

    @property
    def device_info(self):
        """Return the device info to group with Govee."""
        return {
            "identifiers": {(DOMAIN, f"govee_{self._title}")},
            "name": "Govee API",
            "manufacturer": "Govee",
        }

    @property
    def entity_registry_enabled_default(self):
        """Disable by default — this is a diagnostic sensor."""
        return False
