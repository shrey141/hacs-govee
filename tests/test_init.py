"""Tests for the Govee integration init."""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest


class TestSetup:
    """Tests for async_setup (Bug 5)."""

    @pytest.mark.asyncio
    async def test_async_setup_no_spurious_state(self):
        """Verify async_setup doesn't create a govee.state entity."""
        from custom_components.govee import async_setup

        hass = MagicMock()
        hass.data = {}
        result = await async_setup(hass, {})
        assert result is True
        # Should NOT call async_set on states
        hass.states.async_set.assert_not_called()


class TestUnloadEntry:
    """Tests for async_unload_entry (Bug 4)."""

    @pytest.mark.asyncio
    async def test_unload_awaits_coroutine(self):
        """Verify _unload_component_entry awaits the async call."""
        from custom_components.govee import _unload_component_entry

        hass = MagicMock()
        entry = MagicMock()
        hass.config_entries.async_forward_entry_unload = AsyncMock(return_value=True)

        result = await _unload_component_entry(hass, entry, "light")
        assert result is True
        hass.config_entries.async_forward_entry_unload.assert_awaited_once_with(
            entry, "light"
        )

    @pytest.mark.asyncio
    async def test_unload_handles_value_error(self):
        """Verify _unload_component_entry handles ValueError gracefully."""
        from custom_components.govee import _unload_component_entry

        hass = MagicMock()
        entry = MagicMock()
        hass.config_entries.async_forward_entry_unload = AsyncMock(
            side_effect=ValueError("Config entry was never loaded!")
        )

        result = await _unload_component_entry(hass, entry, "light")
        assert result is False

    @pytest.mark.asyncio
    async def test_unload_handles_generic_exception(self):
        """Verify _unload_component_entry handles generic exceptions gracefully."""
        from custom_components.govee import _unload_component_entry

        hass = MagicMock()
        entry = MagicMock()
        hass.config_entries.async_forward_entry_unload = AsyncMock(
            side_effect=RuntimeError("unexpected")
        )

        result = await _unload_component_entry(hass, entry, "light")
        assert result is False


class TestPlatforms:
    """Test that platforms list includes sensor."""

    def test_platforms_includes_sensor(self):
        from custom_components.govee import PLATFORMS

        assert "light" in PLATFORMS
        assert "sensor" in PLATFORMS
